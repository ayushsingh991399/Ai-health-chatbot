from langgraph.graph import StateGraph, START, END

from state import HealthState

from function import (
    ask_topic,
    tavily_search,
    summarize,
    display_summary,
    ready_check,
    generate_quiz,
    ask_quiz,
    receive_answer,
    grade_answer,
    display_feedback,
    continue_chat,
    reset_state,
)


def quiz_router(state):

    ready = state.get("ready", "").strip().lower()

    if ready == "yes":
        return "generate_quiz"

    elif ready == "no":
        return "continue"

    return END


def continue_router(state):

    choice = state.get("continue_chat", "").strip().lower()

    if choice == "yes":
        return "reset"

    elif choice == "no":
        return END

    return END

builder = StateGraph(HealthState)


builder.add_node("ask_topic", ask_topic)
builder.add_node("tavily_search", tavily_search)
builder.add_node("summarize", summarize)
builder.add_node("display_summary", display_summary)
builder.add_node("ready_check", ready_check)
builder.add_node("generate_quiz", generate_quiz)
builder.add_node("ask_quiz", ask_quiz)
builder.add_node("receive_answer", receive_answer)
builder.add_node("grade_answer", grade_answer)
builder.add_node("display_feedback", display_feedback)
builder.add_node("continue_chat", continue_chat)
builder.add_node("reset_state", reset_state)
builder.add_edge(START, "ask_topic")



builder.add_edge("ask_topic", "tavily_search")
builder.add_edge("tavily_search", "summarize")
builder.add_edge("summarize", "display_summary")
builder.add_edge("display_summary", "ready_check")

builder.add_conditional_edges(
    "ready_check",
    quiz_router,
    {
        "generate_quiz": "generate_quiz",
        "continue": "continue_chat",
        END: END,
    },
)
builder.add_edge("generate_quiz", "ask_quiz")
builder.add_edge("ask_quiz", "receive_answer")
builder.add_edge("receive_answer", "grade_answer")
builder.add_edge("grade_answer", "display_feedback")
builder.add_edge("display_feedback", "continue_chat")
builder.add_conditional_edges(
    "continue_chat",
    continue_router,
    {
        "reset": "reset_state",
        END: END,
    },
)
builder.add_edge("reset_state", "ask_topic")


# Compile

graph = builder.compile()