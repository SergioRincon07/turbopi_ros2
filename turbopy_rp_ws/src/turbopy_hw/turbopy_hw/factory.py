from __future__ import annotations

from typing import Literal

from .interfaces import (
    MotorDriverInterface,
    LedDriverInterface,
    BuzzerInterface,
    BatteryInterface,
)
from .hiwonder_board import (
    HiwonderMotorDriver,
    HiwonderLedDriver,
    HiwonderBuzzerDriver,
    HiwonderBatteryInterface,
)


BoardType = Literal['hiwonder']


def create_motor_driver(board: BoardType = 'hiwonder') -> MotorDriverInterface:
    if board == 'hiwonder':
        return HiwonderMotorDriver()
    raise ValueError(f"Tipo de placa no soportado: {board}")


def create_led_driver(board: BoardType = 'hiwonder') -> LedDriverInterface:
    if board == 'hiwonder':
        return HiwonderLedDriver()
    raise ValueError(f"Tipo de placa no soportado: {board}")


def create_buzzer_driver(board: BoardType = 'hiwonder') -> BuzzerInterface:
    if board == 'hiwonder':
        return HiwonderBuzzerDriver()
    raise ValueError(f"Tipo de placa no soportado: {board}")


def create_battery_interface(board: BoardType = 'hiwonder') -> BatteryInterface:
    if board == 'hiwonder':
        return HiwonderBatteryInterface()
    raise ValueError(f"Tipo de placa no soportado: {board}")
