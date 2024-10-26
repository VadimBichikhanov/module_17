from fastapi import FastAPI
from backend.db import db_manager
from routers import user, task
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
app = FastAPI()

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    print(f"OMG! An HTTP error!: {repr(exc)}")
    return await http_exception_handler(request, exc)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"OMG! The client sent invalid data!: {exc}")
    return await request_validation_exception_handler(request, exc)

app.include_router(user.router)
app.include_router(task.router)

@app.on_event("startup")
async def startup_event():
    await db_manager.init_models()
    await db_manager.check_db_connection()
    await db_manager.test_async_session()
    await db_manager.test_data_operations()

@app.on_event("shutdown")
async def shutdown_event():
    await db_manager.close_db_connection()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)