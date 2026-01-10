# TurboPy Hardware Workspace (Raspberry Pi - Humble)

Este workspace contiene todos los drivers de hardware del robot TurboPy.

Aquí se controla directamente:
- Motores
- Encoders
- LEDs
- Buzzer
- Servos
- Sensores
- Cámaras

No existe lógica de navegación ni planificación en este workspace.

---

## 📦 Paquetes esperados

```
turbopy_hw_ws/src/
├── turbopy_base_driver
├── turbopy_led_driver
├── turbopy_buzzer_driver
├── turbopy_servo_driver
├── turbopy_sensors_driver
└── turbopy_camera_driver
```


---

## 🔌 Interfaces

Este workspace se comunica con el PC únicamente mediante ROS 2 topics.

Ejemplo:
- Recibe: `/cmd_vel`
- Publica: `/odom`, `/image_raw`, `/battery`

---

## ▶️ Compilación

```bash
cd turbopy_hw_ws
colcon build
source install/setup.bash

