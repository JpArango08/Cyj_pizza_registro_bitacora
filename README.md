# Cyj_pizza_registro_bitacora

# Bitácora de Cloro Residual y pH --- Cyj Pizza

## 1. Propósito

Aplicación para registrar y consultar mediciones de cloro residual y pH
asociadas a Cyj Pizza. La aplicación web presenta los registros
guardados en Supabase. Existe además un flujo de n8n programado para
crear registros automáticos.

> **Advertencia sobre los datos automáticos actuales:** el flujo de n8n
> descrito aquí genera valores aleatorios simulados dentro de los rangos
> configurados y asigna estados de cumplimiento. Esos registros **no son
> mediciones reales del agua** y no deben usarse como evidencia de
> cumplimiento sanitario. Para uso operativo real, la automatización
> debe recibir datos de un instrumento o de una persona que haya medido
> el agua, y los estados deben calcularse a partir de esos datos.

## 2. Arquitectura general

``` text
Usuario
  |
  v
Aplicación web Flask / archivos estáticos
  |
  v
Supabase (PostgreSQL)
  ^
  |
n8n (flujo programado de registros automáticos)
```

-   **Repositorio de código:**
    https://github.com/JpArango08/Cyj_pizza_registro_bitacora
-   **Rama principal:** `main`
-   **Proyecto local en Windows:**
    `C:\Users\Jp\Downloads\Registro_cyj_pizza\bitacora_cloro_ph`
-   **Aplicación desplegada:** Vercel. La ruta de aplicación que se
    verificó fue `/api/`; la ruta raíz `/` llegó a mostrar `Not Found`.
    No cambiar el enrutamiento sin probar el despliegue.
-   **Base de datos:** Supabase, PostgreSQL.
-   **Proyecto Supabase ref:** `nzyggbftezxnvlfwzcpz`
-   **URL del proyecto Supabase:**
    `https://nzyggbftezxnvlfwzcpz.supabase.co`
-   **Región Supabase:** `us-west-2`
-   **Zona horaria del flujo n8n:** `America/Bogota`
-   **Flujo n8n:** `registros_cloro_ph_cyj_pizza`
-   **Horario previsto:** todos los días a las 12:00 p. m. hora de
    Colombia. Confirmar en n8n que el flujo esté activo y que el
    Schedule Trigger conserve esta configuración.

No se guardan contraseñas, tokens ni claves privadas en este README. No
pegues secretos en tickets, capturas ni conversaciones.

## 3. Estructura del repositorio

Se han identificado los siguientes archivos en el proyecto:

``` text
bitacora_cloro_ph/
├── app/
│   ├── __init__.py          # Inicialización de la aplicación Flask y lógica/rutas del servidor
│   ├── static/
│   │   └── js/
│   │       └── app.js       # JavaScript del frontend asociado a app/
│   └── templates/
│       └── index.html       # Plantilla HTML de la interfaz
├── public/
│   ├── css/
│   │   └── styles.css      # Estilos publicados
│   └── js/
│       └── app.js          # JavaScript publicado
├── index.py                # Punto de entrada usado por el despliegue serverless
└── run.py                  # Punto de entrada para ejecutar localmente
```

La estructura anterior es una guía basada en los archivos identificados
durante el trabajo; puede haber otros archivos. Para confirmar el estado
actual, revisar el repositorio y no asumir que las dos copias de
`app.js` son idénticas. Antes de editar, buscar cuál de ellas carga
realmente cada página.

También se identificó una copia local de respaldo `app/__init__.py.bak`
que estaba sin seguimiento de Git. No es parte necesaria del despliegue;
no subirla sin revisar su contenido.

## 4. Tecnologías y alojamiento

### Aplicación web

-   Python y Flask.
-   HTML, CSS y JavaScript.
-   Vercel para el despliegue.
-   GitHub como repositorio de código.

### Persistencia

-   Supabase con PostgreSQL.
-   Tabla principal: `public.measurements`.

### Automatización

