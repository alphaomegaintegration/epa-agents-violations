FROM node:18-alpine as build

WORKDIR /app

# Accept build arguments for environment variables
ARG REACT_APP_API_BASE
ARG REACT_APP_WS_URL

# Set environment variables from build args
ENV REACT_APP_API_BASE=${REACT_APP_API_BASE}
ENV REACT_APP_WS_URL=${REACT_APP_WS_URL}

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