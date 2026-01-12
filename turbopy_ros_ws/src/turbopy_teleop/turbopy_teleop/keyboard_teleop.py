#!/usr/bin/env python3
"""
Nodo de teleoperación con teclado para TurboPi usando teclas WASD.

Controles:
  W/S - Adelante/Atrás (linear.y)
  A/D - Izquierda/Derecha lateral (linear.x) 
  Q/E - Rotar izquierda/derecha (angular.z)
  Espacio - Detener
  ESC - Salir

El robot TurboPi tiene ruedas mecanum, por lo que puede moverse en cualquier dirección.
"""

import sys
import threading
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

try:
    from pynput import keyboard
except ImportError:
    print("ERROR: pynput no está instalado. Instálalo con: pip install pynput")
    sys.exit(1)


class KeyboardTeleopNode(Node):
    """Nodo de teleoperación con teclado WASD."""

    def __init__(self):
        super().__init__('keyboard_teleop')

        # Parámetros configurables
        self.declare_parameter('linear_speed', 0.1)   # m/s
        self.declare_parameter('angular_speed', 1.0)  # rad/s
        self.declare_parameter('speed_increment', 0.05)  # Incremento de velocidad

        # Publisher para comandos de velocidad
        self._pub_cmd_vel = self.create_publisher(Twist, 'cmd_vel', 10)

        # Estado de las teclas presionadas
        self._keys_pressed = set()
        self._lock = threading.Lock()

        # Timer para publicar comandos continuamente
        self._publish_timer = self.create_timer(0.05, self._publish_cmd_vel)  # 20 Hz

        # Velocidades actuales
        self._current_linear_speed = self.get_parameter('linear_speed').value
        self._current_angular_speed = self.get_parameter('angular_speed').value

        # Iniciar listener de teclado en thread separado
        self._listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self._listener.start()

        self._print_instructions()
        self.get_logger().info('Nodo de teleoperación iniciado. Usa WASD para controlar.')

    def _print_instructions(self):
        """Muestra las instrucciones de control."""
        print("\n" + "="*60)
        print("  CONTROL DE TELEOPERACIÓN - TurboPi")
        print("="*60)
        print("\n  Movimiento:")
        print("    W - Adelante")
        print("    S - Atrás")
        print("    A - Lateral izquierda")
        print("    D - Lateral derecha")
        print("\n  Rotación:")
        print("    Q - Girar izquierda (antihorario)")
        print("    E - Girar derecha (horario)")
        print("\n  Combinaciones:")
        print("    W+A - Diagonal adelante-izquierda")
        print("    W+D - Diagonal adelante-derecha")
        print("    W+Q - Adelante girando a la izquierda")
        print("    etc...")
        print("\n  Control:")
        print("    ESPACIO - Detener")
        print("    +/-     - Aumentar/Disminuir velocidad")
        print("    ESC     - Salir")
        print("\n" + "="*60)
        print(f"  Velocidad lineal: {self._current_linear_speed:.2f} m/s")
        print(f"  Velocidad angular: {self._current_angular_speed:.2f} rad/s")
        print("="*60 + "\n")

    def _on_key_press(self, key):
        """Callback cuando se presiona una tecla."""
        with self._lock:
            try:
                # Teclas de carácter
                if hasattr(key, 'char') and key.char:
                    self._keys_pressed.add(key.char.lower())
                    
                    # Controles de velocidad
                    if key.char == '+' or key.char == '=':
                        increment = self.get_parameter('speed_increment').value
                        self._current_linear_speed += increment
                        self._current_angular_speed += increment * 10
                        self.get_logger().info(
                            f'Velocidad aumentada: linear={self._current_linear_speed:.2f} m/s, '
                            f'angular={self._current_angular_speed:.2f} rad/s'
                        )
                    elif key.char == '-':
                        increment = self.get_parameter('speed_increment').value
                        self._current_linear_speed = max(0.05, self._current_linear_speed - increment)
                        self._current_angular_speed = max(0.5, self._current_angular_speed - increment * 10)
                        self.get_logger().info(
                            f'Velocidad reducida: linear={self._current_linear_speed:.2f} m/s, '
                            f'angular={self._current_angular_speed:.2f} rad/s'
                        )
                else:
                    # Teclas especiales
                    if key == keyboard.Key.space:
                        self._keys_pressed.clear()
                        self._publish_stop()
                        self.get_logger().info('¡Detenido!')
                    elif key == keyboard.Key.esc:
                        self.get_logger().info('Saliendo...')
                        self._publish_stop()
                        rclpy.shutdown()
                        
            except AttributeError:
                pass

    def _on_key_release(self, key):
        """Callback cuando se suelta una tecla."""
        with self._lock:
            try:
                if hasattr(key, 'char') and key.char:
                    self._keys_pressed.discard(key.char.lower())
            except AttributeError:
                pass

    def _publish_cmd_vel(self):
        """Publica comandos de velocidad basados en las teclas presionadas."""
        with self._lock:
            twist = Twist()

            # Movimiento lineal en Y (adelante/atrás)
            if 'w' in self._keys_pressed:
                twist.linear.y = self._current_linear_speed
            if 's' in self._keys_pressed:
                twist.linear.y = -self._current_linear_speed

            # Movimiento lineal en X (lateral izquierda/derecha)
            if 'a' in self._keys_pressed:
                twist.linear.x = -self._current_linear_speed
            if 'd' in self._keys_pressed:
                twist.linear.x = self._current_linear_speed

            # Rotación (girar sobre su eje)
            if 'q' in self._keys_pressed:
                twist.angular.z = self._current_angular_speed
            if 'e' in self._keys_pressed:
                twist.angular.z = -self._current_angular_speed

            # Solo publicar si hay algún movimiento
            if (twist.linear.x != 0.0 or twist.linear.y != 0.0 or twist.angular.z != 0.0):
                self._pub_cmd_vel.publish(twist)

    def _publish_stop(self):
        """Publica un comando de velocidad cero para detener el robot."""
        twist = Twist()
        self._pub_cmd_vel.publish(twist)

    def destroy_node(self):
        """Limpia recursos al destruir el nodo."""
        self._publish_stop()
        if self._listener:
            self._listener.stop()
        super().destroy_node()


def main(args=None):
    """Función principal."""
    rclpy.init(args=args)
    
    try:
        node = KeyboardTeleopNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