-   n8n autohospedado, configurado para ejecutar un flujo diario.
-   El flujo es independiente de Vercel: el despliegue de la web no
    activa ni reemplaza el flujo n8n.

## 5. Variables de entorno y secretos

En Vercel se configuraron estas variables para los entornos
**Production** y **Preview**:

-   `SUPABASE_URL`
-   `SUPABASE_KEY`

La clave configurada para la aplicación web se identificó como una clave
pública/anon/publishable, no como una `service_role`. Mantener la clave
privilegiada fuera del navegador y del repositorio.

En n8n existe una credencial de Supabase configurada para el nodo que
inserta registros. No copiar el valor de la credencial en el README ni
compartirlo. Si una clave se expone accidentalmente, rotarla en el
proveedor y actualizar las credenciales/variables correspondientes.

### Reglas de seguridad

-   No subir `.env` ni archivos con claves al repositorio.
-   Confirmar que `.env` está excluido por `.gitignore`.
-   Nunca usar una clave `service_role` en JavaScript del navegador.
-   Revisar las políticas RLS de Supabase antes de cambiar permisos.
-   Compartir errores y capturas ocultando tokens, claves, cookies y
    datos sensibles.

## 6. Tabla `public.measurements`

La tabla guarda mediciones y campos de estado. Se han identificado estos
campos relevantes:

-   `id`: identificador UUID.
-   `measured_at`: fecha/hora de la medición.
-   `created_at`: fecha de creación, si aplica según el esquema.
-   `chlorine_value`: valor numérico de cloro.
-   `ph_value`: valor numérico de pH.
-   `chlorine_status`: estado calculado del cloro.
-   `ph_status`: estado calculado del pH.
-   `overall_status`: estado general.
-   `record_type`: distingue registros `manual` y `automatic`.
-   `automation_date`: fecha local usada para controlar los registros
    automáticos.

Confirmar el esquema real en Supabase antes de migrar o modificar
columnas.

### Valores aceptados por las restricciones CHECK

`chlorine_status` y `ph_status` aceptan:

-   `BAJO`
-   `DENTRO DEL RANGO`
-   `ALTO`
-   `INVÁLIDO`
-   `SIN DATOS`

`overall_status` acepta:

-   `CUMPLE`
-   `NO CUMPLE`
-   `INVÁLIDO`
-   `SIN DATOS`

Los textos deben coincidir exactamente, incluidos espacios y tildes. Por
ejemplo, `CUMPLE` **no** es válido para `chlorine_status` o `ph_status`.

### Rangos configurados en la aplicación

-   Cloro: de `0.3` a `2.0` mg/L.
-   pH: de `6.5` a `9.0`.

Verificar el código actual antes de cambiar estos límites; pueden
depender de los requisitos sanitarios aplicables y no deben considerarse
asesoría normativa por sí solos.

### Protección contra registros automáticos duplicados

Existe una restricción/índice único llamado:

`measurements_one_automatic_per_day_uq`

Está destinado a limitar los registros `automatic` a uno por fecha. La
lógica de fecha usa `America/Bogota` y `automation_date`. Un error
`duplicate key value violates unique constraint "measurements_one_automatic_per_day_uq"`
suele indicar que ya existe un registro automático para esa fecha. No
desactivar la restricción para evitar el error.

Consulta de solo lectura para inspeccionar los registros automáticos:

``` sql
SELECT
    id,
    measured_at,
    record_type,
    automation_date,
    overall_status
FROM public.measurements
WHERE record_type = 'automatic'
ORDER BY measured_at DESC
LIMIT 20;
```

Consulta para contar los registros:

``` sql
SELECT COUNT(*) AS registros_totales
FROM public.measurements;
```

Consulta para comprobar las restricciones CHECK:

``` sql
SELECT
    conname AS restriccion,
    pg_get_constraintdef(oid) AS definicion
FROM pg_constraint
WHERE conrelid = 'public.measurements'::regclass
  AND contype = 'c';
```

