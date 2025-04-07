# Stage 1: Build the Vue frontend
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the app and build
COPY . .
RUN chmod +x ./node_modules/.bin/vite && npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy built files to Nginx's web directory
COPY --from=builder /app/dist /usr/share/nginx/html
COPY ./src/assets/videos /usr/share/nginx/html/videos

# Expose the port for Nginx
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]