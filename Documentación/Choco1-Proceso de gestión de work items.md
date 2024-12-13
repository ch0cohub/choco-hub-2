# Proceso de Gestión de Work Items (WIs)

Este proceso define los estados, tipos, roles y la plantilla de Work Items (WIs) en el proyecto, asegurando que cada WI pase por un flujo organizado y estructurado hasta su finalización.

---

## 1. Estados del Work Item (WI)

Cada WI pasa por una serie de estados que representan su ciclo de vida desde la creación hasta la finalización:

- **Asignado**: El WI es creado y asignado a uno de los miembros.
- **En Progreso**: El WI está siendo trabajado activamente.
- **En Revisión**: Se revisa el WI para asegurar la calidad y cumplimiento de los requisitos.
- **Completado**: El WI ha sido revisado y aprobado, y se considera finalizado.

### Ejemplo de Ciclo de Vida de un WI:
Estado Inicial: **Nuevo** ➔ **En Progreso** ➔ **En Revisión** ➔ **Completado**.

---

## 2. Tipos de Work Items (WI)

Para organizar el trabajo y la naturaleza de cada WI, se definen los siguientes tipos:

- **Funcionalidad (feat)**: Incorporación de nuevas características en el sistema.
- **Pruebas (test)**: Creación y mejora de pruebas de unidad, integración o sistema.

---

## 3. Roles Asignados para la Gestión de WIs

Cada WI debe contar con uno o más roles asignados que cubran las responsabilidades en cada etapa:

- **Responsable de Desarrollo**: Miembro del equipo al que se asigna el WI para su desarrollo.
- **Revisor**: Persona encargada de revisar y aprobar el WI antes de su finalización.

---

## 4. Prioridad del WI

Cada WI debe ser evaluado y clasificado según su importancia y urgencia:

- **Alta**: WI que tiene un impacto significativo en el proyecto y debe ser resuelto prioritariamente.
- **Media**: WI que es importante pero no bloquea el desarrollo.
- **Baja**: WI que tiene un impacto mínimo y puede ser atendido en una fase posterior.

---

## 5. Plantilla de Work Items (WIs)

Para mantener uniformidad en la gestión de WIs, se debe usar una plantilla estándar para registrar la información de cada WI.

### Plantilla de Work Item (WI)

- **ID del WI**: Único identificador del WI.
- **Título**: Breve descripción del WI.
- **Descripción**: Explicación detallada de la tarea a realizar, incluyendo objetivos, alcance y dependencias.
- **Tipo**: Selecciona entre los tipos de WI.
- **Estado**: Estado actual del WI: *Nuevo, En Progreso, En Revisión, Bloqueado, Completado*.
- **Prioridad**: *Alta, Media o Baja*.
- **Responsable de Desarrollo**: Nombre de la persona asignada a trabajar en el WI.
- **Revisor**: Persona encargada de la revisión final del WI.
- **Comentarios/Notas**: Espacio para observaciones adicionales, actualizaciones o información de seguimiento.

---

## Ejemplos de Work Items (WIs)

### Work Item (WI): Visualize UVL
- **ID del WI**: WI-1
- **Título**: Visualize UVL
- **Descripción**: Crear una interfaz gráfica que permita la visualización de UVL en tiempo real.
- **Tipo**: Funcionalidad (feat)
- **Estado**: Asignado
- **Prioridad**: Alta
- **Responsable de Desarrollo**: Franco
- **Revisor**: Por asignar
- **Comentarios/Notas**: 

---

### Work Item (WI): Anonymize datasets
- **ID del WI**: WI-2
- **Título**: Anonymize datasets
- **Descripción**: Anonimizar datasets para que los metadatos de los autores sean anónimos. Con la opción de hacerlo público más tarde.
- **Tipo**: Funcionalidad (feat)
- **Estado**: Asignado
- **Prioridad**: Alta
- **Responsable de Desarrollo**: Ricardo
- **Revisor**: Por asignar
- **Comentarios/Notas**: 

---

### Work Item (WI): New test cases
- **ID del WI**: WI-3
- **Título**: New test cases
- **Descripción**: Crear casos de prueba adicionales para asegurar la cobertura de los nuevos módulos desarrollados.
- **Tipo**: Pruebas (test)
- **Estado**: En progreso
- **Prioridad**: Alta
- **Responsable de Desarrollo**: Antonio
- **Revisor**: Por asignar
- **Comentarios/Notas**: Enfocar casos de prueba en la validación de datos y seguridad.

---

### Work Item (WI): Rate Data sets/models
- **ID del WI**: WI-4
- **Título**: Rate Data sets/models
- **Descripción**: Desarrollar un sistema para evaluar datasets y modelos en base a diferentes criterios.
- **Tipo**: Funcionalidad (feat)
- **Estado**: Asignado
- **Prioridad**: Alta
- **Responsable de Desarrollo**: Claudio
- **Revisor**: Por asignar
- **Comentarios/Notas**: Incorporar un sistema de valoración de 5 estrellas con comentarios opcionales.

---

### Work Item (WI): UVL editor
- **ID del WI**: WI-5
- **Título**: UVL editor
- **Descripción**: Desarrollar una herramienta para editar un archivo UVL para exportarlo y/o pasarlo a un parser.
- **Tipo**: Funcionalidad (feat)
- **Estado**: Asignado
- **Prioridad**: Alta
- **Responsable de Desarrollo**: Alfonso
- **Revisor**: Por asignar
- **Comentarios/Notas**: 

---

### Work Item (WI): Search queries
- **ID del WI**: WI-6
- **Título**: Search queries
- **Descripción**: Desarrollar la posibilidad de consultar el repositorio de una manera que permita obtener un conjunto de modelos, o incluso descargarlos todos.
- **Tipo**: Funcionalidad (feat)
- **Estado**: En progreso
- **Prioridad**: Alta
- **Responsable de Desarrollo**: Pablo
- **Revisor**: Por asignar
- **Comentarios/Notas**: 

---

### Work Item (WI): View user profile
- **ID del WI**: WI-7
- **Título**: View user profile
- **Descripción**: Como usuario, quiero poder hacer clic en el nombre o apellido de un usuario (que aparece en el perfil de un dataset bajo la etiqueta "Uploaded by") y ser dirigido a una página donde pueda ver todos los datasets que ese usuario ha subido a la plataforma.
- **Tipo**: Funcionalidad (feat)
- **Estado**: En progreso
- **Prioridad**: Baja
- **Responsable de Desarrollo**: Franco
- **Revisor**: Por asignar
- **Comentarios/Notas**: 
