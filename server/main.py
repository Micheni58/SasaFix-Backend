from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.resources import booking_resource, user_resource

app = FastAPI(title="Sasafix API", version="1.0")

# Configure CORS properly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Sasafix API"}

app.include_router(user_resource.router, prefix="/api")
app.include_router(booking_resource.router, prefix="/api")
