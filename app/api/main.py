from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import init_db
from app.core.scheduler import start_scheduler, shutdown_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    await start_scheduler()
    yield
    # Shutdown
    await shutdown_scheduler()


# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "Welcome to PaperWhale API!"}
