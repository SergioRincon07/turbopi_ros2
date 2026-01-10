# TurboPy – Interfaz ROS

Esta es la interfaz oficial entre el PC y la Raspberry Pi.

---

## Movimiento

| Topic | Tipo | Dirección |
|------|------|-----------|
| /cmd_vel | geometry_msgs/Twist | PC → Robot |
| /odom | nav_msgs/Odometry | Robot → PC |
| /joint_states | sensor_msgs/JointState | Robot → PC |

---

## Cámara

| Topic | Tipo |
|------|------|
| /camera/image_raw | sensor_msgs/Image |

---

## LEDs

| Topic | Tipo |
|------|------|
| /leds_cmd | std_msgs/String |

---

## Buzzer

| Topic | Tipo |
|------|------|
| /buzzer_cmd | std_msgs/Bool |

---

## Sensores

| Topic | Tipo |
|------|------|
| /battery | sensor_msgs/BatteryState |
| /distance | sensor_msgs/Range |
