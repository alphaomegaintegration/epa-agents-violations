FROM node:18-alpine as build

WORKDIR /app

# Accept build arguments for environment variables
ARG VITE_API_BASE
ARG VITE_WS_URL

# Set environment variables from build args
ENV VITE_API_BASE=${VITE_API_BASE}
ENV VITE_WS_URL=${VITE_WS_URL}

# Copy package files
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build the application with environment variables baked in
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]