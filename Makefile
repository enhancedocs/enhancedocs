.PHONY: dev
dev:
	uvicorn main:app --reload --port 8080
