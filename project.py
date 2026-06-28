from typing import TypedDict, List


class HealthState(TypedDict, total=False):
    # User Input
    topic: str

    # Tavily Search Results
    search_results: List

    # LLM Summary
    summary: str

    # Quiz Flow
    ready: str
    quiz_question: str
    user_answer: str

    # Evaluation
    feedback: str

    # Continue Session
    continue_session: str



import os
from dotenv import load_dotenv

from langchain_cohere import ChatCohere
from langchain_community.tools import TavilySearchResults

load_dotenv("config.env")

llm = ChatCohere(
    model="command-nightly",
    temperature=0.3
)

search_tool = TavilySearchResults(max_results=5)


# -------------------------------
# Node 1 : Ask Topic
# -------------------------------
def ask_topic(state):
    return state


# -------------------------------
# Node 2 : Tavily Search
# -------------------------------
def tavily_search(state):

    results = search_tool.invoke(state["topic"])

    return {
        "search_results": results
    }


# -------------------------------
# Node 3 : Summarize
# -------------------------------
def summarize(state):

    prompt = f"""
You are a medical assistant.

Summarize the following medical information in simple,
patient-friendly language.

Include

- What it is
- Symptoms
- Causes
- Treatment
- Prevention

Search Results:

{state["search_results"]}
"""

    response = llm.invoke(prompt)

    return {
        "summary": response.content
    }


# -------------------------------
# Node 4 : Display Summary
# -------------------------------
def display_summary(state):

    return {
        "summary": state["summary"]
    }


# -------------------------------
# Node 5 : Ready Check
# -------------------------------
def ready_check(state):

    return {
        "ready": state.get("ready", "")
    }


# -------------------------------
# Node 6 : Generate Quiz
# -------------------------------
def generate_quiz(state):

    prompt = f"""
Generate ONE multiple choice question from the summary.

Summary:

{state["summary"]}

Return only the question.
"""

    response = llm.invoke(prompt)

    return {
        "quiz_question": response.content
    }


# -------------------------------
# Node 7 : Ask Quiz
# -------------------------------
def ask_quiz(state):

    return {
        "quiz_question": state["quiz_question"]
    }


# -------------------------------
# Node 8 : Receive Answer
# -------------------------------
def receive_answer(state):

    return {
        "user_answer": state.get("user_answer", "")
    }


# -------------------------------
# Node 9 : Grade Answer
# -------------------------------
def grade_answer(state):

    prompt = f"""
Summary

{state['summary']}

Question

{state['quiz_question']}

User Answer

{state['user_answer']}

Evaluate the answer.

Return

Grade:

Explanation:
"""

    response = llm.invoke(prompt)

    return {
        "feedback": response.content
    }


# -------------------------------
# Node 10 : Display Feedback
# -------------------------------
def display_feedback(state):

    return {
        "feedback": state["feedback"]
    }


# -------------------------------
# Node 11 : Continue
# -------------------------------
def continue_chat(state):

    return {
        "continue_session": state.get("continue_session", "")
    }


# -------------------------------
# Node 12 : Reset
# -------------------------------
def reset_state(state):

    return {
        "topic": "",
        "search_results": [],
        "summary": "",
        "ready": "",
        "quiz_question": "",
        "user_answer": "",
        "feedback": "",
        "continue_session": ""
    }


from langgraph.graph import StateGraph, START, END


# -----------------------------
# Quiz Router
# -----------------------------
def quiz_router(state):

    if state.get("ready", "").lower() == "yes":
        return "generate_quiz"

    return "continue"


# -----------------------------
# Continue Router
# -----------------------------
def continue_router(state):

    if state.get("continue_session", "").lower() == "yes":
        return "reset"

    return END


builder = StateGraph(HealthState)


# -----------------------------
# Nodes
# -----------------------------
builder.add_node("ask_topic", ask_topic)
builder.add_node("tavily_search", tavily_search)
builder.add_node("summarize", summarize)
builder.add_node("display_summary", display_summary)
builder.add_node("ready_check", ready_check)
builder.add_node("generate_quiz", generate_quiz)
builder.add_node("ask_quiz", ask_quiz)
builder.add_node("receive_answer", receive_answer)
builder.add_node("grade", grade_answer)
builder.add_node("feedback", display_feedback)
builder.add_node("continue", continue_chat)
builder.add_node("reset", reset_state)


# -----------------------------
# Main Flow
# -----------------------------
builder.add_edge(START, "ask_topic")
builder.add_edge("ask_topic", "tavily_search")
builder.add_edge("tavily_search", "summarize")
builder.add_edge("summarize", "display_summary")
builder.add_edge("display_summary", "ready_check")


# -----------------------------
# Ready for Quiz?
# -----------------------------
builder.add_conditional_edges(
    "ready_check",
    quiz_router,
    {
        "generate_quiz": "generate_quiz",
        "continue": "continue",
    },
)


# -----------------------------
# Quiz Flow
# -----------------------------
builder.add_edge("generate_quiz", "ask_quiz")
builder.add_edge("ask_quiz", "receive_answer")
builder.add_edge("receive_answer", "grade")
builder.add_edge("grade", "feedback")
builder.add_edge("feedback", "continue")


# -----------------------------
# Continue?
# -----------------------------
builder.add_conditional_edges(
    "continue",
    continue_router,
    {
        "reset": "reset",
        END: END,
    },
)


# -----------------------------
# Restart
# -----------------------------
builder.add_edge("reset", "ask_topic")


graph = builder.compile()