# 🏪 **API de Tienda de Mascotas - Arquitectura de Microservicios**

## 📜 **Descripción General**

La **API de Tienda de Mascotas** está basada en una **arquitectura de microservicios** diseñada para gestionar:

- **Autenticación de Usuarios**
- **Gestión del Carrito de Compras**
- **Procesamiento de Pedidos**
- **Productos, Categorías y Reseñas**
- **Funcionalidad de Búsqueda**
- **Gestión de Mascotas**
- **Gateway de API con Nginx**
- **Autenticación JWT y Control de Acceso Basado en Roles (RBAC)**
- **Despliegue con Docker y Balanceo de Carga**

---

## 📌 **Estructura del Proyecto**

```
.
├── Dockerfile
├── start_services.bat
├── docker-compose.yml
├── architecture.drawio
├── docker/
└── services/
    ├── api-gateway/
    ├── auth/
    ├── cart/
    ├── orders/
    ├── products/
    ├── categories/
    ├── pets/
    ├── reviews/
    ├── search/
    └── utils/
        └── middelwares

```

---

## 🚀 **Cómo Ejecutar el Proyecto**

### **1️⃣ Clonar el Repositorio**

```bash
git clone https://github.com/mehdiattia404/petStore.git

```

### **2️⃣ Configuración del Entorno**

Cada microservicio contiene un archivo `.env` para su configuración. Asegúrate de que todos los archivos `.env` existen en sus respectivas carpetas.

Ejemplo `.env` para **Servicio de Autenticación (`services/auth/.env`)**:

```env
API_PORT=5000
JWT_SECRET_KEY=your_secret_key_here
```

### **3️⃣ Construir e Iniciar los Servicios**

Para **compilar y ejecutar todos los microservicios con Docker Compose**, ejecuta:

```bash
docker compose up -d --build
```

Para detener todos los servicios:

```bash
docker compose down
```

Para reiniciar los servicios:

```bash
docker compose restart
```

---

## ⚡ **Resumen de Middleware**

| Tipo de Middleware           | Propósito                                                        | Se Aplica A                  |
| ---------------------------- | ---------------------------------------------------------------- | ---------------------------- |
| **Autenticación JWT**        | Garantiza que solo los usuarios autenticados accedan a las rutas | APIs protegidas              |
| **Validación JSON**          | Valida el cuerpo de la solicitud entrante                        | Rutas `POST` & `PUT`         |
| **Filtrado y Ordenación**    | Permite ordenar y filtrar los datos devueltos                    | Endpoints `GET`              |
| **Paginación**               | Limita los datos por solicitud para un mejor rendimiento         | Respuestas basadas en listas |
| **Manejo Global de Errores** | Estandariza las respuestas de error y previene fallos            | Todos los servicios          |

---

Estos middleware aseguran que la **API de Pet Store** siga las mejores prácticas en seguridad, validación de datos y optimización de respuestas de la API. 🚀

## 🔥 **Resumen de Microservicios y Guía de API**

Cada servicio expone API REST documentadas con **Swagger (OpenAPI)**.

### **🛡️ 1. Servicio de Autenticación (`auth`)**

