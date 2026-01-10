# TurboPy ROS Platform

TurboPy ROS Platform es una plataforma robótica distribuida basada en ROS 2.
Este repositorio define completamente el comportamiento, la simulación y el control
del robot TurboPy, así como de futuras variantes del robot.

El sistema está dividido en dos grandes entornos:

| Entorno | ROS | Función |
|-------|-----|--------|
| PC de alto rendimiento | ROS 2 Jazzy | Simulación, navegación, planificación, visualización |
| Raspberry Pi | ROS 2 Humble | Control físico del robot (motores, sensores, actuadores) |

Ambos entornos se comunican usando ROS 2 DDS en red.

---

## 📂 Estructura del repositorio

```
turbopy_ros/
├── turbopy_ros_ws/     ← PC potente (Jazzy)
│   ├── src/
│   │   ├── turbopy_description
│   │   ├── turbopy_navigation
│   │   ├── turbopy_simulation
│   │   ├── turbopy_teleop
│   │   └── turbopy_bringup
│   └── README.md
│
├── turbopy_hw_ws/      ← Raspberry Pi (Humble)
│   ├── src/
│   │   ├── turbopy_base_driver
│   │   ├── turbopy_led_driver
│   │   ├── turbopy_buzzer_driver
│   │   ├── turbopy_servo_driver
│   │   └── turbopy_camera_driver
│   └── README.md
│
├── docs/
│   ├── architecture.md
│   ├── topics.md
│   └── wiring.md
│
└── README.md
└── .gitignore

---

## 📖 Documentación

Toda la información del sistema se encuentra en:

- `docs/architecture.md` → Arquitectura general
- `docs/topics.md` → Interfaz ROS (topics, mensajes)
- `docs/wiring.md` → Conexiones físicas del robot

---

## 🎯 Objetivo del proyecto

Este proyecto no define un solo robot, sino una plataforma reutilizable
para construir múltiples robots a partir de los mismos módulos.

Las variaciones del robot se definen mediante configuraciones de lanzamiento
(`bringup`) y no mediante cambios de código.
