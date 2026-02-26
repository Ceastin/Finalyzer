from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, AnalysisRecord
import os
import uuid
from fastapi.responses import HTMLResponse
# Import our Celery Worker task
from worker import process_financial_document

app = FastAPI(
    title="Financial Document Analyzer",
    description="Asynchronous AI-powered financial document analysis system"
)

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the frontend dashboard"""
    try:
        with open("index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>index.html not found! Make sure it is in the same folder as main.py</h1>"
    
@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
    db: Session = Depends(get_db)  # Inject the database connection
):
    """Upload a document and send it to the background AI Queue."""
    
    # 1. Generate a short unique ID for the file to prevent concurrent overwrites
    short_id = str(uuid.uuid4())[:8]
    file_path = f"data/doc_{short_id}.pdf"
    
    try:
        os.makedirs("data", exist_ok=True)
        
        # Save the uploaded file to disk
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        if not query or query.strip() == "":
            query = "Analyze this financial document for investment insights"
            
        # 2. Create a "PENDING" record in our SQLite database
        db_record = AnalysisRecord(filename=file.filename, status="PENDING")
        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        # 3. Send the job to RabbitMQ (Celery will pick this up instantly)
        # The .delay() command pushes it to the background worker!
        process_financial_document.delay(db_record.id, file_path, query.strip())
        
        # 4. Instantly return a receipt to the user (Returns in ~0.1 seconds)
        return {
            "status": "success",
            "task_id": db_record.id,
            "message": "Your document has been added to the queue! Use the /status endpoint with your task_id to view the results.",
            "file_processed": file.filename
        }
        
    except Exception as e:
        # If saving the file fails, clean up and throw an error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error queuing document: {str(e)}")



@app.get("/status/{task_id}")
async def get_analysis_status(task_id: str, db: Session = Depends(get_db)):
    """Check the database to see if the AI agents have finished."""
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == task_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Task ID not found")
    
    return {
        "task_id": record.id,
        "filename": record.filename,
        "status": record.status, # Will be PENDING, PROCESSING, COMPLETED, or FAILED
        "result": record.result_text
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)