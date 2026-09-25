from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, FRIEND_ID
from linebot.v3 import WebhookParser
from linebot.v3 .messaging import Configuration, MessagingApi, PushMessageRequest, TextMessage, ApiClient, FlexMessage, FlexContainer
from gmail import get_email_content, get_gemini_response
import datetime

cutoff_date = datetime.datetime.today() - datetime.timedelta(days=1)
date = datetime.datetime.strftime(cutoff_date, "%Y-%m-%d")
context = get_email_content(date)
if len(context) == 0:
    exit()
response = get_gemini_response(context)


config = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(channel_secret=LINE_CHANNEL_SECRET)
greeting = f"你好 這是{date} Bloomberg新聞整理與分析"

# import json
# with open("test.json", "r") as f:
    # response = json.load(f)
# 
content = {"type": "carousel", "contents": []}
for sec in response["sections"]:
    content["contents"].append(
        {
            "type": "bubble",
            "styles": {
                "header": {
                "backgroundColor": "#ebb434"
            }},
            "header":{
                "type": "box",
                "layout": "vertical",
                "contents":[
                    {
                        "type": "text",
                        "text": sec["title"] + "\n",
                        # "size": "lg",
                        "weight": "bold",
                        "wrap": True,
                    }

                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"{i + 1}. {item} \n",
                        "wrap": True,
                    } for i, item in enumerate(sec["items"])
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "size": "sm",
                "contents": [{"type": "text", "text": f"資料時間: {date}", "color": "#e0e0e0"}]
            }
        }
    )


with ApiClient(config) as api_client:
    line_bot_api = MessagingApi(api_client)
    for id_ in FRIEND_ID:
        line_bot_api.push_message(
            PushMessageRequest(
                to=id_,
                messages=[
                    TextMessage(
                        text=f"找到 {len(context)} 封來自Bloomberg 的新郵件"
                    )
                ]
            )
        )
        line_bot_api.push_message(
            PushMessageRequest(
                to=id_,
                messages=[
                    FlexMessage(
                        alt_text=greeting,
                        contents=FlexContainer.from_dict(content)
                    )
                ]
        ))