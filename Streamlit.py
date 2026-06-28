import streamlit as st
from project import graph

st.set_page_config(
    page_title="HealthBot",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 AI HealthBot")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "stage" not in st.session_state:
    st.session_state.stage = "topic"

if "state" not in st.session_state:
    st.session_state.state = {}

# -------------------------
# Show Chat History
# -------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------
# Chat Input
# -------------------------

user_input = st.chat_input("Type here...")

if user_input:

    st.session_state.messages.append(
        {
            "role":"user",
            "content":user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # -----------------------
    # Stage 1
    # -----------------------

    if st.session_state.stage=="topic":

        state={
            "topic":user_input,
            "ready":""
        }

        result=graph.invoke(state)

        st.session_state.state=result

        reply=result["summary"]+"\n\n**Ready for Quiz? (yes/no)**"

        st.session_state.stage="ready"

    # -----------------------
    # Stage 2
    # -----------------------

    elif st.session_state.stage=="ready":

        if user_input.lower()=="yes":

            state=st.session_state.state
            state["ready"]="yes"

            result=graph.invoke(state)

            st.session_state.state=result

            reply=result["quiz_question"]

            st.session_state.stage="answer"

        else:

            reply="Would you like to learn another topic? (yes/no)"

            st.session_state.stage="continue"

    # -----------------------
    # Stage 3
    # -----------------------

    elif st.session_state.stage=="answer":

        state=st.session_state.state
        state["user_answer"]=user_input

        result=graph.invoke(state)

        st.session_state.state=result

        reply=result["feedback"]+"\n\nWould you like another topic? (yes/no)"

        st.session_state.stage="continue"

    # -----------------------
    # Stage 4
    # -----------------------

    elif st.session_state.stage=="continue":

        if user_input.lower()=="yes":

            st.session_state.state={}

            reply="Great 😊\n\nEnter another health topic."

            st.session_state.stage="topic"

        else:

            reply="Thank you for using HealthBot ❤️"

            st.session_state.stage="end"

    else:

        reply="Session Ended."

    st.session_state.messages.append(
        {
            "role":"assistant",
            "content":reply
        }
    )

    with st.chat_message("assistant"):
        st.markdown(reply)