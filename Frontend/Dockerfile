# Stage 1: Build the Vue frontend
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Build the app
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy built files to Nginx's web directory
COPY --from=builder /app/dist /usr/share/nginx/html

# (Optional) Replace the default nginx config if needed
# COPY nginx.conf /etc/nginx/nginx.conf

# Expose the port for Nginxs
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
