#!/bin/bash

# Ruta del directorio de hooks en el repositorio local
HOOKS_DIR=".git/hooks"

# Verifica si la carpeta existe
if [ ! -d "$HOOKS_DIR" ]; then
  echo "❌ No se encontró el directorio de hooks. ¿Estás en un repositorio Git?"
  exit 1
fi

# Copiar hooks personalizados
cp git-hooks/* "$HOOKS_DIR/"
chmod +x "$HOOKS_DIR/"*

echo "✅ Hooks instalados correctamente."
