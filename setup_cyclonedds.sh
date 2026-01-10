#!/bin/bash
# Configuración de variables de entorno para comunicación multi-dispositivo con CycloneDDS
# Adaptado para WSL2 y Raspberry Pi

# Usar CycloneDDS (recomendado para multi-máquina)
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Detectar si estamos en WSL
if grep -qi "microsoft" /proc/version 2>/dev/null \
   || [ -n "$WSL_INTEROP" ] \
   || [ -n "$WSL_DISTRO_NAME" ]; then
    ENTORNO="WSL"
    DDS_FILE="cyclonedds_WSL.xml"
else
    ENTORNO="Raspberry Pi"
    DDS_FILE="cyclonedds_RasPI.xml"
fi

# Carpeta única de configuración
CONFIG_DIR="$HOME/ros2_ws/ros2_ws_wsl2_RasPI/config"
CONFIG_FILE="$CONFIG_DIR/$DDS_FILE"

# Exportar configuración CycloneDDS
if [ -f "$CONFIG_FILE" ]; then
    export CYCLONEDDS_URI="file://$CONFIG_FILE"
    echo "✅ CycloneDDS configurado para $ENTORNO"
    echo "   Archivo: $CONFIG_FILE"
else
    echo "❌ ERROR: No se encontró $DDS_FILE"
    echo "   Ruta esperada: $CONFIG_FILE"
    echo "   CycloneDDS usará configuración por defecto"
fi

# Dominio ROS2 (debe ser el mismo en todos los dispositivos)
export ROS_DOMAIN_ID=10

# Configuración de descubrimiento automático (reemplaza ROS_LOCALHOST_ONLY)
export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET

# Opcional: para debugging de descubrimiento DDS
# Descomentar la siguiente línea para habilitar trazas detalladas
# export CYCLONEDDS_TRACE=info

echo "=========================================="
echo "  Configuración CycloneDDS cargada"
echo "=========================================="
echo "  RMW: $RMW_IMPLEMENTATION"
echo "  Dominio: $ROS_DOMAIN_ID"
echo "  Config: ${CYCLONEDDS_URI:-'default'}"
echo "  Entorno detectado: ${ENTORNO:-'desconocido'}"
echo "  Discovery range: $ROS_AUTOMATIC_DISCOVERY_RANGE"
echo "=========================================="
echo ""
echo "✓ Listo para comunicación multi-dispositivo"
echo ""
