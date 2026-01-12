#!/usr/bin/env python3
"""
Nodo de teleoperación con teclado para TurboPi usando teclas WASD.

Controles:
  W/S - Adelante/Atrás (linear.y)
  A/D - Izquierda/Derecha lateral (linear.x) 
  Q/E/Z/C - Movimientos diagonales
  G/H - Rotar izquierda/derecha (angular.z)
  Espacio - Detener
  ESC - Salir

El robot TurboPi tiene ruedas mecanum, por lo que puede moverse en cualquier dirección.
"""

import sys
import select
import termios
import tty
import threading
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class KeyboardTeleopNode(Node):
    """Nodo de teleoperación con teclado WASD."""

    def __init__(self):
        super().__init__('keyboard_teleop')

        # Parámetros configurables
        self.declare_parameter('linear_speed', 0.1)   # m/s
        self.declare_parameter('angular_speed', 1.0)  # rad/s
        self.declare_parameter('speed_increment', 0.01)  # Incremento de velocidad

        # Publisher para comandos de velocidad
        self._pub_cmd_vel = self.create_publisher(Twist, 'cmd_vel', 10)

        # Estado de las teclas presionadas con timestamp
        self._keys_pressed = {}  # {key: timestamp}
        self._lock = threading.Lock()
        self._key_timeout = 1  # Segundos antes de considerar la tecla "soltada"

        # Timer para publicar comandos continuamente
        self._publish_timer = self.create_timer(0.05, self._publish_cmd_vel)  # 20 Hz
        
        # Timer para actualizar display
        self._display_timer = self.create_timer(0.2, self._update_display)  # 5 Hz

        # Velocidades actuales
        self._current_linear_speed = self.get_parameter('linear_speed').value
        self._current_angular_speed = self.get_parameter('angular_speed').value

        # Estado actual del movimiento
        self._current_twist = Twist()

        # Configuración del terminal
        self._settings = termios.tcgetattr(sys.stdin)
        self._running = True

        # Imprimir instrucciones ANTES de poner el terminal en modo raw
        self._print_instructions()
        self.get_logger().info('Nodo de teleoperación iniciado. Usa WASD para controlar.')
        
        # Esperar un momento para que se vean las instrucciones
        time.sleep(0.5)

        # Iniciar listener de teclado en thread separado
        self._keyboard_thread = threading.Thread(target=self._keyboard_listener)
        self._keyboard_thread.daemon = True
        self._keyboard_thread.start()

    def _keyboard_listener(self):
        """Lee teclas desde la consola en modo raw."""
        try:
            tty.setraw(sys.stdin.fileno())
            while self._running and rclpy.ok():
                # Leer con timeout más corto para ser más responsive
                if select.select([sys.stdin], [], [], 0.05)[0]:
                    key = sys.stdin.read(1)
                    self._process_key(key)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._settings)

    def _process_key(self, key):
        """Procesa una tecla presionada."""
        with self._lock:
            key_lower = key.lower()
            
            # Debug: mostrar qué tecla se detectó
            # print(f"\rTecla detectada: {repr(key)} ({ord(key)})", end='', flush=True)
            
            """
            W - Adelante
            S - Atrás
            A - Lateral izquierda
            D - Lateral derecha
            Q - Diagonal izquierda (Adelante)
            E - Diagonal derecha (Adelante)
            Z - Diagonal izquierda (Atrás)
            C - Diagonal derecha (Atrás)
            
            g - Girar izquierda (antihorario)
            h - Girar derecha (horario)

            Espacio - Detener
            ESC - Salir
            +/- - Aumentar/Disminuir velocidad
            
            """     

            # Teclas de movimiento - añadir al conjunto de teclas presionadas
            if key_lower in ['w', 's', 'a', 'd', 'q', 'e', 'z', 'c', 'g', 'h']:
                self._keys_pressed[key_lower] = time.time()
            
            # Teclas de control instantáneas
            elif key == ' ':  # Espacio
                self._keys_pressed.clear()
                self._publish_stop()
            
            elif key == '\x1b' or key == '\x03':  # ESC o Ctrl+C
                self._publish_stop()
                self._running = False
                rclpy.shutdown()
            
            elif key == '+' or key == '=':
                increment = self.get_parameter('speed_increment').value
                self._current_linear_speed += increment
                self._current_angular_speed += increment * 10
            
            elif key == '-' or key == '_':
                increment = self.get_parameter('speed_increment').value
                self._current_linear_speed = max(0.03, self._current_linear_speed - increment)   # Velocidad mínima 0.03 m/s
                self._current_angular_speed = max(0.5, self._current_angular_speed - increment * 10)
    
    def _clean_old_keys(self):
        """Elimina teclas que no se han presionado recientemente."""
        current_time = time.time()
        keys_to_remove = [k for k, t in self._keys_pressed.items() 
                         if current_time - t > self._key_timeout]
        for key in keys_to_remove:
            del self._keys_pressed[key]


    def _print_instructions(self):
        """Muestra las instrucciones de control."""
        # Limpiar pantalla
        print("\033[2J\033[H", end='', flush=True)
        print("\n" + "="*60)
        print("  CONTROL DE TELEOPERACIÓN - TurboPi")
        print("="*60)
        print("\n  Movimiento:")
        print("    W - Adelante")
        print("    S - Atrás")
        print("    A - Lateral izquierda")
        print("    D - Lateral derecha")
        print("\n  Diagonal:")
        print("    Q - Diagonal izquierda (Adelante)")
        print("    E - Diagonal derecha (Adelante)")
        print("    Z - Diagonal izquierda (Atrás)")
        print("    C - Diagonal derecha (Atrás)")
        print("\n  Rotación:")
        print("    G - Girar izquierda (antihorario)")
        print("    H - Girar derecha (horario)")
        print("\n  NOTA: Presiona y mantén las teclas para movimiento continuo")
        print("\n  Control:")
        print("    ESPACIO - Detener")
        print("    +/-     - Aumentar/Disminuir velocidad")
        print("    ESC     - Salir")
        print("\n" + "="*60)
        print(f"  Velocidad lineal: {self._current_linear_speed:.2f} m/s")
        print(f"  Velocidad angular: {self._current_angular_speed:.2f} rad/s")
        print("="*60 + "\n")
        print("Iniciando control de teclado...\n")
        sys.stdout.flush()

    def _update_display(self):
        """Actualiza el display en consola con el estado actual."""
        with self._lock:
            # En modo raw, necesitamos usar \r\n para saltos de línea
            # Mover cursor a una posición fija (línea 20)
            output = "\033[20;0H"
            
            # Estado de teclas presionadas
            active_keys = list(self._keys_pressed.keys())
            keys_str = ', '.join(active_keys).upper() if active_keys else 'ninguna'
            
            # Estado de velocidad
            output += f"┌{'─'*58}┐\r\n"
            output += f"│ {'ESTADO ACTUAL':^56} │\r\n"
            output += f"├{'─'*58}┤\r\n"
            output += f"│ Teclas activas: {keys_str:<41} │\r\n"
            output += f"│                                                          │\r\n"
            output += f"│ Linear X (lateral):  {self._current_twist.linear.x:>6.2f} m/s               │\r\n"
            output += f"│ Linear Y (adelante): {self._current_twist.linear.y:>6.2f} m/s               │\r\n"
            output += f"│ Angular Z (giro):    {self._current_twist.angular.z:>6.2f} rad/s            │\r\n"
            output += f"│                                                          │\r\n"
            output += f"│ Vel. config linear:  {self._current_linear_speed:>6.2f} m/s               │\r\n"
            output += f"│ Vel. config angular: {self._current_angular_speed:>6.2f} rad/s            │\r\n"
            output += f"└{'─'*58}┘\r\n"
            output += "\r\nPresiona ESC o Ctrl+C para salir                          \r\n"
            
            # Escribir todo de una vez
            sys.stdout.write(output)
            sys.stdout.flush()

    def _publish_cmd_vel(self):
        """Publica comandos de velocidad basados en las teclas presionadas."""
        with self._lock:
            # Limpiar teclas antiguas
            self._clean_old_keys()
            
            twist = Twist()

            # Movimiento lineal en Y (adelante/atrás)
            if 'w' in self._keys_pressed:
                twist.linear.y = self._current_linear_speed
            if 's' in self._keys_pressed:
                twist.linear.y -= self._current_linear_speed

            # Movimiento lineal en X (lateral izquierda/derecha)
            if 'a' in self._keys_pressed:
                twist.linear.x = -self._current_linear_speed
            if 'd' in self._keys_pressed:
                twist.linear.x += self._current_linear_speed

            # Movimientos diagonales (combinan X e Y)
            if 'q' in self._keys_pressed:  # Diagonal izquierda adelante
                twist.linear.y = self._current_linear_speed
                twist.linear.x = -self._current_linear_speed
            if 'e' in self._keys_pressed:  # Diagonal derecha adelante
                twist.linear.y = self._current_linear_speed
                twist.linear.x = self._current_linear_speed
            if 'z' in self._keys_pressed:  # Diagonal izquierda atrás
                twist.linear.y = -self._current_linear_speed
                twist.linear.x = -self._current_linear_speed
            if 'c' in self._keys_pressed:  # Diagonal derecha atrás
                twist.linear.y = -self._current_linear_speed
                twist.linear.x = self._current_linear_speed

            # Rotación (girar sobre su eje)
            if 'g' in self._keys_pressed:
                twist.angular.z = self._current_angular_speed
            if 'h' in self._keys_pressed:
                twist.angular.z -= self._current_angular_speed

            # Guardar estado actual
            self._current_twist = twist
            
            # Publicar comando
            self._pub_cmd_vel.publish(twist)

    def _publish_stop(self):
        """Publica un comando de velocidad cero para detener el robot."""
        twist = Twist()
        self._pub_cmd_vel.publish(twist)

    def destroy_node(self):
        """Limpia recursos al destruir el nodo."""
        self._publish_stop()
        self._running = False
        # Restaurar configuración del terminal
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._settings)
            # Limpiar pantalla y restaurar cursor
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.write("Nodo de teleoperación detenido.\r\n")
            sys.stdout.flush()
        except:
            pass
        super().destroy_node()



def main(args=None):
    """Función principal."""
    rclpy.init(args=args)
    node = None
    
    try:
        node = KeyboardTeleopNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if node:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
