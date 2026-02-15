
<p align="center">
  <img src="static/images/goalhub-logo.png" alt="alt" width="400" />
</p>

#  GoalHub

**Plataforma integral de recaudación de fondos basada en objetivos**

Recauda dinero para tus objetivos vendiendo o donando productos seleccionados de tu catálogo. Una solución moderna construida con Django que facilita la gestión de campañas de fundraising con roles diferenciados: administradores, beneficiarios (destinatarios) y clientes/donantes.

---

## 📋 Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Features Principales](#features-principales)
- [Roles, Grupos y Permisos](#roles-grupos-y-permisos)
- [Arquitectura y Aplicaciones](#arquitectura-y-aplicaciones)
- [Requisitos Técnicos](#requisitos-técnicos)
- [Setup Local](#setup-local)
- [Uso y Flujos](#uso-y-flujos)
- [Screenshots](#screenshots)
- [Convenciones del Proyecto](#convenciones-del-proyecto)

---

## Integrantes
    - Milagros Farfan

### Responsabilidades
    - Desarrollo de la plataforma 
    - Documentación
    - Gestión de Jira
    - Pruebas
    - Desarrollo de registro de usuarios
    - Desarrollo de administración de usuarios
    - Desarrollo de administración de grupos
    - Desarrollo de administración de permisos
    - Desarrollo de gestión de productos
    - Desarrollo de gestión de objetivos
    - Desarrollo de gestión de carrito
    - Desarrollo de gestión de pedidos
    - Desarrollo de gestión de historial de pedidos
    - Desarrollo de gestión de dashboard

## 📖 Descripción General

GoalHub es una plataforma flexible para recaudar fondos vinculados a objetivos específicos. Permite que los beneficiarios (destinatarios) creen campañas con metas monetarias o de stock, y que los clientes (usuarios/donantes) compren productos asociados a estos objetivos contribuyendo a su cumplimiento.

**Caso de uso típico:**
- Un destinatario crea un objetivo "Fondo para educación" con meta de $10,000
- Agrega productos del catálogo (libros, materiales) para la venta
- Los clientes compran productos para financiar el objetivo
- Cuando se alcanza la meta o se agota el stock → objetivo completado

La plataforma maneja automáticamente carritos de compra, genera pedidos simulados y rastrea el progreso de cada objetivo en tiempo real.

---

## ✨ Features Principales

### Para Administradores
- ✅ **Catálogo de Productos**: CRUD completo (crear, listar, editar, eliminar productos)
- ✅ **Gestión de Stock**: Controlar disponibilidad y precios de productos
- ✅ **Fotos de Productos**: Soporte de imágenes en Base64 o ImageField
- ✅ **Simulación de Compra**: Agregar productos al carrito y simular pedidos
- ✅ **Panel de Control**: Dashboard con estadísticas y resumen

### Para Destinatarios (Beneficiarios)
- ✅ **Gestión de Objetivos**: CRUD de sus propias campañas (goals)
- ✅ **Seguimiento de Progreso**: Ver montos recaudados vs. meta y stock disponible
- ✅ **Selección de Productos**: Asignar productos del catálogo a sus objetivos
- ✅ **Estados de Objetivo**: Activo, Cumplido (por monto), Finalizado (sin stock), Cancelado
- ✅ **Descripción y Foto**: Incluir foto y motivo detallado de cada objetivo

### Para Clientes/Usuarios
- ✅ **Explorar Objetivos**: Navegar y visualizar campañas activas
- ✅ **Carrito de Compra**: Agregar productos vinculados a objetivos
- ✅ **Checkout Simulado**: Simular compra y contribuir a objetivos
- ✅ **Historial de Pedidos**: Ver compras realizadas
- ✅ **Detalles de Productos**: Información completa con fotos

### Características Generales
- 🔐 **Autenticación y Autorización**: Registro, login e integración con Django Auth
- 👥 **Sistema de Grupos y Permisos**: Acceso granular basado en roles
- 📱 **Interfaz Responsiva**: Diseño Bootstrap 5 adaptado a móvil
- 💾 **Base de Datos** SQLite (desarrollo) / TODO: SQL (producción)
- 🎨 **UI/UX Moderna**: Widget tweaks, componentes reutilizables

---

## 👥 Roles, Grupos y Permisos

GoalHub implementa un sistema de tres roles principales. Cada uno tiene acceso diferenciado a funcionalidades:

### 1️⃣ **Administrador**

| Feature | Acceso | Descripción |
|---------|--------|-------------|
| **Catálogo de Productos** | ✅ CRUD | Crear, ver, editar, eliminar productos |
| **Stock de Productos** | ✅ Editar | Cambiar cantidad disponible |
| **Precios** | ✅ Editar | Actualizar precio de venta |
| **Carrito** | ✅ Sí | Puede agregar productos al carrito y simular compra |
| **Admin de Django** | ✅ Acceso total | Gestión de usuarios, grupos y permisos |
| **Dashboard** | ✅ Sí | Panel con estadísticas del catálogo |


### 2️⃣ **Destinatario**

| Feature | Acceso | Descripción |
|---------|--------|-------------|
| **Crear Objetivos** | ✅ CRUD | Crear, ver, editar, eliminar sus propios objetivos |
| **Editar Meta** | ✅ Sí | Cambiar monto a recaudar |
| **Seguimiento** | ✅ Sí | Ver montos recaudados y stock consumido |
| **Asignar Productos** | ✅ Sí | Vincular productos del catálogo a sus objetivos |
| **Catálogo de Productos** | ✅ Lectura | Ver productos disponibles (sin editar) |
| **Carrito** | ✅ Sí | Puede agregar productos al carrito (si aplica) |

**Permisos en Django:**
```
- goals.add_goal
- goals.change_goal (solo propios)
- goals.delete_goal (solo propios)
- goals.view_goal (solo propios)
- products.view_product
- cart.add_cart
- cart.view_cart
```

---

### 3️⃣ **Cliente / Usuario (Anónimo o Registrado)**

| Feature | Acceso | Descripción |
|---------|--------|-------------|
| **Registro/Login** | ✅ Sí | Crear cuenta o iniciar sesión |
| **Explorar Objetivos** | ✅ Sí | Ver todas las campañas activas |
| **Ver Detalles Objetivo** | ✅ Sí | Información completa, foto, monto, progreso |
| **Ver Productos** | ✅ Sí | Catálogo público de productos |
| **Carrito de Compra** | ✅ Sí | Agregar productos al carrito |
| **Checkout** | ✅ Sí | Simular compra (pedido) |
| **Historial de Pedidos** | ✅ Sí | Ver compras realizadas |

**Permisos en Django:**
```
- goals.view_goal (público)
- products.view_product (público)
- cart.add_cart
- cart.view_cart
- cart.add_order
- cart.view_order
```

---

## 🏗️ Arquitectura y Aplicaciones

GoalHub está modularizado en aplicaciones Django independientes, cada una con responsabilidad clara:

### **Estructura Base del Proyecto**

```
django-single/
├── config/                     
│   ├── settings.py           
│   ├── urls.py               
│   ├── wsgi.py
│   └── asgi.py
│
├── [APPS]/                   
│   ├── models.py              
│   ├── views.py              
│   ├── forms.py              
│   ├── urls.py               
│   ├── admin.py              
│   ├── services.py           
│   ├── tests.py               
│   ├── migrations/            
│   └── templates/[APP]/       
│
├── templates/                 
│   ├── base.html              
│   ├── errors/                
│   └── partials/              
│
├── static/                     
│   ├── css/
│   ├── js/
│   ├── images/               
│   └── screenshots/           
│
├── media/                      
│   └── [app]/
│
├── manage.py                  
├── requirements.txt            
├── pyproject.toml             
├── .env.example               
├── .env                        
└── setup.sh                    
```

---

## 🔧 Requisitos Técnicos

### Python y Django
- **Python**: 3.9+ (recomendado 3.12)

### Dependencias Principales
```
Django>=4.2.0
django-widget-tweaks        # Para simplificar atributos form en templates
Pillow                       # Para procesar imágenes
pre-commit                   # Git hooks
commitizen                   # Conventional commits
ruff                         # Linter/formatter rápido
```

---

## 🚀 Setup Local

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/learning-codes-projects/goal-hub
cd goal-hub
```

### Paso 2: Ejecutar script

./setup.sh

---

## 💡 Uso y Flujos

### Flujo 1: Administrador Crea Producto

```
1. Hace login en http://localhost:8000/login/ o /admin/
2. Navega a: /products/create/
3. Completa formulario:
   - Nombre: "Libro Educativo"
   - Descripción: "Recurso para aprendizaje"
   - Precio: 45.00
   - Stock: 50
   - Foto: Sube imagen o pega Base64
4. Save → Producto creado ✅
```

**Vista en Admin:**
```
Admin → Products → [+] Add Product
Rellena: name, description, price, stock, is_active
Guardar
```

---

### Flujo 2: Destinatario Crea Objetivo

```
1. Se registra en /register/ (debe ser creado como grupo "Destinatario" en admin)
2. Hace login
3. Navega a: /goals/create/
4. Completa formulario:
   - Título: "Fondo para educación"
   - Descripción: "Necesitamos recursos educativos"
   - Meta (target_amount): 10,000.00
   - Completa por: "Monto" (o "Stock", o "Ambos")
   - Foto: Sube imagen o Base64
5. Save → Objetivo creado (status: ACTIVE)
6. Opción: Editar → Asignar productos del catálogo
7. El objetivo aparece en /goals/ como propio y en la sección pública
```

---

### Flujo 3: Cliente Explora y Compra

```
1. Accede a http://localhost:8000/ (sin login o registrado)
2. Navega a /goals/ → ve todos los objetivos ACTIVE
3. Click en objetivo (ej: "Fondo para educación")
   → Ve detalles, foto, monto recaudado vs. meta, foto
   → Botón: "Add products to cart" o mostrar productos asignados
4. Selecciona producto, cantidad
5. "Add to cart" → producto agregado
6. Navega a /cart/ → ve items con meta asociada
7. Review & Checkout → simula pedido
8. Pedido guardado, objetivo se actualiza con amount_raised ✅
9. Puedo ver en /orders/ el historial de comprass
```

---

### Flujo 4: Seguimiento de Objetivo

```
Destinatario en /goals/ → Mi objetivo
├─ Progreso: $3,500 / $10,000 (35%)
├─ Stock: 45 unidades restantes de 50
├─ Estado: ACTIVE
├─ Si amount_raised >= target_amount → Status = ACHIEVED ✅
└─ Si no hay stock en productos → Status = EXHAUSTED ✅

Cliente en /goals/ → Objetivo público
├─ Ve mismo progreso
├─ Puede contribuir si objetivo está ACTIVE
└─ El carrito vincula su compra al objetivo
```

---

## 📸 Screenshots

### 🏠 **Home / Dashboard**

![Dashboard](static/screenshots/dashboard.png)

*Panel general con resumen de objetivos y productos activos.*

---

### 📦 **Catálogo de Productos**

#### Vista Admin
![Crear Producto](static/screenshots/create_product_admin.png)

*Formulario para administrador: crear/editar producto con foto, precio y stock.*

![Listado Productos Admin](static/screenshots/product_list_admin.png)

*Listado de productos en el admin, edición rápida y eliminación.*

#### Vista Cliente/Destinatario
![Listado Productos Cliente](static/screenshots/product_list_client.png)

*Catálogo de productos disponibles para compra (vista pública).*

![Listado Productos Destinatario](static/screenshots/product_list_destinatario.png)

*Productos desde perspectiva del destinatario (lectura, sin editar).*

---

### 🎯 **Gestión de Objetivos**

#### Crear Objetivo
![Crear Objetivo](static/screenshots/create_goal_destinatario.png)

*Formulario para el destinatario: título, meta, descripción, foto.*

#### Listar Objetivos
![Mis Objetivos (Destinatario)](static/screenshots/goal_list_destinatario.png)

*Vista de "Mis Objetivos" para beneficiario: editar, ver progreso, eliminar.*

![Objetivos Públicos (Cliente)](static/screenshots/goal_list_client.png)

*Listado de objetivos públicos/activos que el cliente puede ver.*

#### Detalle de Objetivo
![Detalle Objetivo - Cliente 1](static/screenshots/goal_by_goal_client1.png)

*Vista completa del objetivo: foto, descripción, progreso, productos asociados.*

![Detalle Objetivo - Cliente 2](static/screenshots/goal_by_coal_client2.png)

*Otro ángulo: botón de compra, descripción del proyecto, barras de progreso.*

![Objetivo Completado](static/screenshots/goal_completed_destinatario.png)

*Objetivo con status ACHIEVED (meta alcanzada) después de suficientes compras.*

#### Detalles del Producto dentro del Objetivo
![Detalle Producto en Objetivo](static/screenshots/goal_product_detail_client.png)

*Información del producto: precio, stock, vinculación con el objetivo actual.*

---

### 🛒 **Carrito y Pedidos**

#### Carrito Vacío
![Carrito Vacío](static/screenshots/no_cart_client.png)

*Mensaje amigable cuando el carrito está vacío.*

#### Carrito con Productos
![Carrito con Ítems](static/screenshots/cart_client.png)

*Carrito con productos agregados, cantidades, totales y botón de checkout.*

#### Realizar Pedido
![Pedido Cliente](static/screenshots/pedido_client.png)

*Confirmación antes de simular la compra, resumen de artículos y monto.*

#### Detalle del Pedido
![Detalle Pedido Cliente](static/screenshots/Pedido_detail_client.png)

*Vista del pedido completado: fecha, items, precio unitario, total.*

#### Historial de Pedidos
![Listado de Pedidos](static/screenshots/orders_client.png)

*Historial de compras realizadas por el usuario, con links a detalles.*

---

### 🔐 **Admin de Usuarios y Permisos**

#### Gestión de Usuarios
![Admin - Usuarios](static/screenshots/admin_usuarios_permissions.png)

*Panel de admin: listado de usuarios, búsqueda, edición de permisos.*

#### Gestión de Grupos
![Admin - Grupos](static/screenshots/admin_groups.png)

*Pantalla de "Grupos" en Django Admin: crear/editar roles (Admin, Destinatario, Cliente).*

#### Grupo: Especificaciones
- **Superusuario**: Acceso total [Imagen: admin_superusuario1_1.png]
- **Administrador**: Permisos de catálogo [Imagen: aadmin_gerente_permissions.png]
- **Destinatario**: Permisos de objetivos [Imagen: admin_destinatario_permissions.png]
- **Cliente/Invitado**: Permisos de lectura y compra [Imagen: admin_invitados_permissions.png]

---

### 👤 **Registro y Perfil**

![Registro](static/screenshots/register.png)

*Formulario de registro: usuario, email, contraseña, confirmación.*

---

### 📋 **Otras Pantallas**

![Sin Objetivos](static/screenshots/no_goals_client.png)

*Mensaje cuando no hay objetivos disponibles en la sección pública.*

![Editar Objetivo](static/screenshots/edit_goal_admin.png)

*Formulario para editar objetivo existente (solo para el propietario/admin).*

---

## 📐 Convenciones del Proyecto

### Estructura de Archivos

```
[app]/
├── models.py              # Modelos ORM (lógica de datos)
├── forms.py               # Formularios Django (validación)
├── views.py               # CBV o FBV (controladores)
├── urls.py                # Rutas de la app
├── services.py            # Lógica de negocio (opcional pero recomendado)
├── selectors.py           # Query helpers (opcional)
├── admin.py               # Custom admin site
├── tests.py               # Tests unitarios
├── migrations/            # Historial de cambios BD
└── templates/[app]/       # Templates HTML
    ├── [model]_list.html
    ├── [model]_detail.html
    ├── [model]_form.html  # Crear/Editar
    └── ...
```

### Git Commits (Conventional Commits)

```bash
# Crear feature
git commit -m "feat(products): add product image upload with base64 support"

# Fix bug
git commit -m "fix(cart): correct total calculation for discounted items"

# Docs
git commit -m "docs(readme): update setup instructions"

# Refactor
git commit -m "refactor(goals): extract progress calculation to service"

# Tests
git commit -m "test(goals): add unit tests for goal completion logic"

# Style
git commit -m "style: format code with ruff"
```

Formato: `<type>(<scope>): <subject>`
- **type**: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `chore`
- **scope**: app o módulo afectado
- **subject**: descripción breve, imperativo, 50 caracteres máx