- **URL Base**: `http://localhost:5001`
- **Swagger**: [http://localhost:5001/swagger](http://localhost:5001/swagger)
- **APIs:**
  - **Registrar un Usuario** (`POST /api/auth/register`)
  - **Iniciar Sesión** (`POST /api/auth/login`)
  - **Obtener Información del Usuario** (`GET /api/auth/me`) 🔐 (Requiere JWT)

> **🔐 Autenticación JWT**
>
> - Después de iniciar sesión, se devuelve un **Token de Acceso (JWT)**.
> - Inclúyelo en las solicitudes con el encabezado `Authorization`:
>   ```http
>   Authorization: Bearer YOUR_JWT_TOKEN
>   ```

---

### **🛒 2. Servicio de Carrito (`cart`)**

- **URL Base**: `http://localhost:5005`
- **Swagger**: [http://localhost:5005/swagger](http://localhost:5005/swagger)
- **APIs:**
  - **Ver Carrito** (`GET /api/cart`) 🔐 (Requiere JWT)
  - **Agregar Producto al Carrito** (`POST /api/cart`) 🔐
  - **Eliminar Producto del Carrito** (`DELETE /api/cart/{item_id}`)

> **⚠ Requiere Autenticación JWT (`jwt_required()`)**
>
> - Los usuarios **deben estar autenticados** para acceder al carrito.
> - El JWT es **validado** en el encabezado de la solicitud.

---

### **📦 3. Servicio de Pedidos (`orders`)**

- **URL Base**: `http://localhost:5006`
- **Swagger**: [http://localhost:5006/swagger](http://localhost:5006/swagger)
- **APIs:**
  - **Realizar un Pedido** (`POST /api/orders`) 🔐 (Requiere JWT)
  - **Obtener Pedido por ID** (`GET /api/orders/{order_id}`) 🔐
  - **Actualizar Estado del Pedido** (`PUT /api/orders/{order_id}`) 🔐 (Solo Administradores)

> **👑 Control de Acceso Basado en Roles (RBAC)**
>
> - Solo los **Administradores** pueden actualizar el estado de los pedidos.
> - Los usuarios regulares pueden **realizar y ver** pedidos.

---

### **🛍️ 4. Servicio de Productos (`products`)**

- **URL Base**: `http://localhost:5002`
- **Swagger**: [http://localhost:5002/swagger](http://localhost:5002/swagger)
- **APIs:**
  - **Obtener Todos los Productos** (`GET /api/products`)
  - **Filtrar Productos** (`GET /api/products?category=electronics&sort=asc`)
  - **Obtener Producto por ID** (`GET /api/products/{product_id}`)
  - **Agregar Nuevo Producto** (`POST /api/products`) 🔐 (Solo Administradores)

---

### **📂 5. Servicio de Categorías (`categories`)**

- **URL Base**: `http://localhost:5003`
- **Swagger**: [http://localhost:5003/swagger](http://localhost:5003/swagger)
- **APIs:**
  - **Obtener Todas las Categorías** (`GET /api/categories`)
  - **Obtener Categoría por ID** (`GET /api/categories/{category_id}`)
  - **Crear Categoría** (`POST /api/categories`) 🔐 (Solo Administradores)

---

### **🐶 6. Servicio de Mascotas (`pets`)**

- **URL Base**: `http://localhost:5007`
- **Swagger**: [http://localhost:5007/swagger](http://localhost:5007/swagger)
- **APIs:**
  - **Obtener Todas las Mascotas** (`GET /api/pets`)
  - **Adoptar una Mascota** (`POST /api/pets/adopt`) 🔐 (Requiere JWT)

---

### **🔍 7. Servicio de Búsqueda (`search`)**

- **URL Base**: `http://localhost:5004`
- **Swagger**: [http://localhost:5004/swagger](http://localhost:5004/swagger)
- **APIs:**
  - **Buscar Productos/Mascotas** (`GET /api/search?query=dog`)

---

### **⭐ 8. Servicio de Reseñas (`reviews`)**

- **URL Base**: `http://localhost:5008`
- **Swagger**: [http://localhost:5008/swagger](http://localhost:5008/swagger)
- **APIs:**
  - **Obtener Reseñas** (`GET /api/reviews/{product_id}`)
  - **Enviar Reseña** (`POST /api/reviews`) 🔐 (Requiere JWT)

---

### **🌐 Gateway de API (Nginx)**

- **URL Base**: `http://localhost:80`
- **Maneja Balanceo de Carga y Enrutamiento**
- **Rutas de Servicios**:

  ```nginx
  location /api/auth {
      proxy_pass http://auth_service;
  }

  location /api/cart {
      proxy_pass http://cart_service;
  }

  location /api/orders {
      proxy_pass http://orders_service;
  }

  location /api/products {
      proxy_pass http://products_service;
  }

  location /api/categories {
      proxy_pass http://categories_service;
  }

  location /api/pets {
      proxy_pass http://pets_service;
  }

  location /api/search {
      proxy_pass http://search_service;
  }

  location /api/reviews {
      proxy_pass http://reviews_service;
  }
  ```

---

## 🏗 **Resiliencia y Balanceo de Carga**

- Cada servicio tiene **2 réplicas** (`deploy.replicas: 2`).
- **Nginx Load Balancer** distribuye el tráfico entre instancias.

### **🛠️ Manejo de Errores**

- **Validaciones** en todas las rutas `POST`/`PUT`.
- **Autenticación JWT y Autorización (`RBAC`)**.
- **Manejo Global de Excepciones** para fallos en la API.

---

## 📄 **Licencia**

Licencia MIT © 2025 Pet Store API
