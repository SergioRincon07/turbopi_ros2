#!/bin/bash
# Script para construir el workspace ROS2

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo "  Construyendo Workspace ROS2"
echo -e "==========================================${NC}"
echo ""

# Directorio del repo (turbopi_ros2)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$SCRIPT_DIR"

ROS_WS_DIR="$REPO_DIR/turbopy_ros_ws"
RP_WS_DIR="$REPO_DIR/turbopy_rp_ws"

# Seleccionar workspace según ROS_DISTRO (jazzy -> PC, humble -> Raspberry Pi)
case "${ROS_DISTRO:-}" in
    jazzy)
        WORKSPACE_DIR="$ROS_WS_DIR"
        TARGET_NAME="turbopy_ros_ws (PC/Jazzy)"
        ;;
    humble)
        WORKSPACE_DIR="$RP_WS_DIR"
        TARGET_NAME="turbopy_rp_ws (Raspberry Pi/Humble)"
        ;;
    *)
        # Fallback: si no hay ROS_DISTRO, priorizar turbopy_ros_ws si existe
        if [ -d "$ROS_WS_DIR" ]; then
            WORKSPACE_DIR="$ROS_WS_DIR"
            TARGET_NAME="turbopy_ros_ws (por defecto)"
        elif [ -d "$RP_WS_DIR" ]; then
            WORKSPACE_DIR="$RP_WS_DIR"
            TARGET_NAME="turbopy_rp_ws (por defecto)"
        else
            echo -e "${RED}✗ Error: No se encontraron workspaces turbopy_ros_ws ni turbopy_rp_ws en $REPO_DIR${NC}"
            exit 1
        fi
        ;;
esac

if [ ! -d "$WORKSPACE_DIR" ]; then
    echo -e "${RED}✗ Error: Workspace no encontrado en $WORKSPACE_DIR${NC}"
    exit 1
fi

cd "$WORKSPACE_DIR"
echo -e "${GREEN}📁 Directorio de trabajo: $PWD${NC}"
echo -e "${GREEN}📦 Workspace seleccionado: $TARGET_NAME (ROS_DISTRO=${ROS_DISTRO:-'no establecido'})${NC}"
echo ""

# Verificar que existe el directorio src
if [ ! -d "src" ]; then
    echo -e "${RED}✗ Error: No se encontró directorio 'src' en $WORKSPACE_DIR${NC}"
    exit 1
fi

# Preguntar si se desea limpiar antes de compilar
echo -e "${YELLOW}¿Deseas limpiar antes de compilar? (y/N)${NC}"
read -t 5 -n 1 CLEAN_RESPONSE
echo ""

if [[ $CLEAN_RESPONSE =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🧹 Limpiando workspace...${NC}"
    rm -rf build install log
    echo -e "${GREEN}✓ Limpieza completada${NC}"
    echo ""
fi

# Compilar
echo -e "${BLUE}🔨 Compilando paquetes con colcon...${NC}"
colcon build --symlink-install

# Verificar resultado
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "  ✓ Compilación exitosa"
    echo -e "==========================================${NC}"
    echo ""
    echo -e "${YELLOW}📝 Para usar el workspace ejecuta:${NC}"
    echo ""
    echo "  source install/setup.bash"
    echo ""
    echo -e "${YELLOW}💡 O agrégalo a tu ~/.bashrc:${NC}"
    echo ""
    echo "  echo 'source $WORKSPACE_DIR/install/setup.bash' >> ~/.bashrc"
    echo ""
    echo -e "${YELLOW}🔧 Para configurar CycloneDDS:${NC}"
    echo ""
    echo "  source setup_cyclonedds.sh"
    echo ""
    echo "  # O usando el script helper:"
    echo "  source setup_rmw.sh"
    echo ""
else
    echo ""
    echo -e "${RED}=========================================="
    echo "  ✗ Error en la compilación"
    echo -e "==========================================${NC}"
    echo ""
    echo -e "${YELLOW}💡 Sugerencias:${NC}"
    echo "  1. Verifica los errores en el log"
    echo "  2. Asegúrate de tener todas las dependencias instaladas"
    echo "  3. Intenta limpiar y recompilar: ./clean_workspace.sh && ./build_workspace.sh"
    echo ""
    exit 1
fi
