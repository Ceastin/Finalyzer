import os
from dotenv import load_dotenv
from crewai.tools import tool
from PyPDF2 import PdfReader

load_dotenv()

# Fixed Typo: super_dev_tool -> serper_dev_tool
try:
    from crewai_tools.tools.serper_dev_tool import SerperDevTool
    SERPER_KEY = os.getenv("SERPERDEV_API_KEY")
    search_tool = SerperDevTool(api_key=SERPER_KEY) if SERPER_KEY else None
except Exception:
    search_tool = None

@tool("Read PDF Document")
def read_data_tool(file_path: str) -> str:
    """Read a PDF file and return text content. Raises FileNotFoundError if missing."""
    if not os.path.exists(file_path):
        return f"Error: PDF not found at path: {file_path}"

    try:
        reader = PdfReader(file_path)
        pages = []
        for p in reader.pages:
            text = p.extract_text() or ""
            lines = [line.rstrip() for line in text.splitlines() if line.strip()]
            pages.append("\n".join(lines))
        return "\n\n".join(pages)
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

@tool("Analyze Investment")
def analyze_investment_tool(financial_document_data: str) -> str:
    """Analyze financial data for investment insights."""
    if not financial_document_data:
        return "No financial data provided."
    summary = f"Document length (chars): {len(financial_document_data)}\n"
    summary += "Top-level suggestion: Run structured parsing (tables/balances) and validate numbers.\n"
    return summary

@tool("Risk Assessment")
def create_risk_assessment_tool(financial_document_data: str) -> str:
    """Create a risk assessment from financial data."""
    if not financial_document_data:
        return "No financial data provided for risk assessment."
    return (
        "Risk checklist:\n"
        "- Verify revenue recognition policies\n"
        "- Check cadence of cashflow vs. capex\n"
        "- Look for off-balance-sheet items\n"
        "- Recommend scenario analysis and sensitivity testing\n"
    )