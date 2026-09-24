# news-chatbot
This is an RAG application based on LangChain and Streamlit.
To run this application, do the following steps:
1. Download ollama at https://ollama.com/download
2. Install and run ollama
3. Create `config.py` and add `HEADER={your browser header}`
4. `streamlit run deploy_ui.py`

# Email summary line bot
This is a service that uses Gemini to summarize ariticles emailed from Bloomberg and send it to line users.
- Enable Gmail API
- Go to Google AI Studio and create a Gemini API key.
- Go to Line Developers and create a channel.
- In `config.py` fill the followings
    ```
    GEMINI_API_KEY
    LINE_CHANNEL_ACCESS_TOKEN
    LINE_CHANNEL_SECRET
    ```
- `python messgage_service.py`