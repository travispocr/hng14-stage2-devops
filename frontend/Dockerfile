# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json .
RUN npm install --production

# Final stage
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY app.js .
COPY views ./views

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:3000 || exit 1

CMD ["node", "app.js"]