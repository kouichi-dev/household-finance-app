

from fastapi import FastAPI
from routers import router
from database import Base,engine
import models

app = FastAPI()
app.include_router(router)

Base.metadata.create_all(bind=engine)