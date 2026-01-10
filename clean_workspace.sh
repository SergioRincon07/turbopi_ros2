#!/bin/bash
# Script para limpiar el workspace ROS2

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=========================================="
echo "  Limpieza de Workspace ROS2"
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

# Mostrar qué se va a eliminar
echo -e "${YELLOW}Se eliminarán los siguientes directorios:${NC}"
echo ""

if [ -d "build" ]; then
    SIZE_BUILD=$(du -sh build 2>/dev/null | cut -f1)
    echo "  • build/ ($SIZE_BUILD)"
fi

if [ -d "install" ]; then
    SIZE_INSTALL=$(du -sh install 2>/dev/null | cut -f1)
    echo "  • install/ ($SIZE_INSTALL)"
fi

if [ -d "log" ]; then
    SIZE_LOG=$(du -sh log 2>/dev/null | cut -f1)
    echo "  • log/ ($SIZE_LOG)"
fi

echo ""

# Confirmación
echo -e "${RED}⚠️  ¿Estás seguro de que deseas continuar? (y/N)${NC}"
read -n 1 RESPONSE
echo ""

if [[ ! $RESPONSE =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Operación cancelada${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}🧹 Limpiando...${NC}"

# Eliminar directorios
CLEANED=false

if [ -d "build" ]; then
    rm -rf build
    echo -e "${GREEN}  ✓ Eliminado: build/${NC}"
    CLEANED=true
fi

if [ -d "install" ]; then
    rm -rf install
    echo -e "${GREEN}  ✓ Eliminado: install/${NC}"
    CLEANED=true
fi

if [ -d "log" ]; then
    rm -rf log
    echo -e "${GREEN}  ✓ Eliminado: log/${NC}"
    CLEANED=true
fi

echo ""

if [ "$CLEANED" = true ]; then
    echo -e "${GREEN}=========================================="
    echo "  ✓ Limpieza completada"
    echo -e "==========================================${NC}"
    echo ""
    echo -e "${YELLOW}💡 Para recompilar el workspace ejecuta:${NC}"
    echo "  ./build_workspace.sh"
    echo ""
else
    echo -e "${YELLOW}=========================================="
    echo "  ℹ️  No había nada que limpiar"
    echo -e "==========================================${NC}"
    echo ""
fi
