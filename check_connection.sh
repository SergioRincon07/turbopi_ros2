#!/bin/bash
# Script de diagnóstico para comunicación multi-dispositivo ROS2
# Compatible con WSL2 y Raspberry Pi

echo "=========================================="
echo "  Diagnóstico de Comunicación ROS2"
echo "=========================================="
echo ""

# 0. Setup_cyclonedds ROS2
if [ -f "$HOME/ros2_ws/ros2_ws_wsl2_RasPI/setup_cyclonedds.sh" ]; then
    source "$HOME/ros2_ws/ros2_ws_wsl2_RasPI/setup_cyclonedds.sh"
    echo "   ✓ Configuración CycloneDDS cargada"
else
    echo "   ⚠️  No se encontró setup_cyclonedds.sh"
fi
echo ""

# 1. Configuración ROS2
echo "1️⃣  Configuración ROS2:"
echo "   ROS_DISTRO: ${ROS_DISTRO:-'No configurado'}"
echo "   ROS_DOMAIN_ID: ${ROS_DOMAIN_ID:-'0 (default)'}"
echo "   ROS_LOCALHOST_ONLY: ${ROS_LOCALHOST_ONLY:-'No configurado'}"
echo "   RMW_IMPLEMENTATION: ${RMW_IMPLEMENTATION:-'default (FastRTPS)'}"
if [ -n "$CYCLONEDDS_URI" ]; then
    echo "   CYCLONEDDS_URI: $CYCLONEDDS_URI"
fi
echo ""

# 2. Interfaces de red
echo "2️⃣  Interfaces de red activas:"
if command -v ip &> /dev/null; then
    ip addr show | grep -E "^[0-9]|inet " | grep -v "127.0.0.1" | sed 's/^/   /'
else
    ifconfig | grep -E "inet " | grep -v "127.0.0.1" | sed 's/^/   /'
fi
echo ""

# 3. Conectividad básica
echo "3️⃣  Verificación de conectividad:"
echo -n "   Ping a gateway: "
GATEWAY=$(ip route | grep default | awk '{print $3}' | head -1)
if [ -n "$GATEWAY" ]; then
    if ping -c 1 -W 1 $GATEWAY &> /dev/null; then
        echo "✓ OK ($GATEWAY)"
    else
        echo "✗ FALLO ($GATEWAY)"
    fi
else
    echo "⚠️  No se encontró gateway"
fi
echo ""

# 4. Nodos ROS2 activos
echo "4️⃣  Nodos ROS2 activos:"
if command -v ros2 &> /dev/null; then
    NODES=$(ros2 node list 2>/dev/null)
    if [ -n "$NODES" ]; then
        echo "$NODES" | sed 's/^/   /'
    else
        echo "   (No hay nodos activos)"
    fi
else
    echo "   ⚠️  Comando ros2 no disponible"
fi
echo ""

# 5. Topics disponibles
echo "5️⃣  Topics disponibles:"
if command -v ros2 &> /dev/null; then
    TOPICS=$(ros2 topic list 2>/dev/null)
    if [ -n "$TOPICS" ]; then
        echo "$TOPICS" | sed 's/^/   /'
        echo ""
        echo "   Total: $(echo "$TOPICS" | wc -l) topics"
    else
        echo "   (No hay topics disponibles)"
    fi
else
    echo "   ⚠️  Comando ros2 no disponible"
fi
echo ""

# 6. Servicios disponibles
echo "6️⃣  Servicios disponibles:"
if command -v ros2 &> /dev/null; then
    SERVICES=$(ros2 service list 2>/dev/null)
    if [ -n "$SERVICES" ]; then
        SERVICE_COUNT=$(echo "$SERVICES" | wc -l)
        echo "   Total: $SERVICE_COUNT servicios"
        # Mostrar solo los primeros 10
        echo "$SERVICES" | head -10 | sed 's/^/   /'
        if [ $SERVICE_COUNT -gt 10 ]; then
            echo "   ... (y $((SERVICE_COUNT - 10)) más)"
        fi
    else
        echo "   (No hay servicios disponibles)"
    fi
else
    echo "   ⚠️  Comando ros2 no disponible"
fi
echo ""

# 7. Información del daemon
echo "7️⃣  Estado del daemon ROS2:"
if command -v ros2 &> /dev/null; then
    ros2 daemon stop &> /dev/null
    sleep 1
    ros2 daemon start &> /dev/null
    if [ $? -eq 0 ]; then
        echo "   ✓ Daemon reiniciado correctamente"
    else
        echo "   ⚠️  Problema al reiniciar daemon"
    fi
else
    echo "   ⚠️  Comando ros2 no disponible"
fi
echo ""

# 8. Diagnóstico de red DDS
echo "8️⃣  Diagnóstico DDS (esto puede tardar unos segundos):"
if command -v ros2 &> /dev/null; then
    echo "   Ejecutando ros2 doctor..."
    DOCTOR_OUTPUT=$(ros2 doctor --report 2>/dev/null | grep -A 25 "NETWORK CONFIGURATION" || echo "No disponible")
    echo "$DOCTOR_OUTPUT" | sed 's/^/   /'
else
    echo "   ⚠️  Comando ros2 no disponible"
fi
echo ""

echo "=========================================="
echo "  Fin del diagnóstico"
echo "=========================================="
echo ""
echo "💡 Consejos:"
echo "   • Si no ves nodos de otros dispositivos, verifica el ROS_DOMAIN_ID"
echo "   • Si hay problemas de red, revisa el firewall"
echo "   • Para más detalles: ros2 doctor --report"
echo ""
