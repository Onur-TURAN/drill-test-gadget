# 1. Next.js Build aşaması
FROM node:20-alpine AS next-builder

WORKDIR /app

COPY package*.json ./
RUN npm install --legacy-peer-deps

COPY . .
RUN npm run build

# 2. Go API Build aşaması
FROM golang:1.22-alpine AS go-builder

WORKDIR /go-api

COPY api/targets ./targets
WORKDIR /go-api/targets
RUN go mod init targets && go mod tidy
RUN go build -o /go-api/targets-api main.go

# 3. Production aşaması
FROM node:20-alpine

WORKDIR /app

# Next.js dosyalarını kopyala
COPY --from=next-builder /app/package*.json ./
COPY --from=next-builder /app/.next ./.next
COPY --from=next-builder /app/public ./public
COPY --from=next-builder /app/next.config.mjs ./next.config.mjs
COPY --from=next-builder /app/node_modules ./node_modules
COPY --from=next-builder bugboouny-dashboard ./bugboouny-dashboard

# Go API binary'sini kopyala
COPY --from=go-builder /go-api/targets-api /app/targets-api

EXPOSE 3000
EXPOSE 8080

ENV NODE_ENV=production

# Hem Next.js hem Go API başlat
CMD ["sh", "-c", "./targets-api & npx next start"]