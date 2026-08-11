#!/bin/sh

# Valores por defecto de fallback si no están definidas las variables de entorno
API_URL=${API_URL:-"http://localhost:8000/api/v1"}
GRAPH_API_URL=${GRAPH_API_URL:-"http://localhost:8001/api/v1"}
CHAT_API_URL=${CHAT_API_URL:-"http://localhost:8002/api/v1"}

# Asegurar que el directorio assets existe
mkdir -p /usr/share/nginx/html/assets

# Generar env.js dinámicamente de forma incondicional al arrancar el contenedor
cat <<EOF > /usr/share/nginx/html/assets/env.js
(function (window) {
  window.__env = window.__env || {};
  window.__env.apiUrl = '${API_URL}';
  window.__env.graphApiUrl = '${GRAPH_API_URL}';
  window.__env.chatApiUrl = '${CHAT_API_URL}';
})(this);
EOF

echo "[entrypoint.sh] env.js generado exitosamente:"
cat /usr/share/nginx/html/assets/env.js

# Arrancar Nginx en primer plano
exec nginx -g "daemon off;"
