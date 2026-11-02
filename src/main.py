from fastapi import FastAPI

app = FastAPI(
    title="Fast API Service",
    description="파이썬 백엔드 구축!",
    version="1.0.0",
    doce_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
def health_check():
    return {"message": "Hello, World!"}