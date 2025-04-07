# Use Node.js LTS version as base image
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the source code
COPY . .

# Expose the port your gateway runs on
EXPOSE 3000

# Start the gateway
CMD ["node", "gateway.js"]