# Guía para usar Postman con la API PAI

## Problema común: "No se pudieron validar las credenciales"

Si recibes este error al usar el token JWT, sigue estos pasos:

## 1. Obtener el Token

### Endpoint: `POST http://localhost:8000/login/access-token`

**Configuración en Postman:**
- **Método:** POST
- **URL:** `http://localhost:8000/login/access-token`
- **Headers:** No necesitas headers especiales
- **Body:** Selecciona `x-www-form-urlencoded` y agrega:
  - `username`: tu email (ej: `usuario@example.com`)
  - `password`: tu contraseña

**Respuesta esperada:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

## 2. Usar el Token en otras peticiones

### Endpoint: `GET http://localhost:8000/users/me`

**Configuración en Postman:**
- **Método:** GET
- **URL:** `http://localhost:8000/users/me`
- **Headers:** Agrega un header con:
  - **Key:** `Authorization`
  - **Value:** `Bearer <tu_token_aqui>` 
  
  ⚠️ **IMPORTANTE:** 
  - Debe empezar con la palabra "Bearer" (con B mayúscula)
  - Debe haber un **espacio** después de "Bearer"
  - El token debe ser el valor completo que recibiste en `access_token`

**Ejemplo correcto:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTcw...
```

**Ejemplos INCORRECTOS:**
```
❌ Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  (falta "Bearer ")
❌ Authorization: bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  (bearer en minúscula)
❌ Authorization: BearereyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  (falta espacio)
```

## 3. Usar la autenticación OAuth2 de Postman (Recomendado)

Postman tiene soporte nativo para OAuth2:

1. Ve a la pestaña **Authorization** de tu petición
2. Selecciona **Type: OAuth 2.0**
3. En **Token Name:** pon cualquier nombre (ej: "PAI Token")
4. En **Grant Type:** selecciona **Password Credentials**
5. En **Access Token URL:** `http://localhost:8000/login/access-token`
6. En **Username:** tu email
7. En **Password:** tu contraseña
8. Haz clic en **Get New Access Token**
9. Postman automáticamente agregará el header `Authorization: Bearer <token>`

## 4. Verificar que el token funciona

### Endpoint de prueba: `GET http://localhost:8000/login/test-token`

Este endpoint verifica que tu token sea válido y retorna tu información de usuario.

## 5. Solución de problemas

### Error: "No se pudieron validar las credenciales"

**Posibles causas:**
1. ❌ El token no está en el formato correcto: `Bearer <token>`
2. ❌ El token ha expirado (válido por 30 minutos por defecto)
3. ❌ El token está mal copiado (faltan caracteres)
4. ❌ El servidor se reinició y la SECRET_KEY cambió

**Solución:**
- Obtén un nuevo token con `/login/access-token`
- Verifica que el header esté exactamente como: `Authorization: Bearer <token>`
- Revisa los logs del servidor para ver mensajes de DEBUG

### Ver logs del servidor

Si el servidor está corriendo, verás mensajes de DEBUG en la consola que te ayudarán a identificar el problema:
- `DEBUG: Error JWT al decodificar el token: ...`
- `DEBUG: El token ha expirado`
- `DEBUG: Token válido, pero usuario con ID X NO encontrado en la BD`

## 6. Endpoints que requieren autenticación

Todos estos endpoints requieren el header `Authorization: Bearer <token>`:

- `GET /users/me` - Obtener usuario actual
- `GET /users/{user_id}` - Obtener usuario por ID
- `GET /users/` - Listar usuarios (solo admin)
- `POST /courses/` - Crear curso (solo docente/admin)
- `GET /courses/me` - Mis cursos (docente)
- `GET /tasks/{task_id}` - Ver tarea
- `POST /tasks/` - Crear tarea (solo docente/admin)
- Y más...

## 7. Colección de Postman (Opcional)

Puedes crear una colección en Postman con:
- Variables de entorno para `base_url` y `token`
- Pre-request scripts para auto-renovar tokens
- Tests para validar respuestas

