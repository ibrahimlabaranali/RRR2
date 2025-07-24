
# FastAPI backend placeholder (extend with real logic)
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Road Freight Risk AI backend running"}
