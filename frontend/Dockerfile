FROM node:20-alpine

WORKDIR /app

COPY package.json /app/package.json
RUN npm config set registry https://registry.npmmirror.com \
    && npm install

COPY src /app/src
COPY index.html /app/index.html
COPY vite.config.js /app/vite.config.js

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
