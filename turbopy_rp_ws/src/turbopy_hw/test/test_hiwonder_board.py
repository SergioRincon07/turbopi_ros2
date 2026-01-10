from __future__ import annotations

"""Pruebas básicas (sin hardware real) para turbopy_hw.hiwonder_board.

Este script sustituye HiwonderSDK.Board por un FakeBoard que sólo imprime
por pantalla lo que recibiría el hardware real. Así podemos validar que
la lógica de adaptación (clamping, rangos, etc.) funciona.

Ejecutar desde la carpeta turbopy_rp_ws:

    python3 -m turbopy_hw.test_hiwonder_board

"""


class FakeRGB:
    def setPixelColor(self, index, color):
        print(f"FakeRGB.setPixelColor(index={index}, color={color})")

    def show(self):
        print("FakeRGB.show()")


class FakeBoard:
    RGB = FakeRGB()

    @staticmethod
    def setMotor(motor_id: int, value: int) -> None:
        print(f"FakeBoard.setMotor(motor_id={motor_id}, value={value})")

    @staticmethod
    def setBuzzer(value: int) -> None:
        print(f"FakeBoard.setBuzzer(value={value})")

    @staticmethod
    def getBattery() -> int:
        # 7.4 V expresados en mV
        return 7400

    @staticmethod
    def PixelColor(r: int, g: int, b: int):
        # Representamos el color como una tupla simplemente para depuración
        return (r, g, b)


def main() -> None:
    # Inyectamos un módulo falso en sys.modules para evitar que
    # HiwonderSDK.Board intente acceder al hardware real (/dev/mem, etc.).
    import sys as _sys
    import types as _types

    # Registramos FakeBoard como si fuera HiwonderSDK.Board
    _sys.modules["HiwonderSDK.Board"] = FakeBoard

    # Importamos el submódulo del adaptador desde el paquete interno
    # Estructura en src:
    #   turbopy_hw/
    #       turbopy_hw/
    #           hiwonder_board.py
    from turbopy_hw.turbopy_hw import hiwonder_board as hb

    # Nos aseguramos de que utilice nuestro FakeBoard
    hb.Board = FakeBoard

    print("=== Prueba HiwonderMotorDriver ===")
    motor = hb.HiwonderMotorDriver(max_speed=100)
    motor.set_motor_speed(1, 0.5)   # debe dar ~50
    motor.set_motor_speed(1, 2.0)   # debe saturar a +100
    motor.set_motor_speed(2, -0.5)  # debe dar ~-50
    motor.set_motor_speed(2, -2.0)  # debe saturar a -100
    motor.stop_all()                # todos a 0

    print("\n=== Prueba HiwonderLedDriver ===")
    led = hb.HiwonderLedDriver()
    led.set_pixel(0, 255, 0, 0)     # rojo
    led.set_pixel(1, 0, 255, 0)     # verde
    led.show()
    led.clear()                     # apaga LEDs

    print("\n=== Prueba HiwonderBuzzerDriver ===")
    buz = hb.HiwonderBuzzerDriver()
    buz.set_state(True)
    buz.set_state(False)

    print("\n=== Prueba HiwonderBatteryInterface ===")
    bat = hb.HiwonderBatteryInterface()
    voltage = bat.get_voltage()
    print(f"Voltaje leído: {voltage:.2f} V (esperado 7.40 V)")


if __name__ == "__main__":
    main()
