FROM node:22-alpine

WORKDIR /app

COPY frontend/package.json ./package.json
RUN npm install

COPY frontend/ ./
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start", "--", "--hostname", "0.0.0.0", "--port", "3000"]
