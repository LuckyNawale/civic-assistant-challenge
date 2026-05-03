# 🗳️ Election Process & Timeline Assistant

An interactive AI-powered assistant designed to help users understand the election process, timelines, and steps in an easy-to-follow way. Built for Google Cloud Run, utilizing Streamlit and LangChain with the Google Gemini API.

## 🌟 Features

- **Interactive Timeline Viewer**: A visual step-by-step slider of election dates.
- **Voter Guide Form**: A dynamic checklist generator based on user status (e.g., absentee, first-time voter, accessibility needs).
- **"Civic Oracle" Chatbot**: A LangChain-powered Google Gemini AI agent that strictly answers civic and process-only questions in a politically neutral manner.

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Python)
- **AI & Logic**: LangChain + Google Gemini API
- **Data Structuring**: Pandas
- **Deployment**: Google Cloud Run / Docker

## 🚀 Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LuckyNawale/civic-assistant-challenge.git
   cd civic-assistant-challenge
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Set your environment variables:**
   Create a `.env` file in the root directory and add your Google API key:
   ```env
   GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
   ```

4. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

## ☁️ Cloud Run Deployment

This project is packaged with a `Dockerfile` specifically configured to expose port `8080` for Google Cloud Run.

1. Build and push the Docker image to Google Artifact Registry.
2. Deploy to Cloud Run, ensuring you pass the `GOOGLE_API_KEY` as a secret or environment variable during deployment.
