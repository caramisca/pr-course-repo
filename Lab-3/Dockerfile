FROM node:22-bullseye-slim AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy source files and config
COPY tsconfig.json ./
COPY src ./src

# Compile TypeScript
RUN npm run compile

# Runtime image: install only production deps
FROM node:22-bullseye-slim
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --production

# Copy built artifacts and static assets
COPY --from=builder /app/dist ./dist
COPY public ./public
COPY boards ./boards

EXPOSE 8080

# Files are compiled to dist/ directly, not dist/src/
CMD ["node", "dist/server.js", "8080", "boards/perfect.txt"]
