# Etapa 1: Build Angular App
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build --configuration=production

# Etapa 2: Servir con Nginx
FROM nginx:alpine

# Instalar gettext para soporte de envsubst
RUN apk add --no-cache gettext

# Copiar configuración custom de nginx para SPA
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar el build compilado (asume output en dist/angular-app/browser)
COPY --from=build /app/dist/angular-app/browser /usr/share/nginx/html

# Copiar script de entrypoint y darle permisos de ejecución
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
