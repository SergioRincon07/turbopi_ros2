# TurboPy ROS Workspace (PC - Jazzy)

Este workspace contiene todos los paquetes de alto nivel del sistema TurboPy.

Aquí se ejecutan:
- Simulación
- Navegación
- Visualización (RViz)
- Planificación
- Control de misión

Este workspace **no contiene drivers de hardware**.

---

## 📦 Paquetes esperados

```
turbopy_ros_ws/src/
├── turbopy_description # URDF, Xacro, TF
├── turbopy_simulation # Gazebo / Isaac
├── turbopy_navigation # Nav2, planners
├── turbopy_teleop # Control manual
└── turbopy_bringup # Launch del sistema completo
```

---

## 🔌 Dependencias

Este workspace depende de que el robot (Raspberry Pi) esté ejecutando
los drivers de hardware y publicando:

- `/odom`
- `/joint_states`
- sensores
- cámara

---

## ▶️ Compilación

```bash
cd turbopy_ros_ws
colcon build
source install/setup.bash
