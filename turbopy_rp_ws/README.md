# TurboPy – Workspace Raspberry Pi (Humble)

Workspace ROS 2 (Humble) que corre **en la Raspberry Pi** y contiene los drivers de hardware de TurboPy.

Aquí se controla directamente:
- Motores (base móvil)
- LEDs RGB
- Buzzer
- Batería (lectura de tensión)

La navegación, mapeado, etc. van en el workspace del PC. Este workspace es solo "interface de hardware".

---

## 1. Estructura de paquetes

En este workspace (turbopy_rp_ws/src):

```text
turbopy_rp_ws/src/
├── turbopy_hw/              # Capa de abstracción de hardware (Hiwonder, etc.)
├── turbopy_base_driver/     # Nodo de base: motores + batería
├── turbopy_led_driver/      # Nodo de LEDs RGB (opcional)
└── turbopy_buzzer_driver/   # Nodo de buzzer (opcional)
```
## 2. Interfaces ROS 2 principales
Los drivers se comunican con el resto del sistema únicamente mediante topics ROS 2.

```
turbopy_base_driver
Suscribe: /cmd_vel (geometry_msgs/Twist)
Publica: /battery (sensor_msgs/BatteryState)
Otros topics definidos en el proyecto completo se documentan en
ros2_ws/turbopi_ros2/docs/topics.md.
```

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
cd ~/ros2_ws/turbopi_ros2/turbopy_rp_ws
source install/setup.bash
```

### 3.4. Hay perifericos que toca manejarlos con root
Algunas partes del SDK de la placa Hiwonder usan rpi_ws281x y acceden a /dev/mem, por lo que el nodo de base debe correr como root.
```bash
sudo ./run_turbopy_base_node_root.sh
```

## 4. Pruebas locales de /cmd_vel y /battery
Con el nodo turbopy_base_driver corriendo en la Raspberry Pi (como root), abre otra terminal normal:

### 4.1. Publicar en /cmd_vel
Ejemplo de comando para mandar una velocidad lineal hacia delante:
```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.2, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

O publicando de forma continua a 5 Hz:
```bash
ros2 topic pub -r 5 /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.2, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

### 4.2. Leer /battery
Deberías ver mensajes sensor_msgs/BatteryState con el voltaje de la batería.
```bash
ros2 topic echo /battery
```