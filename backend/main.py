from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import reports, auth, classify

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reports.router)
app.include_router(auth.router)
app.include_router(classify.router)


@app.get("/")
def root():
    return {"message": "Road Freight Risk AI backend is running."}
