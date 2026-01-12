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
sudo -E bash
source install/setup.bash
ros2 run turbopy_base_driver turbopy_base_node
```

## 4. Pruebas locales de /cmd_vel y /battery

Con el nodo turbopy_base_driver corriendo en la Raspberry Pi (como root), abre otra terminal normal:

### 4.1. Publicar en /cmd_vel

Ejemplo de comando para mandar una velocidad lineal hacia delante:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

O publicando de forma continua a 5 Hz:

```bash
ros2 topic pub -r 5 /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.2, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

stop

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

### 4.2. Leer /battery

Deberías ver mensajes sensor_msgs/BatteryState con el voltaje de la batería.

```bash
ros2 topic echo /battery
```

---

## 5. Cinemática del Robot Mecanum

Este robot utiliza **ruedas mecanum**, que tienen rodillos a 45° permitiendo movimiento omnidireccional (puede moverse en cualquier dirección sin necesidad de girar primero).

### 5.1. Configuración de las ruedas

```
motor1 (A) |  ↑  | motor2 (B)
           |     |
motor3 (B) |     | motor4 (A)
```

Las ruedas tipo A y B tienen rodillos orientados en direcciones opuestas, lo que genera el efecto omnidireccional.

### 5.2. Funciones principales en `mecanum.py`

#### `set_velocity(velocity, direction, angular_rate)`

Función de control usando **coordenadas polares**:

- **velocity**: Magnitud de velocidad en mm/s
- **direction**: Ángulo de movimiento (0-360°)
  - 0°: Derecha pura
  - 90°: Adelante
  - 180°: Izquierda
  - 270°: Atrás
- **angular_rate**: Velocidad de rotación sobre su eje

**Algoritmo interno:**

1. Convierte polar a cartesiano: $v_x = \text{velocity} \times \cos(\text{direction})$, $v_y = \text{velocity} \times \sin(\text{direction})$
2. Calcula componente de rotación: $v_p = -\text{angular\_rate} \times (a + b)$
3. Aplica cinemática inversa para cada rueda:
   - $v_1 = v_y + v_x - v_p$ (frontal izquierdo)
   - $v_2 = v_y - v_x + v_p$ (frontal derecho)
   - $v_3 = v_y - v_x - v_p$ (trasero izquierdo)
   - $v_4 = v_y + v_x + v_p$ (trasero derecho)

Estas fórmulas provienen de la geometría de los rodillos a 45° y distribuyen correctamente la velocidad entre las 4 ruedas.

#### `translation(velocity_x, velocity_y)`

Función de control usando **coordenadas cartesianas**:

- **velocity_x**: Velocidad en eje X (+ derecha, - izquierda)
- **velocity_y**: Velocidad en eje Y (+ adelante, - atrás)

Internamente convierte cartesiano → polar y llama a `set_velocity()` con `angular_rate=0`.

**Ejemplos:**

```python
chassis.translation(0, 100)      # Adelante a 100mm/s
chassis.translation(100, 0)      # Derecha pura
chassis.translation(100, 100)    # Diagonal 45° (adelante-derecha)
chassis.translation(-50, 50)     # Diagonal (adelante-izquierda)
```

---

## 6. Por qué usar Coordenadas Cartesianas con ROS 2

Aunque el SDK de Hiwonder usa coordenadas polares, **en ROS 2 el estándar son las coordenadas cartesianas** por las siguientes razones:

### 6.1. Compatibilidad con el ecosistema ROS 2

El mensaje `geometry_msgs/msg/Twist` es el **lenguaje universal** para robots móviles en ROS 2:

```
linear.x   → Velocidad adelante/atrás
linear.y   → Velocidad lateral (strafing) - ¡Clave para mecanum!
linear.z   → (No usado en robots terrestres)
angular.x  → (No usado típicamente)
angular.y  → (No usado típicamente)
angular.z  → Velocidad de rotación (yaw)
```

**Ventajas:**

- ✅ Compatible con todos los nodos de navegación (Nav2, SLAM Toolbox)
- ✅ Funciona con herramientas de teleoperación (joystick, teclado)
- ✅ Soportado nativamente por plugins de Gazebo
- ✅ Facilita integración con sensores (Lidar, cámaras, IMU)
- ✅ Simplifica algoritmos de planificación de trayectorias

### 6.2. Integración con Gazebo

Para simulación en Gazebo, se utiliza el plugin `libgazebo_ros_planar_move.so` (o similar) en el archivo URDF/XACRO del robot. Este plugin:

1. **Escucha** el topic `/cmd_vel` automáticamente
2. **Lee** los valores cartesianos `linear.x`, `linear.y`, `angular.z`
3. **Aplica** las fuerzas necesarias a las 4 ruedas usando la cinemática interna

**Sin coordenadas cartesianas**, tendrías que escribir tu propio plugin de Gazebo, lo cual es innecesario y complejo.

### 6.3. Ejemplos de comandos Twist

**Movimiento adelante:**

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

**Movimiento lateral (derecha):**

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.0, y: -0.3, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

_Nota: Valor negativo en `y` = derecha según convención ROS_

**Diagonal 45° (adelante-derecha):**

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.3, y: -0.3, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

**Rotación pura (sin traslación):**

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.5}}"
```

**Movimiento complejo (adelante + rotando):**

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.2, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.3}}"
```

### 6.4. Conversión Cartesiano ↔ Polar (si es necesario)

Si tienes un algoritmo que genera comandos en polares, puedes convertirlos fácilmente:

**Polar → Cartesiano:**
$$v_x = \text{velocidad} \times \cos(\text{ángulo})$$
$$v_y = \text{velocidad} \times \sin(\text{ángulo})$$

**Cartesiano → Polar:**
$$\text{velocidad} = \sqrt{v_x^2 + v_y^2}$$
$$\text{ángulo} = \arctan2(v_y, v_x)$$

_Nota: En Python, `mecanum.py` incluye la función `translation()` que hace esta conversión automáticamente._

### 6.5. Resumen: Configuración recomendada

| Componente            | Configuración                                |
| --------------------- | -------------------------------------------- |
| **Mensaje ROS 2**     | `geometry_msgs/msg/Twist` (cartesianas)      |
| **Simulación Gazebo** | Plugin `libgazebo_ros_planar_move.so`        |
| **Control físico**    | `mecanum.py` → función `translation(vx, vy)` |
| **Navegación**        | Nav2 con soporte mecanum nativo              |

**Conclusión:** Mantén el mensaje `Twist` con coordenadas cartesianas. Es el estándar de la industria y te ahorrará semanas de integración.
