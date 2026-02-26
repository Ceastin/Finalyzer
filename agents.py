import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from tools import search_tool, read_data_tool

load_dotenv()

# Initialize Gemini LLM using CrewAI's native LiteLLM integration
gemini_llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.2,
    api_key=os.getenv("GEMINI_API_KEY")
)

financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Accurately extract and analyze financial metrics based strictly on the provided document answering: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a meticulous financial analyst with 15 years of institutional experience. "
        "You never make assumptions, you rely strictly on data provided in financial reports, "
        "and you always highlight both positive growth and potential financial stress indicators."
    ),
    tools=[read_data_tool],
    llm=gemini_llm,
    max_iter=3,
    max_rpm=10,  # <-- ADD THIS TO PREVENT RATE LIMITING
    allow_delegation=True
)

verifier = Agent(
    role="Financial Document Verifier",
    goal="Verify the authenticity, type, and completeness of the uploaded document.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a strict compliance officer. Your job is to ensure the document being analyzed "
        "is an actual corporate financial report or valid filing, checking for standard formatting "
        "and rejecting non-financial documents immediately."
    ),
    tools=[read_data_tool],
    llm=gemini_llm,
    max_iter=2,
    max_rpm=10,  # <-- ADD THIS TO PREVENT RATE LIMITING
    allow_delegation=False
)
investment_advisor = Agent(
    role="Strategic Investment Advisor",
    goal="Provide objective, compliance-aware investment themes based on the analyst's data.",
    verbose=True,
    backstory=(
        "You are a conservative, SEC-compliant investment strategist. You synthesize financial "
        "metrics into broad market themes. You strictly avoid giving personal financial advice "
        "and you always include disclaimers about market risks."
    ),
    # 👇 REMOVED THE TOOL - it will rely on the Analyst's output
    llm=gemini_llm,
    max_iter=2,
    allow_delegation=False
)

risk_assessor = Agent(
    role="Enterprise Risk Assessment Expert",
    goal="Identify and quantify potential financial, operational, and market risks from the data provided.",
    verbose=True,
    backstory=(
        "You specialize in corporate risk mitigation. You look past the top-line revenue to find "
        "supply chain vulnerabilities, debt burdens, and operational inefficiencies. You are balanced "
        "and data-driven."
    ),
    # 👇 REMOVED THE TOOL
    llm=gemini_llm,
    max_iter=2,
    allow_delegation=False
)