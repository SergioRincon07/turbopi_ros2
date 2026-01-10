import math
from typing import Tuple

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import BatteryState

from turbopy_hw import create_motor_driver, create_battery_interface


class BaseDriverNode(Node):
    """Driver de base simple para TurboPi.

    - Suscribe a /cmd_vel (geometry_msgs/Twist).
    - Controla los motores vía turbopy_hw (independiente de la placa).
    - Publica /battery (sensor_msgs/BatteryState).

    NOTA: La cinemática aquí es muy básica (todos los motores igual según
    linear.x). Más adelante se puede sustituir por un modelo de Mecanum
    completo reutilizando la misma interfaz de motor.
    """

    def __init__(self) -> None:
        super().__init__('turbopy_base_driver')

        self.declare_parameter('board_type', 'hiwonder')
        board_type = self.get_parameter('board_type').get_parameter_value().string_value

        try:
            self._motors = create_motor_driver(board_type)
            self._battery = create_battery_interface(board_type)
        except Exception as exc:  # noqa: BLE001
            self.get_logger().error(f'No se pudo inicializar la capa de hardware: {exc!r}')
            raise

        self.declare_parameter('max_linear_speed', 0.5)  # m/s

        self._sub_cmd_vel = self.create_subscription(
            Twist,
            'cmd_vel',
            self._on_cmd_vel,
            10,
        )

        self._pub_battery = self.create_publisher(BatteryState, 'battery', 10)
        self._battery_timer = self.create_timer(1.0, self._publish_battery)

        self.get_logger().info('turbopy_base_driver listo. Suscrito a /cmd_vel, publicando /battery.')

    # ------------------------------------------------------------------
    # Control de base
    # ------------------------------------------------------------------

    def _on_cmd_vel(self, msg: Twist) -> None:
        max_linear = self.get_parameter('max_linear_speed').get_parameter_value().double_value

        # Normalizamos linear.x a [-1, 1] y lo usamos para todos los motores.
        lin = max(-max_linear, min(max_linear, msg.linear.x))
        if max_linear > 0.0:
            norm = lin / max_linear
        else:
            norm = 0.0

        # Por ahora: todos los motores con la misma velocidad.
        for motor_id in (1, 2, 3, 4):
            self._motors.set_motor_speed(motor_id, norm)

    # ------------------------------------------------------------------
    # Batería
    # ------------------------------------------------------------------

    def _publish_battery(self) -> None:
        try:
            voltage = float(self._battery.get_voltage())
        except Exception as exc:  # noqa: BLE001
            self.get_logger().warn(f'Error leyendo batería: {exc!r}')
            return

        msg = BatteryState()
        msg.voltage = voltage
        msg.present = True
        # El resto de campos se dejan sin rellenar de momento.

        self._pub_battery.publish(msg)


def main(args=None) -> None:  # noqa: D401
    rclpy.init(args=args)
    node = BaseDriverNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
