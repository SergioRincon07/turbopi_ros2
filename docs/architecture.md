# TurboPy – Arquitectura del sistema

TurboPy está diseñado como un sistema robótico distribuido.

El PC ejecuta la inteligencia.
La Raspberry Pi ejecuta el cuerpo.

### 1. Capa de Hardware
Drivers que interactúan con el mundo físico.

```
┌───────────────────────────┐
│        CAPA ALTA          │
│  Simulación / UI / Plan   │
│  (PC potente - Jazzy)     │
└────────────▲──────────────┘
             │ ROS 2 topics / actions
┌────────────┴──────────────┐
│      CAPA MEDIA           │
│   Lógica del robot        │
│  (agnóstica de hardware)  │
└────────────▲──────────────┘
             │ comandos abstractos
┌────────────┴──────────────┐
│      CAPA BAJA            │
│   Drivers / Hardware      │
│  (Raspberry - Humble)     │
└───────────────────────────┘
```

### 2. Capa de Control
Interfaces ROS que abstraen el hardware.
```
┌──────────────────────────────────────────┐
│          PC POTENTE (Jazzy)              │
│  turbopy_ros_ws                          │
│  - navegación                            │
│  - simulación                            │
│  - RViz                                  │
│  - teleop                                │
│  - planificación                         │
└───────────────▲──────────────────────────┘
                │ DDS (ROS 2 network)
┌───────────────┴──────────────────────────┐
│        Raspberry Pi (Humble)             │
│  turbopy_hw_ws                           │
│  - ruedas                                │
│  - leds                                  │
│  - buzzer                                │
│  - cámara                                │
│  - sensores                              │
└──────────────────────────────────────────┘

```

### 3. Capa de Comportamiento
Planificación, navegación y lógica de misión.


El PC nunca habla directamente con GPIO o serial.
Solo habla con topics.