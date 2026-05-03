import os
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# LangChain & Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Google Calendar (using googleapiclient)
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Load environment variables
load_dotenv()

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================

st.set_page_config(
    page_title="Election Process & Timeline Assistant",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for high contrast and accessibility
st.markdown("""
<style>
    /* High contrast text */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #1E1E1E !important;
    }
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
        padding: 1rem;
    }
    .stAlert {
        border-radius: 8px;
    }
    /* Timeline styling */
    .timeline-event {
        padding: 10px;
        margin: 10px 0;
        border-left: 4px solid #0056b3;
        background-color: #f1f8ff;
        border-radius: 4px;
        color: #1E1E1E;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CACHED DATA & RESOURCE FUNCTIONS
# ==========================================

@st.cache_resource
def get_llm():
    """Initializes the Gemini LLM strictly configured for neutral civic duty."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "YOUR_GOOGLE_API_KEY_HERE":
         return None
    
    return ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=api_key,
        temperature=0.0 # Low temperature for factual consistency
    )

@st.cache_data
def fetch_election_dates() -> pd.DataFrame:
    """
    Fetches mock or real election dates. 
    In a fully authenticated environment, this would call Google Calendar API.
    Since we cannot guarantee OAuth setup in this isolated script, 
    we provide a robust mock structure that simulates the expected API response.
    """
    # NOTE: To connect to real Google Calendar, use:
    # service = build('calendar', 'v3', developerKey=os.getenv("GOOGLE_API_KEY"))
    # events = service.events().list(calendarId='en.usa#holiday@group.v.calendar.google.com').execute()
    
    # Mock data structured exactly as Pandas would parse API returns
    today = datetime.now()
    events = [
        {"title": "Voter Registration Deadline", "date": (today + timedelta(days=15)).strftime("%Y-%m-%d"), "description": "Last day to register to vote for the upcoming general election."},
        {"title": "Early Voting Begins", "date": (today + timedelta(days=20)).strftime("%Y-%m-%d"), "description": "Polling locations open for early in-person voting."},
        {"title": "Mail-in Ballot Request Deadline", "date": (today + timedelta(days=25)).strftime("%Y-%m-%d"), "description": "Last day to request an absentee or mail-in ballot."},
        {"title": "Election Day", "date": (today + timedelta(days=35)).strftime("%Y-%m-%d"), "description": "General Election Day. Polls are open from 7 AM to 8 PM."}
    ]
    df = pd.DataFrame(events)
    df['date'] = pd.to_datetime(df['date'])
    return df

def generate_voter_checklist(is_first_time: bool, is_absentee: bool, needs_accommodation: bool) -> list:
    """Generates a list of checklist items based on user circumstances."""
    checklist = [
        "Verify your voter registration status online.",
        "Check your assigned polling location."
    ]
    if is_first_time:
        checklist.append("Bring a valid form of ID (required for first-time voters in many states).")
        checklist.append("Review a sample ballot before heading to the polls.")
    if is_absentee:
        checklist.append("Request your absentee ballot before the deadline.")
        checklist.append("Carefully read the instructions for signing and sealing the ballot envelope.")
        checklist.append("Mail the ballot early or drop it at an official secure dropbox.")
    if needs_accommodation:
        checklist.append("Review the accessible voting options at your polling place (e.g., ballot marking devices).")
    
    return checklist

# ==========================================
# MAIN UI
# ==========================================

def main():
    st.title("🗳️ Election Process & Timeline Assistant")
    st.markdown("""
        **Welcome!** This accessible tool is designed to help you navigate the voting process smoothly. 
        It provides a timeline of important dates, a personalized voter checklist, and a secure AI assistant 
        to answer process-related questions.
    """)

    tab1, tab2, tab3 = st.tabs(["📅 Election Timeline", "📝 Personalized Voter Guide", "💬 Civic Oracle Chatbot"])

    # --- TAB 1: Timeline Viewer ---
    with tab1:
        st.header("Important Upcoming Dates")
        df_events = fetch_election_dates()
        
        st.markdown("Use the slider to filter events by date.")
        min_date = df_events['date'].min().date()
        max_date = df_events['date'].max().date()
        
        selected_date = st.slider(
            "Filter timeline up to:",
            min_value=min_date,
            max_value=max_date,
            value=max_date,
            format="YYYY-MM-DD"
        )
        
        filtered_df = df_events[df_events['date'].dt.date <= selected_date]
        
        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                st.markdown(f"""
                <div class="timeline-event">
                    <strong>{row['date'].strftime('%B %d, %Y')} - {row['title']}</strong><br>
                    {row['description']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No events found before the selected date.")

    # --- TAB 2: Voter Guide Form ---
    with tab2:
        st.header("Generate Your Voter Checklist")
        st.markdown("Please fill out this form to receive a customized checklist.")
        
        with st.form("voter_guide_form"):
            is_first_time = st.checkbox("I am a first-time voter.")
            is_absentee = st.checkbox("I plan to vote absentee or by mail.")
            needs_accommodation = st.checkbox("I require accessibility accommodations at the polling place.")
            
            submitted = st.form_submit_button("Generate Checklist")
            
        if submitted:
            st.subheader("Your Action Items:")
            checklist = generate_voter_checklist(is_first_time, is_absentee, needs_accommodation)
            for i, item in enumerate(checklist, 1):
                st.markdown(f"**{i}.** {item}")

    # --- TAB 3: Civic Oracle Chatbot ---
    with tab3:
        st.header("Civic Oracle Chatbot")
        st.markdown("""
            Ask questions about the **voting process**, **registration**, or **election mechanics**.
            *Note: This AI is strictly programmed to remain politically neutral and will not discuss specific candidates, parties, or policies.*
        """)
        
        llm = get_llm()
        if not llm:
            st.warning("⚠️ Google Gemini API Key is missing or invalid. Please update the `.env` file.")
            st.stop()
            
        # Define the strict neutral prompt
        prompt_template = PromptTemplate(
            input_variables=["question"],
            template="""
You are the "Civic Oracle", an expert, strictly neutral, and helpful assistant focused ONLY on the mechanics and processes of elections and voting in the United States.

STRICT RULES:
1. You MUST NOT mention, endorse, criticize, or discuss any specific political candidate, public figure, political party, or specific legislation/policy.
2. If the user asks about candidates, opinions, who to vote for, or partisan topics, you MUST politely decline and state that your role is strictly limited to explaining the voting process and mechanics.
3. Keep your answers clear, accessible, step-by-step, and factual.

User Question: {question}
Answer:
"""
        )
        chain = prompt_template | llm
        user_question = st.text_input("Enter your question here:", placeholder="e.g., How do I register to vote?")
        
        if st.button("Ask Oracle"):
            if user_question.strip() == "":
                st.error("Please enter a valid question.")
            else:
                with st.spinner("Consulting the Oracle..."):
                    try:
                        # Sanitize input (basic whitespace stripping)
                        sanitized_question = user_question.strip()
                        response = chain.invoke({"question": sanitized_question})
                        st.success("Response:")
                        st.write(response.content)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
