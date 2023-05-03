import time
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import project_config
from app.core.exception import CustomHTTPException
from app.router.detect_router import router as detect_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.exception_handler(CustomHTTPException)
async def uvicorn_exception_handler(request: Request, exc: CustomHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.error_code,
            "msg": exc.error_message
        }
    )

app.include_router(detect_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=project_config.ALGO_PORT)