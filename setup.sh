#!/bin/bash

# Script de configuración inicial para Django Single
# Este script prepara el entorno virtual y las dependencias necesarias

set -e  # Salir si hay algún error

echo "🚀 Configurando el entorno del proyecto Django..."

# Verificar si Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado. Por favor, instálalo primero."
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv .venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

# Activar entorno virtual
echo "🔌 Activando entorno virtual..."
source .venv/bin/activate

# Actualizar pip
echo "⬆️  Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias si existe requirements.txt
if [ -f "requirements.txt" ]; then
    echo "📥 Instalando dependencias..."
    pip install -r requirements.txt
    echo "✅ Dependencias instaladas"
else
    echo "⚠️  No se encontró requirements.txt. Creando uno básico..."
    echo "Django>=4.2.0" > requirements.txt
    pip install -r requirements.txt
    echo "✅ Django instalado"
fi

# Instalar Pillow si no está en requirements.txt
if ! grep -q "Pillow" requirements.txt 2>/dev/null; then
    echo "📦 Instalando Pillow..."
    pip install Pillow
fi

echo "🐍 Python: $(python --version)"



# Aplicar migraciones

echo "🗄️  Aplicando migraciones..."
python manage.py makemigrations
python manage.py migrate
echo "✅ Migraciones aplicadas"

# Función para verificar si un puerto está en uso
check_port() {
    lsof -ti:$1 > /dev/null 2>&1
}

# Intentar levantar el servidor en el puerto 8000, si está ocupado usar 8001
PORT=8000
if check_port $PORT; then
    echo "⚠️  El puerto $PORT está en uso, intentando con el puerto 8001..."
    PORT=8001
    if check_port $PORT; then
        echo "❌ Los puertos 8000 y 8001 están en uso."
        echo "   Por favor, detén los servidores en ejecución o especifica otro puerto manualmente:"
        echo "   python manage.py runserver 8002"
        exit 1
    fi
fi

# Levantar Django
echo "🚀 Levantando servidor Django en el puerto $PORT..."
python manage.py runserver $PORT