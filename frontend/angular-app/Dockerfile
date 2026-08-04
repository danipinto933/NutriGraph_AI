# Etapa 1: Build Angular App
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build --configuration=production

# Etapa 2: Servir con Nginx
FROM nginx:alpine

# Copiar configuración custom de nginx para SPA
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar el build compilado (asume output en dist/angular-app/browser o dist/angular-app)
COPY --from=build /app/dist/angular-app/browser /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
