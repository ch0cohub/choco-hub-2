# Gestión de Ramas y Versionado

## 1. Estrategia de Gestión de Ramas

### Ramas Principales

#### Rama `main`
- Contiene el código en su versión de producción.
- Solo se fusionan cambios completamente probados y revisados.
- Debe estar en un estado estable en todo momento.
- Las versiones liberadas (releases) se etiquetarán aquí con un número de versión semántica.
- Es la rama principal de desarrollo.
- Integra los cambios de todas las ramas de Work Items (WI).

### Ramas de Trabajo por Work Item (WI)

#### Rama por Work Item (WI)
- Para cada Work Item (WI), se crea una rama específica, nombrada a partir del WI con el que se esté trabajando.
- Estas ramas permiten que cada WI se desarrolle de forma aislada y facilite su revisión y pruebas.
- Las ramas de WI se crean a partir de `main` y se fusionan de vuelta a `main` una vez que el trabajo ha sido revisado y aprobado.

### Flujo de Trabajo

#### Crear una rama por WI
1. Al iniciar un nuevo WI, se crea una rama basada en `main` para ese WI.
2. Una vez completada la tarea, se realiza un pull request (PR) hacia `main`.

#### Revisión y Fusión a `main`
- Cada PR hacia `main` debe ser revisado y aprobado antes de la fusión.
- Al aprobar el PR, la rama del WI se fusiona en `main` y se elimina.

---

## 2. Estrategia de Versionado

El sistema de versionado se basa en el esquema de **Versionado Semántico (MAJOR.MINOR.PATCH)**, donde:

- **MAJOR**: Cambia cuando hay modificaciones importantes e incompatibles en el proyecto.
- **MINOR**: Cambia cuando se añaden nuevas funcionalidades de manera compatible con versiones anteriores.
- **PATCH**: Cambia cuando se realizan correcciones de errores y ajustes menores compatibles con versiones anteriores.

### Ejemplos de Versionado
- `v1.0.0`: Primera versión estable de producción.
- `v1.1.0`: Versión con nuevas características, manteniendo la compatibilidad.
- `v1.1.1`: Versión con correcciones menores de errores.

### Flujo de Versionado

#### Liberación en Producción
- Al fusionar en `main` para una nueva versión, se asigna una etiqueta de versión (`vX.Y.Z`).
- El incremento en la versión dependerá de los cambios realizados:
  - Incremento de **MAJOR** para cambios grandes e incompatibles.
  - Incremento de **MINOR** para nuevas funcionalidades compatibles.
  - Incremento de **PATCH** para correcciones de errores menores.

#### Etiquetas en el Repositorio
- Al momento de la fusión en `main`, se crea una etiqueta con la versión en formato `vX.Y.Z`.
- Estas etiquetas sirven para rastrear la historia de las versiones en el repositorio y facilitar la identificación de cambios.
