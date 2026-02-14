# Instrucciones para Agentes - Django Single Project

## Descripción del Proyecto

Este es un proyecto Django básico con una aplicación de dashboard. El proyecto está configurado para ser fácilmente extensible y seguir las mejores prácticas de Django.

## Estructura del Proyecto

```
django-single/
├── config/              # Configuración principal del proyecto Django
│   ├── settings.py      # Configuración del proyecto
│   ├── urls.py          # URLs principales
│   ├── wsgi.py          # Configuración WSGI
│   └── asgi.py          # Configuración ASGI
├── dashboard/           # Aplicación principal del dashboard
│   ├── models.py        # Modelos de la aplicación
│   ├── views.py         # Vistas de la aplicación
│   ├── urls.py          # URLs de la aplicación
│   ├── admin.py         # Configuración del admin
│   └── templates/       # Plantillas HTML
│       └── dashboard/
│           └── index.html
├── manage.py            # Script de gestión de Django
├── requirements.txt     # Dependencias del proyecto
├── setup.sh             # Script de configuración inicial
└── .gitignore           # Archivos ignorados por Git
```

## Configuración Inicial

1. **Ejecutar el script de setup:**
   ```bash
   ./setup.sh
   ```
   Este script crea el entorno virtual, instala las dependencias y prepara el proyecto.

2. **Activar el entorno virtual:**
   ```bash
   source .venv/bin/activate
   ```

3. **Aplicar migraciones:**
   ```bash
   python manage.py migrate
   ```

4. **Crear superusuario (opcional):**
   ```bash
   python manage.py createsuperuser
   ```

5. **Ejecutar el servidor de desarrollo:**
   ```bash
   python manage.py runserver
   ```

## Convenciones y Estándares

- **Nombres de archivos:** Usar snake_case para archivos Python
- **Nombres de clases:** Usar PascalCase para clases
- **Nombres de funciones:** Usar snake_case para funciones
- **Plantillas:** Ubicadas en `app_name/templates/app_name/`
- **URLs:** Cada app tiene su propio archivo `urls.py` incluido en `config/urls.py`

## Añadir Nuevas Funcionalidades

### Crear una Nueva App

```bash
python manage.py startapp nombre_app
```

Luego:
1. Agregar la app a `INSTALLED_APPS` en `config/settings.py`
2. Crear `urls.py` en la nueva app
3. Incluir las URLs en `config/urls.py`

### Añadir Modelos

1. Definir modelos en `app_name/models.py`
2. Crear y aplicar migraciones:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Añadir Vistas

- Usar vistas basadas en clases cuando sea posible
- Las vistas basadas en funciones también son válidas
- Mantener la lógica de negocio separada de las vistas

## Base de Datos

- Por defecto usa SQLite (`db.sqlite3`)
- Para producción, cambiar a PostgreSQL o MySQL en `config/settings.py`

## Estilos y Frontend

- El dashboard actual usa CSS inline para simplicidad
- Para proyectos más grandes, considerar usar un framework CSS (Bootstrap, Tailwind) o un sistema de gestión de assets

## Seguridad

- **IMPORTANTE:** Cambiar `SECRET_KEY` en producción
- Configurar `DEBUG = False` en producción
- Agregar `ALLOWED_HOSTS` apropiados para producción
- Usar variables de entorno para configuración sensible

## Comandos Útiles

- `python manage.py runserver` - Iniciar servidor de desarrollo
- `python manage.py makemigrations` - Crear migraciones
- `python manage.py migrate` - Aplicar migraciones
- `python manage.py createsuperuser` - Crear usuario administrador
- `python manage.py collectstatic` - Recopilar archivos estáticos (producción)
- `python manage.py shell` - Abrir shell de Django

## Notas para Agentes

- Siempre mantener la estructura de carpetas de Django
- Seguir las convenciones de nombres de Django
- Documentar código complejo
- Mantener las vistas simples y delegar lógica a servicios o modelos cuando sea apropiado
- Probar cambios antes de sugerirlos al usuario
- Verificar que las URLs estén correctamente configuradas
- Asegurar que los templates estén en las ubicaciones correctas
