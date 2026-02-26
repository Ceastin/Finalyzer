import os
from celery import Celery
from crewai import Crew, Process
from database import SessionLocal, AnalysisRecord

# Import your agents and tasks from your existing files
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import verification, analyze_financial_document, investment_analysis, risk_assessment
RABBITMQ_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
# Initialize Celery and connect it to RabbitMQ
# celery_app = Celery(
#     "financial_worker",
#     broker="amqp://guest:guest@localhost:5672//"
# )
celery_app = Celery(
    "financial_worker",
    broker=RABBITMQ_URL
)

@celery_app.task
def process_financial_document(record_id: str, file_path: str, query: str):
    """This function runs in the background, entirely separate from FastAPI."""
    db = SessionLocal()
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
    
    if not record:
        db.close()
        return "Record not found"

    try:
        # 1. Update status to let the user know we started
        record.status = "PROCESSING"
        db.commit()

        # 2. Assemble the Crew
        financial_crew = Crew(
            agents=[verifier, financial_analyst, risk_assessor, investment_advisor],
            tasks=[verification, analyze_financial_document, risk_assessment, investment_analysis],
            process=Process.sequential,
            verbose=True
        )

        # 3. Run the heavy AI analysis
        result = financial_crew.kickoff(inputs={"file_path": file_path, "query": query})

        # 4. Save the final output to the database
        record.result_text = str(result)
        record.status = "COMPLETED"
        db.commit()

    except Exception as e:
        # If the API crashes or rate limits, mark it as failed safely
        record.status = "FAILED"
        record.result_text = f"Error: {str(e)}"
        db.commit()
        print(f"❌ Task Failed: {e}")
        
    finally:
        db.close()
        
    return "Task Finished"
