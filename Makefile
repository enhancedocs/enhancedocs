.PHONY: dev
dev:
	uvicorn src.enhancedocs.main:app --reload --port 8080
