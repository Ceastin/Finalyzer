# 📊 Financial Document Analyzer - AI Multi-Agent System

A comprehensive, enterprise-grade financial document analysis system that processes corporate reports, financial statements, and investment documents using a highly optimized CrewAI multi-agent pipeline. 

This project was built to solve the **"Financial Document Analyzer - Debug Assignment"**. It has been heavily debugged, refactored, and upgraded from a basic synchronous script into a fully containerized, asynchronous microservices architecture.

## ✨ Features & Mission Accomplishments

✅ **Fixed Deterministic Bugs:** Resolved critical API timeouts, concurrency issues, and broken tool logic.
✅ **Fixed Inefficient Prompts:** Completely rewrote agent personas to stop hallucinating and provide strict, data-backed financial analysis.
🏆 **Bonus - Queue Worker Model:** Upgraded the system to handle concurrent requests using **Celery** and **RabbitMQ**.
🏆 **Bonus - Database Integration:** Added **SQLite** (via SQLAlchemy) to persistently store analysis results and task statuses.
🌐 **Modern UI Dashboard:** Built a reactive frontend to monitor the AI agents in real-time.
🐳 **Fully Containerized:** One-click deployment using Docker Compose.

RESULTS-
![result screen](https://github.com/user-attachments/assets/2353416d-71c9-4f88-a110-71ed0392d365)
![rseult response](https://github.com/user-attachments/assets/0f0b2d4e-e618-42d5-9e23-ea608a55aafe)

---

## 🐛 Bugs Found & How They Were Fixed

The original codebase suffered from critical deterministic bugs and severe prompt inefficiencies. Here is a breakdown of the fixes:

### 1. Inefficient & Hallucinating Prompts
* **The Bug:** The original `agents.py` and `task.py` explicitly instructed the AI to *"make up investment advice,"* *"hallucinate financial terms,"* and *"ignore actual risk factors."* * **The Fix:** Completely rewrote the system prompts and expectations. Agents are now assigned strict, professional personas with clear objectives to extract *actual* metrics from the provided PDF, assess *real* regulatory risks, and output structured, data-backed analysis with proper disclaimers.

### 2. Synchronous Web Server Blocking (Deterministic Bug)
* **The Bug:** The FastAPI endpoint (`run_crew`) waited for the entire CrewAI process to finish before returning a response, causing browser timeouts and blocking the server from handling multiple users.
* **The Fix:** Extracted the heavy CrewAI logic into a background **Celery Worker**. The FastAPI server now instantly returns a `task_id`, allowing the frontend to poll the database for results asynchronously.

### 3. API Rate Limiting / 429 Errors (Deterministic Bug)
* **The Bug:** Firing four agents simultaneously without speed limits caused the application to exceed the LLM API's strict Rate Limits (RPM), crashing the pipeline.
* **The Fix:** Implemented the `max_rpm=3` parameter on all Agent definitions to artificially pace the LLM requests, ensuring the system stays safely within API limits.

### 4. File Overwrite Race Conditions (Deterministic Bug)
* **The Bug:** The `main.py` endpoint hardcoded the upload path to `data/sample.pdf` and immediately deleted it in a `finally` block.
* **The Fix:** Implemented dynamic UUID-based file generation (`doc_{uuid}.pdf`). Removed premature cleanup logic so background workers actually have time to read the files.

### 5. Broken Tooling & Imports (Deterministic Bug)
* **The Bug:** The custom tools relied on undefined classes and contained broken asynchronous logic that CrewAI couldn't execute cleanly.
* **The Fix:** Refactored the tool definitions and ensured agents could properly read the PDF documents to extract the necessary text.

---

## 🚀 Setup and Usage Instructions

This application is fully containerized. You do not need to install Python, RabbitMQ, or Redis on your local machine—only Docker!

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
* A Gemini API Key from Google AI Studio.

### 1. Installation
Clone the repository and navigate into the project directory:
```bash
git clone [https://github.com/YOUR_USERNAME/financial-document-analyzer.git](https://github.com/YOUR_USERNAME/financial-document-analyzer.git)
cd financial-document-analyzer
```
### 2. Environment Variables
Create a .env file in the root directory and add your LLM API key:
```bash
GEMINI_API_KEY=your_actual_api_key_here
```
### 3. Launch the Application
Start the entire microservices stack (FastAPI, RabbitMQ, and Celery Worker) 
using Docker Compose:

```bash
docker compose up --build
```

### 4. Usage
Once the terminal logs confirm the services are running, open your web browser and navigate to the frontend dashboard:
👉 http://localhost:8000/

Upload a financial document (e.g., Tesla Q2 Update).

Click "Submit".

Watch the live status monitor track your AI agents as they process the document in the background.



## 📖 API Documentation
The backend exposes a RESTful API built with FastAPI. You can view the interactive Swagger UI at http://localhost:8000/docs.

### POST /analyze
Uploads a financial PDF and queues it for asynchronous processing.

Content-Type: multipart/form-data

Parameters:

    file (File, Required): The PDF document to analyze.

    query (String, Optional): Custom instructions for the AI analyst.

Response (200 OK):
```bash
{
  "status": "success",
  "task_id": "a1b2c3d4-e5f6-7890",
  "message": "Your document has been added to the queue! Use the /status endpoint with your task_id to view the results.",
  "file_processed": "TSLA-Q2-2025.pdf"
}
```
### GET /status/{task_id}
Checks the SQLite database for the current status of an analysis job.

Parameters:

    task_id (Path, Required): The ID returned by the /analyze endpoint.

Response (200 OK):
```bash
{
  "task_id": "a1b2c3d4-e5f6-7890",
  "filename": "TSLA-Q2-2025.pdf",
  "status": "COMPLETED", 
  "result": "**Investment Themes from Tesla...** \n\n (Full markdown report here)"
}

(Note: status will cycle through PENDING, PROCESSING, COMPLETED, or FAILED)
```
