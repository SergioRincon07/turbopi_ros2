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

# Verificar que estamos en el directorio correcto
WORKSPACE_DIR="$HOME/ros2_ws/ros2_ws_wsl2_RasPI"

if [ ! -d "$WORKSPACE_DIR" ]; then
    echo -e "${RED}✗ Error: Workspace no encontrado en $WORKSPACE_DIR${NC}"
    exit 1
fi

cd "$WORKSPACE_DIR"
echo -e "${GREEN}📁 Directorio de trabajo: $PWD${NC}"
echo ""

# Verificar que existe el directorio src
if [ ! -d "src" ]; then
    echo -e "${RED}✗ Error: No se encontró directorio 'src'${NC}"
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
echo -e "${BLUE}🔨 Compilando paquetes...${NC}"
colcon build --packages-select wsl_raspi_comm wsl_raspi_comm_msgs --symlink-install

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
