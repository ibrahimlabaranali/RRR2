from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import reports, auth, classify
from routes import sms_report
app.include_router(sms_report.router)


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


@app.post("/reports/bulk_upload/")
def bulk_upload(reports: List[ReportIn]):
    for r in reports:
        db.add(Report(**r.dict(), synced=False))
    db.commit()
    return {"status": "Bulk upload received"}

