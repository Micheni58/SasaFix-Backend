from fastapi import FastAPI
from server.resources import user_resource  # your resource file

app = FastAPI(title="Sasafix API", version="1.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to Sasafix API"}

app.include_router(user_resource.router, prefix="/api")