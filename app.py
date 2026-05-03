import os
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# LangChain & Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================

st.set_page_config(
    page_title="Civic Assistant",
    page_icon="🗳️",
    layout="centered"
)

# ==========================================
# CACHED DATA & RESOURCE FUNCTIONS
# ==========================================

@st.cache_resource
def get_llm():
    """Initializes the Gemini LLM strictly configured for neutral civic duty."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "YOUR_GOOGLE_API_KEY_HERE":
         return None
    
    # Use gemini-2.5-flash as the older 1.5 models are deprecated and cause 404 errors
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.0 # Low temperature for factual consistency
    )

@st.cache_data
def fetch_election_dates() -> pd.DataFrame:
    """
    Fetches mock election dates structured as expected.
    """
    today = datetime.now()
    events = [
        {"title": "Registration Deadline", "date": (today + timedelta(days=15)).strftime("%B %d, %Y"), "description": "Last day to register to vote for the upcoming general election. Make sure to bring your proof of residence if registering in person."},
        {"title": "Early Voting Begins", "date": (today + timedelta(days=20)).strftime("%B %d, %Y"), "description": "Polling locations open for early in-person voting. Bring a valid photo ID."},
        {"title": "Mail-in Ballot Request Deadline", "date": (today + timedelta(days=25)).strftime("%B %d, %Y"), "description": "Last day to request an absentee or mail-in ballot. You can request this online or via your local election office."},
        {"title": "Election Day", "date": (today + timedelta(days=35)).strftime("%B %d, %Y"), "description": "General Election Day. Polls are open from 7 AM to 8 PM. If you are in line by 8 PM, you are allowed to vote."}
    ]
    return pd.DataFrame(events)

def generate_voter_checklist(first_time: str, vote_method: str) -> list:
    """Generates a list of checklist items based on user circumstances."""
    checklist = [
        "Verify your voter registration status online.",
        "Locate your designated polling place or ballot drop box."
    ]
    if first_time == "Yes":
        checklist.append("Bring a valid form of photo ID (often required for first-time voters).")
        checklist.append("Review a sample ballot online before heading out.")
    
    if vote_method == "Absentee" or vote_method == "Mail-in":
        checklist.append("Request your absentee/mail-in ballot before the deadline.")
        checklist.append("Read instructions carefully for signing and sealing the envelope.")
        checklist.append("Mail the ballot early, or drop it off at an official secure dropbox.")
    else:
        checklist.append("Check the polling hours and plan what time you will vote.")
    
    return checklist

# ==========================================
# MAIN UI
# ==========================================

def main():
    st.title("🗳️ Civic Assistant")
    st.subheader("Your interactive guide to the election process, timelines, and voting steps.")

    # --- FEATURE 1: The Interactive Election Timeline ---
    st.header("📅 Upcoming Election Timeline")
    st.info("Click on any date below to see what you need to do and what documents to prepare.")
    
    df_events = fetch_election_dates()
    
    for _, row in df_events.iterrows():
        with st.expander(f"{row['date']}: {row['title']}"):
            st.write(row['description'])

    st.divider()

    # --- FEATURE 2: Personalized Voter Guide Generator ---
    st.header("📝 Personalized Voter Guide")
    st.write("Answer a few quick questions to get your customized to-do list.")
    
    is_first_time = st.radio("Are you a first-time voter?", ("Yes", "No"))
    vote_method = st.selectbox("How do you plan to vote?", ("In-person", "Absentee", "Mail-in"))
    
    if st.button("Generate My Checklist"):
        checklist = generate_voter_checklist(is_first_time, vote_method)
        
        # Display instantly inside an st.success box
        success_msg = "**Here is your step-by-step checklist:**\n\n"
        for i, item in enumerate(checklist, 1):
            success_msg += f"{i}. {item}\n"
        st.success(success_msg)

    st.divider()

    # --- FEATURE 3: The Civic Oracle Chatbot ---
    st.header("💬 Civic Oracle")
    st.write("Ask a question about voting mechanics, registration, or election rules.")
    
    llm = get_llm()
    if not llm:
        st.warning("⚠️ Google Gemini API Key is missing or invalid. Please update the `.env` file.")
        return
        
    prompt_template = PromptTemplate(
        input_variables=["question"],
        template="""
You are the "Civic Oracle", an expert, strictly neutral, and helpful assistant focused ONLY on the mechanics and processes of elections and voting in the United States.

STRICT RULES:
1. You MUST NOT mention, endorse, criticize, or discuss any specific political candidate, public figure, political party, or specific legislation/policy.
2. If the user asks about candidates, opinions, who to vote for, or partisan topics, you MUST politely decline and state: "I am here to help with the voting process only, not political opinions."
3. Keep your answers clear, accessible, step-by-step, and factual.

User Question: {question}
Answer:
"""
    )
    
    chain = prompt_template | llm

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if user_question := st.chat_input("Ask a question about voting..."):
        # Display user message in chat message container
        st.chat_message("user").markdown(user_question)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_question})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Checking civic rules..."):
                try:
                    response = chain.invoke({"question": user_question.strip()})
                    answer = response.content
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
