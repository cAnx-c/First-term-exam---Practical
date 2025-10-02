# First-term-exam---Practical
Requisitos

Python 3.10+

Git Bash o WSL para ejecutar brute_force.sh (opcional).
En Windows puedes usar bruteforce.py sin bash.

Un entorno virtual.

# Estructura y usuarios por defecto

En python/main.py hay usuarios "quemados" (ejemplo):

admin / 1234

admin4 / 1234

testuser / passw0rd

Endpoints:

GET / — salud / mensaje.

POST /users — crear usuario. Body JSON ejemplo:

{"username":"alice","password":"miPass","email":"alice@example.com","is_active":true}


GET /users — listar usuarios (skip, limit query params).

GET /users/{id} — obtener usuario por id.

PUT /users/{id} — actualizar (username, email, is_active; no password).

DELETE /users/{id} — eliminar usuario.

POST /users/change-password — cambiar contraseña (requiere old_password).

POST /login — login. Body JSON:

{"username":"admin4","password":"1234"}


Respuesta de login exitosa:

{"message":"Login successful","user":"admin4"}


Respuesta fallida: 401 Invalid credentials o 403 User inactive.

Probar manualmente con curl (ejemplos)

Git Bash / WSL:

curl -i -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin4","password":"1234"}'


PowerShell (recomendado en Windows):

Invoke-RestMethod -Uri http://127.0.0.1:8000/login -Method Post -ContentType 'application/json' -Body '{"username":"admin4","password":"1234"}'

# Prueba de fuerza bruta
Usando brute_force.sh (Git Bash / WSL)

Asegúrate de estar en la carpeta del proyecto:

cd /c/Users/Home/code/project


Haz ejecutable (si es necesario) y ejecuta:

chmod +x brute_force.sh
./brute_force.sh http://127.0.0.1:8000 admin4 passwords.txt 2>&1 | tee results.log


passwords.txt contiene una contraseña por línea.

El script imprimirá cada intento con HTTP_CODE y cuerpo de respuesta; se detiene al encontrar 200.

En results.log se verá las líneas como:

[401] pwd='wrongpass' -> {"detail":"Invalid credentials"}
[200] pwd='1234' -> {"message":"Login successful","user":"admin4"}


200 → contraseña encontrada; el script se detiene.

000 → fallo en conexión (curl no alcanzó el servidor).

401/403/422 → credenciales inválidas / usuario inactivo / JSON malformado.


Pruebas:
<img width="739" height="238" alt="image" src="https://github.com/user-attachments/assets/22169985-a956-4c3e-b833-692d1b9008b4" />
