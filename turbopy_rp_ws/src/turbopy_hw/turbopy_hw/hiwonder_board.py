from __future__ import annotations

from typing import Optional

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import HiwonderSDK.Board as Board

from .interfaces import (
    MotorDriverInterface,
    LedDriverInterface,
    BuzzerInterface,
    BatteryInterface,
)


class HiwonderMotorDriver(MotorDriverInterface):
    """Adaptador de motores para la placa Hiwonder (Board.setMotor).

    Esta implementación traduce una velocidad normalizada [-1.0, 1.0]
    al rango entero que espera Board.setMotor (aprox. -100..100).
    """

    def __init__(self, max_speed: int = 100) -> None:
        if Board is None:
            raise RuntimeError("HiwonderSDK.Board no está disponible en este entorno")
        self._max_speed = max(1, int(max_speed))

    def set_motor_speed(self, motor_id: int, speed: float) -> None:
        clamped = max(-1.0, min(1.0, speed))
        hw_speed = int(clamped * self._max_speed)
        Board.setMotor(motor_id, hw_speed)

    def stop_all(self) -> None:
        for motor_id in (1, 2, 3, 4):
            Board.setMotor(motor_id, 0)


class HiwonderLedDriver(LedDriverInterface):
    """Adaptador para los LEDs RGB integrados en la placa/sonar Hiwonder."""

    def __init__(self) -> None:
        if Board is None:
            raise RuntimeError("HiwonderSDK.Board no está disponible en este entorno")

    def set_pixel(self, index: int, r: int, g: int, b: int) -> None:
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))
        Board.RGB.setPixelColor(index, Board.PixelColor(r, g, b))

    def show(self) -> None:
        Board.RGB.show()

    def clear(self) -> None:
        # Suponemos dos LEDs como en el código original; si son más
        # se puede generalizar con un parámetro.
        for i in (0, 1):
            Board.RGB.setPixelColor(i, Board.PixelColor(0, 0, 0))
        Board.RGB.show()


class HiwonderBuzzerDriver(BuzzerInterface):
    """Adaptador de buzzer para Hiwonder (Board.setBuzzer)."""

    def __init__(self) -> None:
        if Board is None:
            raise RuntimeError("HiwonderSDK.Board no está disponible en este entorno")

    def set_state(self, on: bool) -> None:
        Board.setBuzzer(1 if on else 0)


class HiwonderBatteryInterface(BatteryInterface):
    """Lectura de batería vía Board.getBattery()."""

    def __init__(self) -> None:
        if Board is None:
            raise RuntimeError("HiwonderSDK.Board no está disponible en este entorno")

    def get_voltage(self) -> float:
        # El SDK devuelve mV según la documentación de TurboPi.
        mv = float(Board.getBattery())
        return mv / 1000.0
