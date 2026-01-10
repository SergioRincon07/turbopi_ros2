from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable, Tuple


@runtime_checkable
class MotorDriverInterface(Protocol):
    """Interfaz abstracta para el control de motores.

    La idea es que cualquier tarjeta de control implemente estos métodos,
    y el resto del código (ROS2, lógica de alto nivel) dependa solo de esta
    interfaz, no de la librería concreta (HiwonderSDK, PCA9685, etc.).
    """

    @abstractmethod
    def set_motor_speed(self, motor_id: int, speed: float) -> None:
        """Fija la velocidad de un motor individual.

        :param motor_id: identificador lógico del motor (1..N)
        :param speed: velocidad normalizada en el rango [-1.0, 1.0]
        """
        raise NotImplementedError

    @abstractmethod
    def stop_all(self) -> None:
        """Detiene todos los motores controlados por esta tarjeta."""
        raise NotImplementedError


@runtime_checkable
class LedDriverInterface(Protocol):
    """Interfaz abstracta para LEDs RGB direccionables."""

    @abstractmethod
    def set_pixel(self, index: int, r: int, g: int, b: int) -> None:
        """Fija el color de un pixel LED.

        :param index: índice del LED (0..N-1)
        :param r: componente rojo (0-255)
        :param g: componente verde (0-255)
        :param b: componente azul (0-255)
        """
        raise NotImplementedError

    @abstractmethod
    def show(self) -> None:
        """Envía el buffer de LEDs al hardware."""
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Apaga todos los LEDs controlados."""
        raise NotImplementedError


@runtime_checkable
class BuzzerInterface(Protocol):
    """Interfaz abstracta para el zumbador."""

    @abstractmethod
    def set_state(self, on: bool) -> None:
        """Enciende o apaga el buzzer."""
        raise NotImplementedError


@runtime_checkable
class BatteryInterface(Protocol):
    """Interfaz abstracta para lectura de batería."""

    @abstractmethod
    def get_voltage(self) -> float:
        """Devuelve la tensión de batería en voltios."""
        raise NotImplementedError
