.PHONY: setup setup-backend setup-frontend setup-mcp run-backend run-frontend run-mcp test test-backend test-mcp lint clean

PYTHON ?= python3
PIP    ?= $(PYTHON) -m pip

setup: setup-backend setup-frontend setup-mcp

setup-backend:
	$(PIP) install -r backend/requirements.txt

setup-frontend:
	cd frontend && npm install

setup-mcp:
	$(PIP) install -r mcp_server/requirements.txt

run-backend:
	cd backend && uvicorn main:app --reload --port 8000

run-frontend:
	cd frontend && npm run dev

run-mcp:
	cd mcp_server && $(PYTHON) server.py

test: test-backend test-mcp

test-backend:
	cd backend && $(PYTHON) -m pytest tests/ -v

test-mcp:
	cd mcp_server && $(PYTHON) -m pytest tests/ -v

lint:
	$(PYTHON) -m pyflakes backend/ mcp_server/ || true

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .next -exec rm -rf {} +
	find . -type d -name node_modules -prune -exec rm -rf {} +
