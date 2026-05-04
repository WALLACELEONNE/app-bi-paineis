FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

RUN echo '#!/bin/sh' > /entrypoint.sh && \
    echo 'cd /app && npm install --silent' >> /entrypoint.sh && \
    echo 'exec npm run dev -- --host 0.0.0.0' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 5173

ENTRYPOINT ["/entrypoint.sh"]
