# FastAPI Production Best Practices & Architectural Patterns

## Dependency Injection and Router Modularization
FastAPI uses `Depends()` for composable dependency injection. Use dependency providers for database sessions, authentication, and service clients:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.services.items import ItemService
from app.api.deps import get_item_service

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("/{item_id}")
async def get_item(
    item_id: str,
    service: ItemService = Depends(get_item_service),
):
    item = await service.fetch_item(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item
```

## Exception Handling & Error Schemas
Always use consistent structured JSON error responses with custom exception handlers:

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

class BusinessValidationError(Exception):
    def __init__(self, message: str, code: str = "VALIDATION_ERROR"):
        self.message = message
        self.code = code

@app.exception_handler(BusinessValidationError)
async def validation_handler(request: Request, exc: BusinessValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": exc.code, "message": exc.message},
    )
```

## CORS & Security Middleware
Configure CORS middleware explicitly for production frontend origins:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://app.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```
