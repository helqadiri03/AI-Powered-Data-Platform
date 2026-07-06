FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Expose Vite default port
EXPOSE 5173

# Start dev server
CMD ["npm", "run", "dev", "--", "--host"]
