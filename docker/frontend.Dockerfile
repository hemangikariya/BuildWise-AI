FROM node:20-alpine

WORKDIR /app

# Copy package descriptors
COPY ./package.json ./package-lock.json* /app/

# Install dependencies
RUN npm install --frozen-lockfile || npm install

# Copy source code
COPY . /app

EXPOSE 3000

# Next.js 15 dev mode
CMD ["npm", "run", "dev"]
