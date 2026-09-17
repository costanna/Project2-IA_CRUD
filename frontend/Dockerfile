# Build
FROM node:20-alpine AS build
WORKDIR /app

# Vite incrusta las variables VITE_* en el bundle en tiempo de build, asi
# que las recibimos como build args de Docker y las exponemos como env
# antes de compilar.
ARG VITE_API_URL=http://localhost:8000/api/v1
ARG VITE_WS_URL=ws://localhost:8000/ws/notifications
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_WS_URL=$VITE_WS_URL

COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# Serve estatico con nginx
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
