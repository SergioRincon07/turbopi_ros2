# turbopy_teleop

Paquete de teleoperación para controlar el robot TurboPi mediante teclado.

## Características

- ✅ Control con teclas WASD
- ✅ Soporte para movimiento omnidireccional (ruedas mecanum)
- ✅ Movimiento lateral, diagonal y rotación
- ✅ Ajuste de velocidad en tiempo real
- ✅ Publicación continua en `/cmd_vel`

## Instalación

### Requisitos previos

Instalar la biblioteca `pynput` para captura de teclado:

```bash
pip install pynput
```

### Compilar el paquete

```bash
cd ~/ros2_ws/turbopi_ros2/turbopy_ros_ws
colcon build --packages-select turbopy_teleop
source install/setup.bash
```

## Uso

### Ejecutar el nodo de teleoperación

```bash
ros2 run turbopy_teleop keyboard_teleop
```

### Controles

#### Movimiento lineal
- **W** - Adelante
- **S** - Atrás  
- **A** - Lateral izquierda
- **D** - Lateral derecha

#### Rotación
- **Q** - Girar izquierda (antihorario)
- **E** - Girar derecha (horario)

#### Movimientos combinados
Puedes presionar múltiples teclas simultáneamente:
- **W + A** - Diagonal adelante-izquierda
- **W + D** - Diagonal adelante-derecha
- **W + Q** - Adelante mientras giras a la izquierda
- **A + Q** - Lateral izquierda mientras giras

#### Control de velocidad
- **+** o **=** - Aumentar velocidad
- **-** - Disminuir velocidad
- **Espacio** - Detener inmediatamente
- **ESC** - Salir del programa

## Parámetros

Puedes ajustar los parámetros al lanzar el nodo:

```bash
ros2 run turbopy_teleop keyboard_teleop --ros-args \
  -p linear_speed:=0.15 \
  -p angular_speed:=1.5 \
  -p speed_increment:=0.05
```

### Parámetros disponibles

- `linear_speed` (default: 0.1 m/s) - Velocidad lineal máxima
- `angular_speed` (default: 1.0 rad/s) - Velocidad angular máxima  
- `speed_increment` (default: 0.05) - Incremento al ajustar velocidad

## Integración con el robot

Este nodo publica mensajes `geometry_msgs/Twist` en el topic `/cmd_vel`, que son consumidos por el `turbopy_base_driver` para controlar los motores del robot.

### Ejemplo de uso completo

Terminal 1 (en el Raspberry Pi - robot):
```bash
cd ~/ros2_ws/turbopi_ros2/turbopy_rp_ws
source install/setup.bash
ros2 run turbopy_base_driver base_node
```

Terminal 2 (en tu PC o WSL):
```bash
cd ~/ros2_ws/turbopi_ros2/turbopy_ros_ws
source install/setup.bash
ros2 run turbopy_teleop keyboard_teleop
```

## Solución de problemas

### Error: "pynput no está instalado"
```bash
pip install pynput
```

### El robot no responde
1. Verifica que el `turbopy_base_driver` esté ejecutándose
2. Comprueba que ambos nodos estén en la misma red ROS2
3. Verifica el topic: `ros2 topic echo /cmd_vel`

### Teclas no responden
- Asegúrate de que la terminal donde ejecutas el nodo tenga el foco del teclado
- En algunos sistemas Linux puede requerir permisos adicionales para captura de teclado

## Arquitectura

```
┌─────────────────────┐
│ keyboard_teleop     │
│                     │
│ [WASD Keys] ──────► │
└─────────┬───────────┘
          │
          │ /cmd_vel (Twist)
          │
          ▼
┌─────────────────────┐
│ turbopy_base_driver │
│                     │
│ ──────► [Motors]    │
└─────────────────────┘
```

## Licencia

TODO: License declaration
