from fastapi import FastAPI
from app.db.database import init_db
from app.core.scheduler import start_scheduler, shutdown_scheduler

# Initialize FastAPI app
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    init_db()
    await start_scheduler()


@app.on_event("shutdown")
async def shutdown_event():
    await shutdown_scheduler()


@app.get("/")
async def read_root():
    return {"message": "Welcome to PaperWhale API!"}
