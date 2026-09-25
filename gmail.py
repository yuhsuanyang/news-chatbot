from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google import genai
import os
import base64
import json
from config import GEMINI_API_KEY
from pydantic import BaseModel

client = genai.Client(api_key=GEMINI_API_KEY)


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


if not os.path.exists("token.json"):
    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json",
        SCOPES,
    )
    creds = flow.run_local_server(port=0)
    print(creds)
    with open("token.json", "w") as token:
        token.write(creds.to_json())

else:
    creds = Credentials.from_authorized_user_file(
        "token.json",
        SCOPES,
    )

class Section(BaseModel):
    title: str
    items: list[str]


class Analysis(BaseModel):
    title: str
    sections: list[Section]

#i print(msg["payload"]["headers"])
# print(msg["payload"]["body"])
# print(msg["payload"]["parts"][0]["body"]["data"])
def decode_email_body(msg):
    if "parts" in msg["payload"]:
        for part in msg["payload"]["parts"]:
            if part["mimeType"] == "text/plain":
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
    else:
        return base64.urlsafe_b64decode(msg["payload"]["body"]["data"]).decode("utf-8")
# print(base64.urlsafe_b64decode(msg["payload"]["parts"][0]["body"]["data"]).decode("utf-8"))
def get_email_content(after_date):
    gmail = build("gmail", "v1", credentials=creds)
    results = gmail.users().messages().list(
        userId="me",
        q=f"from:noreply@news.bloomberg.com after:{after_date}"
    ).execute()

    messages = results.get("messages", [])
    print(f"Found {len(messages)}")

    content = []
    for msg in messages:
        msg = gmail.users().messages().get(userId="me", id=msg["id"]).execute()
        email_body = decode_email_body(msg)
        content.append(email_body)
    return content

def get_gemini_response(content) -> dict:
    prompt = f"""
        你是一個有在研究總體經濟的專家，請你幫我分析以下的文章內容，整理出重點，結合美股昨天的表現，
        分析最近總體經濟走向以及以及對台灣股市的影響。
        回答時請使用繁體中文。
    """
    for i, text in enumerate(content):
        prompt += f"{i+1}. \n {text}"
        prompt += "-" * 50 + "\n"

    response = client.models.generate_content(
        model="gemini-pro-latest", 
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Analysis,
            )
        )
    return json.loads(response.text)