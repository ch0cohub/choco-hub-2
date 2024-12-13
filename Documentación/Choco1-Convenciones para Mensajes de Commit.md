# Convenciones para Mensajes de Commit

---

## Formato de Mensajes de Commit

### Estructura General
Los mensajes de commit deben seguir este formato:

`<tipo>(<alcance>): <mensaje>`

`[opcionalmente, cuerpo]`

- **tipo**: Indica el tipo de cambio realizado en el código (por ejemplo, una nueva funcionalidad, corrección de errores, etc.).
- **alcance**: *(Opcional)* Define la parte del proyecto que se ve afectada por el cambio (por ejemplo, el módulo o componente). Este campo se debe usar solo si es necesario.
- **mensaje**: Un breve resumen del cambio realizado.

---

## Tipos de Cambios

A continuación, se detallan los tipos de cambios que se deben utilizar. Estos tipos deben reflejar el propósito y la naturaleza del commit:

- **feat**: Nueva característica o funcionalidad.
- **fix**: Corrección de un error.
- **docs**: Actualización o adición a la documentación.
- **style**: Cambios de estilo o formato que no afectan la funcionalidad (espaciados, indentación, etc.).
- **refactor**: Modificaciones al código que mejoran su estructura, pero no cambian su comportamiento.
- **perf**: Mejoras en el rendimiento del código.
- **test**: Cambios relacionados con pruebas, como añadir o modificar pruebas.
- **chore**: Mantenimiento del proyecto o tareas no relacionadas directamente con el código (por ejemplo, actualizar dependencias).

---

## Ejemplos de Tipos de Cambios

- **`feat(auth): agregar login con Google`**  
  Se ha agregado una nueva funcionalidad de login con Google.

- **`fix(database): corregir bug en la conexión a la base de datos`**  
  Se corrigió un error en la configuración de la conexión a la base de datos.

- **`docs(readme): actualizar instrucciones de instalación`**  
  Se actualizaron las instrucciones de instalación en el README.

- **`style(ui): mejorar la disposición de los botones en la página de inicio`**  
  Cambios de estilo en la interfaz de usuario, sin impacto en la funcionalidad.

---

## Convenciones Importantes

1. **Escribir en Tiempo Presente**  
   Los mensajes de commit deben estar en tiempo presente. Utiliza frases como "agregar", "corregir", "actualizar", en lugar de "agregado", "corregido" o "actualizado".

2. **Longitud del Encabezado**  
   El encabezado del commit (la primera línea) debe ser breve, con un máximo de **50 caracteres**. Esta es la línea más importante y debe ofrecer una descripción concisa del cambio.

3. **Longitud del Cuerpo**  
   Si el commit requiere una explicación más detallada, utiliza el cuerpo. Limita cada línea del cuerpo a **72 caracteres**. El cuerpo debe describir los detalles adicionales del cambio, como el contexto, el razonamiento o las implicaciones de la modificación.

4. **Separación de Encabezado y Cuerpo**  
   Si se incluye un cuerpo en el mensaje de commit, debe haber una línea en blanco que lo separe del encabezado.

5. **Evitar Tareas No Relacionadas**  
   Evita incluir en el mismo commit cambios que no estén directamente relacionados. Si es necesario realizar múltiples tareas, crea un commit por cada una.
