#!/bin/sh

# Valores por defecto de fallback si no están definidas las variables de entorno
export API_URL=${API_URL:-"http://localhost:8000/api/v1"}
export GRAPH_API_URL=${GRAPH_API_URL:-"http://localhost:8001/api/v1"}
export CHAT_API_URL=${CHAT_API_URL:-"http://localhost:8002/api/v1"}

# Sustituir variables de entorno en env.template.js y generar env.js final
envsubst '${API_URL} ${GRAPH_API_URL} ${CHAT_API_URL}' < /usr/share/nginx/html/assets/env.template.js > /usr/share/nginx/html/assets/env.js

# Arrancar Nginx en primer plano
exec nginx -g "daemon off;"
