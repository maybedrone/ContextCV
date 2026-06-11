"""Agent nodes: supervisor, researcher, analyzer, writer, and the tool router."""
from langchain_core.messages import SystemMessage

from src.config import supervisor_llm, worker_llm, researcher_llm
from src.state import JobAppState
from src.state import TailoredCV


def Supervisor(state: JobAppState) -> JobAppState:
    """Deterministic routing based on what's complete in state.
    Routes researcher -> analyzer -> writer in sequence, then FINISH."""
    if not state.get("research"):
        nxt = "researcher"
    elif not state.get("analysis"):
        nxt = "analyzer"
    elif not state.get("cv_tailored"):
        nxt = "writer"
    else:
        nxt = "FINISH"
    print(f"[SUPERVISOR] -> {nxt}")
    return {"next": nxt}


def Researcher(state: JobAppState) -> JobAppState:
    """Searches the web for company info, then summarizes into state['research']."""
    system = SystemMessage(content=f"""You are a company researcher. Identify the company from the job description below, then research that company.

    IMPORTANT RULES:
    - Make only ONE search at a time. Never request multiple searches in a single response.
    - Only use the duckduckgo_results_json tool. No other tools exist.
    - Start with one search for the company overview. After you see results, you may make ONE more search if needed.
    - After at most two searches, STOP searching and write a plain-text summary of what you learned about the company (its business, products, tech stack, and culture).
    - Do NOT search for the job posting itself — focus on the company.

    Job Description:
    {state['jd']}
    """)

    messages = [system] + state["messages"]
    response = researcher_llm.invoke(messages)

    # Tool call → pass along, research not done yet
    if response.tool_calls:
        return {"messages": [response]}

    return {"messages": [response], "research": response.content}


def Analyzer(state: JobAppState) -> JobAppState:
    """Compares the CV against the JD using research context.
    Identifies matches, gaps, and emphasis; saves into state['analysis']."""
    prompt = f"""You are a career analyst. Compare the candidate's CV against the job description.

    Job Description:
    {state['jd']}

    Candidate CV:
    {state['cv']}

    Company Research:
    {state['research']}

    Produce a structured analysis covering:
    1. Strong matches — where the CV directly meets JD requirements
    2. Gaps — JD requirements the CV does not address
    3. Emphasis — which existing CV points to highlight for this specific role

    Be specific and honest."""

    response = worker_llm.invoke([SystemMessage(content=prompt)])
    return {"messages": [response], "analysis": response.content}


def Writer(state: JobAppState) -> JobAppState:
    """Tailors the CV to the JD using the analysis; saves into state['cv_tailored']."""
    structured_writer = worker_llm.with_structured_output(TailoredCV)
    
    prompt = f"""You are a professional CV writer. Tailor the candidate's CV for this specific role.

    Job Description:
    {state['jd']}

    Original CV:
    {state['cv']}

    Analysis (matches, gaps, what to emphasize):
    {state['analysis']}

    Produce a tailored version of the CV that:
    1. Reorders and rewrites bullet points to emphasize relevant experience
    2. Mirrors keywords from the job description naturally
    3. Keeps everything truthful — do not invent experience
    4. Stays concise and professional

    Return the tailored CV as structured data: name, contact, summary, and a list of sections each with a heading and bullet points."""

    result = structured_writer.invoke([SystemMessage(content=prompt)])
    return {"cv_tailored": result.model_dump()}  # store as dict


def should_continue(state: JobAppState) -> str:
    """Router for the researcher's tool loop."""
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "end"