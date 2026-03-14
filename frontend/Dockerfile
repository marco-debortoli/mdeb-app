FROM node:22-alpine AS base

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

# dev: source is mounted via volume; command provided by compose
FROM base AS dev
EXPOSE 5173

# build: compile static assets
FROM base AS build
COPY . .
RUN npm run build

# prod: nginx serves static files and proxies /api to backend
FROM nginx:alpine AS prod
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
