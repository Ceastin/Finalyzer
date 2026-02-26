from crewai import Task
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import read_data_tool

verification = Task(
    description="Verify the file type at {file_path} and produce a short verification summary.",
    expected_output="File type, page count, first-page snippet, and confirmation if it's a valid financial document.",
    agent=verifier,
    tools=[read_data_tool],
    async_execution=False
)

analyze_financial_document = Task(
    description=(
        "Analyze the supplied financial document (path: {file_path}) and answer the user's query: {query}. "
        "Extract key financial metrics (revenue, net income, cashflow, major changes)."
    ),
    expected_output="Concise summary, bullet points of key metrics, and noted material events.",
    agent=financial_analyst,
    tools=[read_data_tool],
    async_execution=False,
)

investment_analysis = Task(
    description="Take the extracted metrics provided by the financial analyst and provide thematic, compliance-aware investment ideas.",
    expected_output="High-level themes, supporting evidence from the analyst's data, and strict regulatory disclaimers.",
    agent=investment_advisor,
    # No tools needed! It reads the output from analyze_financial_document
    async_execution=False,
)

risk_assessment = Task(
    description="Produce a risk assessment based on the financial analyst's extracted data and propose mitigations.",
    expected_output="Balanced risk checklist and suggested analyses to perform next.",
    agent=risk_assessor,
    # No tools needed!
    async_execution=False,
)