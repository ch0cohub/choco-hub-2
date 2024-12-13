# Política de Gestión de Issues

## 1. Creación de Issues
- **Título Claro y Específico:** Cada issue debe tener un título claro y conciso que resuma el problema o la solicitud.
- **Descripción Detallada:** La descripción debe incluir:
  - Contexto del problema o mejora.
  - Pasos para reproducir el problema, si aplica.
- **Tipos Estandarizados:** Diferenciando entre:
  - **Bugs:** Problemas técnicos o fallos.  
  - **Features:** Nuevas funcionalidades o mejoras.  
  - **Tests:** Nuevas pruebas o cambios a pruebas.  
  - **Documentation:** Documentación del código o de la gestión de la configuración.  
  - **Tasks:** Tareas específicas relacionadas con el proyecto.
- **Etiquetas:** Asignar etiquetas de acuerdo a la naturaleza del issue (e.g., `bug`, `enhancement`, `priority: high/medium/low`).

## 2. Clasificación y Priorización de Issues
- **Asignación de Prioridad:** Asignar prioridades a los issues según su impacto en el proyecto:
  - **High:** Fundamentales para que se apruebe el proyecto.
  - **Medium:** Impacta el funcionamiento o la experiencia, pero no bloquea funcionalidades críticas.
  - **Low:** Menor impacto; pueden ser problemas estéticos o solicitudes de bajo impacto.
- **Asignación de Responsable:** Cada issue debe tener un responsable asignado tan pronto como sea posible. Esto asegura que todos sepan quién está a cargo de cada tarea.

## 3. Flujo de Trabajo del Issue
- **Estados del Issue:**
  - **Open:** Issue creado y pendiente de revisión.
  - **In Progress:** El equipo está trabajando en la solución.
  - **In Review:** El equipo está trabajando en la revisión.
  - **Closed:** El issue está completamente resuelto y cerrado.
- **Revisión de Issues:**
  - Los issues deben revisarse al menos una vez por semana para ajustar prioridades y confirmar el progreso.
  - Los responsables deben actualizar el estado y añadir comentarios relevantes en cada etapa.

## 4. Resolución y Cierre de Issues
- **Criterios de Cierre:**
  - El issue solo se cierra cuando se confirma que está completamente resuelto y verificado en el entorno de producción.
  - Un issue puede cerrarse automáticamente si el código relevante se ha fusionado en la rama principal y pasa todas las pruebas.
- **Comentarios de Cierre:** Agregar un comentario al cerrar un issue para resumir la solución, haciendo referencia a la confirmación de pruebas o cualquier otro aspecto importante.

## 5. Roles y Responsabilidades
- **Responsable de Asignación Inicial:** Quien cree el issue debe asignar etiquetas y responsables iniciales.
- **Revisión y Validación Final:** Otra persona distinta revisará y validará la issue antes de cerrarla para asegurar la calidad.
