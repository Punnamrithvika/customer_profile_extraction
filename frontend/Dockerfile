# Stage 1: Build the React application
FROM node:16 as build

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . ./
RUN npm run build

# Stage 2: Serve the built application with Nginx
FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html

# When a request comes in, if it's not for a file, serve index.html
# This is crucial for single-page applications with routing.
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
