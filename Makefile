# ============================================================
# Makefile — Build, push và deploy image lên CMC Cloud
# Dùng: make <target>
# ============================================================

# Đọc từ .env nếu có
-include .env
export

REGISTRY   ?= yourdockerhub
TAG        ?= latest
BACKEND_IMG = $(REGISTRY)/media-backend:$(TAG)
FRONTEND_IMG= $(REGISTRY)/media-frontend:$(TAG)

# ── Local Development ────────────────────────────────────────
.PHONY: dev
dev:
	docker compose up --build -d
	@echo "✅ Dev stack running at http://localhost:8080"

.PHONY: dev-down
dev-down:
	docker compose down -v

# ── Build Images ─────────────────────────────────────────────
.PHONY: build
build: build-backend build-frontend

.PHONY: build-backend
build-backend:
	@echo "🔨 Building backend image..."
	docker build -t $(BACKEND_IMG) ./backend
	@echo "✅ Backend image: $(BACKEND_IMG)"

.PHONY: build-frontend
build-frontend:
	@echo "🔨 Building frontend image..."
	docker build -t $(FRONTEND_IMG) ./frontend
	@echo "✅ Frontend image: $(FRONTEND_IMG)"

# ── Push to Registry ─────────────────────────────────────────
.PHONY: push
push: push-backend push-frontend

.PHONY: push-backend
push-backend:
	docker push $(BACKEND_IMG)

.PHONY: push-frontend
push-frontend:
	docker push $(FRONTEND_IMG)

# ── Build + Push (shortcut) ──────────────────────────────────
.PHONY: release
release: build push
	@echo "🚀 Images pushed: $(BACKEND_IMG) | $(FRONTEND_IMG)"

# Trên Backend EC (chạy cả Backend và 4 DB):
.PHONY: deploy-backend
deploy-backend:
	docker pull $(BACKEND_IMG)
	docker compose -f docker-compose.backend.yml up -d
	@echo "✅ Backend & DBs deployed"

# Trên Frontend EC:
.PHONY: deploy-frontend
deploy-frontend:
	docker pull $(FRONTEND_IMG)
	docker compose -f docker-compose.frontend.yml up -d
	@echo "✅ Frontend deployed"

# ── Logs & Status ────────────────────────────────────────────
.PHONY: logs-backend
logs-backend:
	docker compose -f docker-compose.backend.yml logs -f

.PHONY: logs-frontend
logs-frontend:
	docker compose -f docker-compose.frontend.yml logs -f

.PHONY: status
status:
	docker ps --filter "name=prod_"


# ── Help ──────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "  make dev            - Chạy local development stack"
	@echo "  make build          - Build cả 2 images"
	@echo "  make push           - Push lên Docker Hub"
	@echo "  make release        - Build + Push (shortcut)"
	@echo "  make deploy-backend - Deploy backend trên EC"
	@echo "  make deploy-frontend- Deploy frontend trên EC"
	@echo "  make logs-backend   - Xem log backend"
	@echo "  make logs-frontend  - Xem log frontend"
	@echo "  make status         - Kiểm tra container đang chạy"
	@echo ""