**Operaciones destructivas:** `DELETE FROM public.measurements;` elimina
todos los registros. Solo ejecutarlo si se solicita explícitamente, se
confirma el alcance y se acepta perder el historial. Vaciar la tabla no
es un paso normal para resolver errores.

## 7. Flujo n8n

Nombre del flujo: `registros_cloro_ph_cyj_pizza`.

Cadena prevista:

1.  **Schedule Trigger:** cada día a las 12:00 p. m.
2.  **Code:** genera los valores y campos de estado.
3.  **Supabase --- Create a row:** inserta en `public.measurements`.

La zona horaria del flujo se configuró como `America/Bogota`.

El nodo Code se modificó para producir: - `chlorine_value` dentro del
rango configurado de cloro. - `ph_value` dentro del rango configurado de
pH. - `measured_at` como fecha/hora ISO. - `record_type: "automatic"`. -
`chlorine_status: "DENTRO DEL RANGO"`. -
`ph_status: "DENTRO DEL RANGO"`. - `overall_status: "CUMPLE"`. -
`simulation: true` como dato auxiliar del flujo; no debe mapearse a una
columna si esa columna no existe.

Estos valores se generan aleatoriamente y, por tanto, son **simulados**.
No equivalen a medir cloro o pH. No afirmar cumplimiento real basándose
en ellos.

### Recomendaciones para probar n8n

-   Ejecutar el nodo Code por separado para validar su salida, sin
    escribir en la base.
-   Antes de ejecutar Supabase, comprobar si ya existe un registro
    automático en la fecha local actual.
-   Ejecutar el nodo de inserción como máximo una vez por fecha cuando
    la restricción diaria está activa.
-   Si la inserción devuelve un error, leer el mensaje exacto antes de
    cambiar el esquema.
-   Después de una prueba correcta, activar y guardar el flujo;
    confirmar el indicador de estado activo.
-   No modificar la zona horaria global de n8n si basta con la
    configuración de este flujo.

## 8. Desarrollo local

En Windows, la carpeta del proyecto indicada anteriormente está dentro
de `Registro_cyj_pizza`. Durante la configuración se utilizó el entorno
virtual:

`C:\Users\Jp\Downloads\Registro_cyj_pizza\.venv`

Desde una terminal de Windows:

``` bat
cd C:\Users\Jp\Downloads\Registro_cyj_pizza
.venv\Scripts\activate
cd bitacora_cloro_ph
python run.py
```

Si el entorno virtual no existe, crear uno e instalar las dependencias
declaradas por el proyecto. Antes de ejecutar, comprobar que las
variables de entorno necesarias están configuradas de forma segura. No
inventar ni copiar valores de producción para resolver errores locales.

## 9. Flujo de trabajo Git y despliegue

Repositorio: `https://github.com/JpArango08/Cyj_pizza_registro_bitacora`

Rama principal: `main`.

Antes de cambiar código:

``` bash
git status
git pull
```

Después de editar, revisar los cambios:

``` bash
git diff
git status
```

Tras probar localmente y confirmar que no se han incluido secretos,
hacer commit y push siguiendo el flujo normal del repositorio. Vercel
despliega a partir de la configuración conectada al repositorio;
confirmar el resultado del último deployment en Vercel en vez de asumir
que un push ya se desplegó correctamente.

Un commit previamente mencionado durante el trabajo fue `9331681`. El
estado de la rama puede haber cambiado desde entonces.

## 10. Diagnóstico de errores frecuentes

### A. `violates check constraint "measurements_chlorine_status_check"`

**Causa habitual:** `chlorine_status` contiene un valor no permitido,
como `CUMPLE`.

**Comprobar:** las restricciones con la consulta de la sección 6. Usar
`DENTRO DEL RANGO`, `BAJO`, `ALTO`, `INVÁLIDO` o `SIN DATOS` según
corresponda.

### B. `violates check constraint "measurements_ph_status_check"`

**Causa habitual:** `ph_status` no coincide exactamente con uno de los
valores permitidos.

