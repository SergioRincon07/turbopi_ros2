#!/usr/bin/python3
# coding=utf8
import os
import sys
import math  # Necesario para cálculos trigonométricos (sin, cos, atan) y constantes (pi)
import time
import threading
# Añade dinámicamente la carpeta raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import HiwonderSDK.Board as Board  # Módulo de hardware que controla los motores físicos

class MecanumChassis:
    """
    Clase para controlar un chassis con ruedas mecanum.
    
    Las ruedas mecanum tienen rodillos a 45° que permiten movimiento omnidireccional:
    - Puede moverse en cualquier dirección (adelante, atrás, diagonal, lateral)
    - Puede rotar sobre su propio eje mientras se mueve
    - No necesita girar primero para cambiar de dirección
    """
    # A = 67  # mm - Distancia del centro a la rueda (eje X)
    # B = 59  # mm - Distancia del centro a la rueda (eje Y)
    # WHEEL_DIAMETER = 65  # mm - Diámetro de las ruedas

    def __init__(self, a=67, b=59, wheel_diameter=65):
        """
        Inicializa el chassis con sus dimensiones físicas.
        
        :param a: Distancia horizontal del centro del robot a las ruedas (mm)
        :param b: Distancia vertical del centro del robot a las ruedas (mm)
        :param wheel_diameter: Diámetro de las ruedas en milímetros
        
        Estas dimensiones se usan para calcular cómo distribuir la velocidad
        entre las 4 ruedas cuando el robot rota.
        """
        self.a = a
        self.b = b
        self.wheel_diameter = wheel_diameter
        # Variables de estado: guardan la última velocidad comandada
        self.velocity = 0        # Velocidad lineal (mm/s)
        self.direction = 0       # Dirección de movimiento (0-360°)
        self.angular_rate = 0    # Velocidad de rotación (rad/s o similar)

    def reset_motors(self):
        """
        Detiene todos los motores y resetea el estado del chassis.
        
        Se usa al iniciar o cuando se necesita parar el robot completamente.
        Itera por los 4 motores (1, 2, 3, 4) y los pone a velocidad 0.
        """
        for i in range(1, 5):
            Board.setMotor(i, 0)  # Envía comando al hardware para detener cada motor
            
        # Resetea las variables de estado interno
        self.velocity = 0
        self.direction = 0
        self.angular_rate = 0

    def set_velocity(self, velocity, direction, angular_rate, fake=False):
        """
        FUNCIÓN PRINCIPAL: Controla el movimiento del chassis usando coordenadas polares.
        
        Disposición de los motores en el robot:
        motor1 v1 (A)   |  ↑  | v2 motor2 (B)
                        |     |
        motor3 v3 (B)   |     | v4 motor4 (A)
        
        :param velocity: Velocidad de traslación en mm/s (qué tan rápido se mueve)
        :param direction: Dirección de movimiento en grados (0-360°)
                         - 0°: Derecha pura
                         - 90°: Adelante
                         - 180°: Izquierda  
                         - 270°: Atrás
                         - Valores intermedios: Movimientos diagonales
        :param angular_rate: Velocidad de rotación sobre su propio eje
                            - Positivo: gira en sentido horario mientras se mueve
                            - Negativo: gira en sentido antihorario
                            - 0: No rota, solo se traslada
        :param fake: Si es True, calcula pero no envía comandos (para testing)
        :return: None
        
        ALGORITMO CLAVE:
        1. Convierte la velocidad polar (magnitud + ángulo) a cartesiana (vx, vy)
        2. Calcula la contribución de rotación (vp)
        3. Combina traslación + rotación para cada rueda según la cinemática mecanum
        """
        # Constante para convertir grados a radianes (necesaria para sin/cos)
        rad_per_deg = math.pi / 180
        
        # PASO 1: Convertir de polar a cartesiano
        # vx: componente de velocidad en eje X (izquierda-derecha)
        # vy: componente de velocidad en eje Y (adelante-atrás)
        vx = velocity * math.cos(direction * rad_per_deg)
        vy = velocity * math.sin(direction * rad_per_deg)
        
        # PASO 2: Calcular la velocidad de rotación
        # vp: velocidad tangencial en las ruedas debido a la rotación
        # Se multiplica por (a+b) porque es la distancia del centro a las ruedas
        # El signo negativo ajusta la convención de rotación
        vp = -angular_rate * (self.a + self.b)
        
        # PASO 3: CINEMÁTICA INVERSA para ruedas mecanum
        # Cada rueda tiene una combinación específica de vx, vy y vp
        # Estas fórmulas provienen de la geometría de las ruedas mecanum a 45°
        
        # Motor 1 (frontal izquierdo): suma Y, suma X, resta rotación
        v1 = int(vy + vx - vp) 
        # Motor 2 (frontal derecho): suma Y, resta X, suma rotación
        v2 = int(vy - vx + vp)
        # Motor 3 (trasero izquierdo): suma Y, resta X, resta rotación
        v3 = int(vy - vx - vp)
        # Motor 4 (trasero derecho): suma Y, suma X, suma rotación
        v4 = int(vy + vx + vp)
        
        # Si es modo "fake", solo calcula pero no ejecuta (útil para debugging)
        if fake:
            return
        
        # PASO 4: Enviar velocidades a los motores físicos
        Board.setMotor(1, v1)
        Board.setMotor(2, v2)
        Board.setMotor(3, v3)
        Board.setMotor(4, v4)
        
        # Guardar el estado actual
        self.velocity = velocity
        self.direction = direction
        self.angular_rate = angular_rate

    def translation(self, velocity_x, velocity_y, fake=False):
        """
        FUNCIÓN ALTERNATIVA: Controla el movimiento usando coordenadas cartesianas.
        
        En lugar de dar velocidad + ángulo (polar), puedes dar velocidad en X e Y.
        Esta función convierte automáticamente cartesiano → polar y llama a set_velocity().
        
        :param velocity_x: Velocidad en eje X (mm/s) - positivo=derecha, negativo=izquierda
        :param velocity_y: Velocidad en eje Y (mm/s) - positivo=adelante, negativo=atrás
        :param fake: Si es True, solo retorna los valores calculados sin ejecutar
        :return: Si fake=True retorna (velocity, direction), sino ejecuta el movimiento
        
        EJEMPLOS:
        - translation(0, 100): Avanza recto hacia adelante a 100mm/s
        - translation(100, 0): Se mueve lateral puro hacia la derecha
        - translation(100, 100): Se mueve en diagonal 45° (adelante-derecha)
        - translation(-50, 50): Se mueve en diagonal (adelante-izquierda)
        """
        # PASO 1: Calcular la magnitud de la velocidad (teorema de Pitágoras)
        # Si vx=3 y vy=4, entonces velocity=5 (hipotenusa del triángulo 3-4-5)
        velocity = math.sqrt(velocity_x ** 2 + velocity_y ** 2)
        
        # PASO 2: Calcular la dirección (ángulo) usando trigonometría
        # Casos especiales primero (cuando vx=0):
        if velocity_x == 0:
            # Movimiento puramente vertical
            direction = 90 if velocity_y >= 0 else 270  # 90°=adelante, 270°=atrás
        else:
            if velocity_y == 0:
                # Movimiento puramente horizontal
                direction = 0 if velocity_x > 0 else 180  # 0°=derecha, 180°=izquierda
            else:
                # Movimiento diagonal: usar arcotangente
                # θ = arctan(y/x) nos da el ángulo en radianes
                direction = math.atan(velocity_y / velocity_x)  
                
                # Convertir radianes a grados
                direction = direction * 180 / math.pi
                
                # AJUSTES DE CUADRANTE:
                # atan solo retorna -90° a +90°, necesitamos 0° a 360°
                if velocity_x < 0:
                    # Cuadrantes 2 y 3 (izquierda): sumar 180°
                    direction += 180
                else:
                    # Cuadrante 4 (abajo-derecha): convertir negativo a positivo
                    if velocity_y < 0:
                        direction += 360
        
        # PASO 3: Ejecutar o retornar
        if fake:
            # Modo test: solo retorna los valores calculados
            return velocity, direction
        else:
            # Modo normal: ejecuta el movimiento sin rotación (angular_rate=0)
            return self.set_velocity(velocity, direction, 0)

