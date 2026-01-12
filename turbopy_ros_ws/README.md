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


## 3. Compilar el workspace (Raspberry Pi)

En la Raspberry Pi (Ubuntu 22.04 + ROS 2 Humble):

### 3.1. Compilar el workspace

```bash
cd ~/ros2_ws/turbopi_ros2/
./build_workspace.sh
```

### 3.2. Configurar CycloneDDS (middleware)

```bash
cd ~/ros2_ws/turbopi_ros2/
./setup_cyclonedds.sh
source setup_cyclonedds.sh
```

### 3.3. Cargar entorno ROS 2 + paquete

```bash
cd ~/ros2_ws/turbopi_ros2/turbopy_ros_ws
source install/setup.bash
```

### 3.4. Hay perifericos que toca manejarlos con root

Algunas partes del SDK de la placa Hiwonder usan rpi_ws281x y acceden a /dev/mem, por lo que el nodo de base debe correr como root.

```bash
ros2 run turbopy_teleop keyboard_teleop
```