**Comprobar:** igual que el estado de cloro. No usar `CUMPLE` en
`ph_status`.

### C. `violates check constraint "measurements_overall_status_check"`

**Causa habitual:** `overall_status` no coincide con `CUMPLE`,
`NO CUMPLE`, `INVÁLIDO` o `SIN DATOS`.

### D. `duplicate key value violates unique constraint "measurements_one_automatic_per_day_uq"`

**Causa habitual:** ya existe un registro automático para la fecha local
actual.

**Acción:** consultar `record_type` y `automation_date`. No borrar
registros ni quitar la restricción como solución rutinaria. Si el flujo
está reintentando, corregir la lógica para evitar otro intento de
inserción en esa fecha.

### E. El registro existe en Supabase pero no aparece en Vercel

1.  Actualizar la página y revisar filtros de fecha/tipo.
2.  Confirmar que la consulta de la aplicación lee de
    `public.measurements`.
3.  Revisar la consola del navegador y los logs de Vercel.
4.  Revisar variables `SUPABASE_URL` y `SUPABASE_KEY` en el entorno
    correcto.
5.  Revisar RLS y permisos de lectura; no desactivar RLS
    indiscriminadamente.
6.  Confirmar que el frontend y la ruta de API que se está usando son
    los esperados.

### F. Vercel muestra `Not Found` en la ruta raíz

La ruta raíz `/` llegó a mostrar `Not Found` durante la configuración,
mientras que `/api/` funcionaba. Probar primero la ruta conocida `/api/`
y revisar el enrutamiento/deployment antes de cambiar archivos. No
asumir que es un fallo de la base de datos.

### G. El flujo n8n no corre a la hora prevista

1.  Confirmar que el workflow está activo.
2.  Confirmar Schedule Trigger: diario, 12:00, minuto 0.
3.  Confirmar la zona horaria `America/Bogota`.
4.  Revisar el historial de ejecuciones de n8n.
5.  Revisar credencial Supabase y error del nodo.
6.  Verificar que el servidor/instancia autohospedada de n8n esté
    funcionando.

### H. Error de conexión o autenticación con Supabase

-   Confirmar host/URL y credencial configurados, sin copiar secretos a
    los logs compartidos.
-   Distinguir la clave pública de la clave privilegiada.
-   Revisar logs del servicio y permisos RLS.
-   Rotar cualquier secreto que se haya expuesto.

## 11. Lista de comprobación para investigar un bug

Al reportar un problema, recopilar:

1.  **Dónde ocurre:** local, Vercel, Supabase o n8n.
2.  **Qué se esperaba** y qué ocurrió realmente.
3.  **Pasos exactos para reproducirlo.**
4.  **Mensaje de error completo**, quitando secretos y datos personales.
5.  **Hora aproximada y zona horaria** del fallo.
6.  **Si afecta a registros manuales, automáticos o ambos.**
7.  **Último cambio realizado:** archivo, configuración o nodo.
8.  **Evidencia:** captura sin claves, salida de consulta de solo
    lectura o logs relevantes.
9.  **Estado actual:** si el registro existe en Supabase y si aparece en
    Vercel.

No ejecutar `DELETE`, `TRUNCATE`, cambios de restricciones ni cambios de
RLS como primer paso de diagnóstico. Primero recopilar evidencia y
reproducir el error de forma segura.

## 12. Pendientes y datos que conviene mantener actualizados

Actualizar este README cuando cambien: - La estructura de archivos. - El
nombre o configuración del deployment de Vercel. - Las variables de
entorno (documentar solo los nombres, nunca sus valores). - Las
columnas, índices, triggers o políticas de Supabase. - Los nodos,
horario o zona horaria de n8n. - Los rangos de cloro/pH y la lógica de
cálculo de estados. - Los procedimientos de despliegue.

No se documentan aquí el nombre de usuario de la cuenta, contraseñas,
claves API, tokens ni credenciales de n8n. Guardarlos únicamente en los
gestores de secretos correspondientes.
