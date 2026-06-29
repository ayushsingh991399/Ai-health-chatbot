from config import llm, search_tool


def ask_topic(state):
    return state


def tavily_search(state):

    results = search_tool.invoke(state["topic"])

    return {
        "search_results": results
    }

def summarize(state):

    prompt = f"""
    You are a helpful medical assistant.

    Summarize the following medical information in simple,
    patient-friendly language.

    Include:
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

def display_summary(state):

    return {
        "summary": state["summary"]
    }


def ready_check(state):

    return {
        "ready": state.get("ready", "").strip().lower()
    }


def generate_quiz(state):

    prompt = f"""
    You are a medical Teacher.

    Based on the summary below, generate ONE simple
    comprehension question for the patient.
    Summary:
    {state["summary"]}

    Return only the question.
    """

    response = llm.invoke(prompt)

    return {
        "quiz_question": response.content
    }
def ask_quiz(state):

    return {
        "quiz_question": state["quiz_question"]
    }

def receive_answer(state):

    return {
        "user_answer": state.get("user_answer", "")
    }


def grade_answer(state):

    prompt = f"""
        You are a medical instructor.

        Summary:
        {state["summary"]}

        Question:
        {state["quiz_question"]}

        Patient's Answer:
        {state["user_answer"]}

        Evaluate the patient's answer.

        Return in this format:
        
        Grade:
        first check the answer is correct /partially/correct/incorrect,
        on the bases of this provide the grade A/B/C.
        

        Explanation:
        Explain why.

        Citation:
        Mention the relevant part of the summary.
    """

    response = llm.invoke(prompt)

    return {
        "feedback": response.content
    }

def display_feedback(state):

    return {
        "feedback": state["feedback"]
    }


def continue_chat(state):

    return {
        "continue_session": state.get(
            "continue_chat",
            ""
        ).strip().lower()
    }


def reset_state(state):

    return {
        "topic": "",
        "search_results": [],
        "summary": "",
        "ready": "",
        "quiz_question": "",
        "user_answer": "",
        "feedback": "",
        "continue_chat": ""
    }
