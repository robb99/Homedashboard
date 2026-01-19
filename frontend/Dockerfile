# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY public/ ./public/
COPY src/ ./src/

# Build arguments for environment variables
ARG REACT_APP_API_URL=http://localhost:8000
ARG REACT_APP_REFRESH_INTERVAL=30000

ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_REFRESH_INTERVAL=$REACT_APP_REFRESH_INTERVAL

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
