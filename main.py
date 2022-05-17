from typing import Any, Dict, List
from fastapi import Body, FastAPI
from pydantic import BaseModel

app = FastAPI()

DEFAULT_RESPONSE = [{"simpleResponse": {"textToSpeech": "I did not get that."}}]


class IntentRequest(BaseModel):
    pass


def create_mp3_response(mp3_url: str, book_title: str, icon_url: str = None):
    result = {
        "mediaResponse": {
            "mediaType": "AUDIO",
            "mediaObjects": [
                {
                    "contentUrl": mp3_url,
                    "description": book_title,
                    "icon": {"url": icon_url, "accessibilityText": book_title},
                    "name": book_title,
                }
            ],
        }
    }
    return result


def chapter_handler(request):
    # Here we need to extract the information from the request and find the
    # correct information for it.
    mp3_url = "https://ia800603.us.archive.org/14/items/annakarenina_mas_1202_librivox/annakarenina_001_tolstoy.mp3"
    icon_url = "https://ia601601.us.archive.org/26/items/LibrivoxCdCoverArt15/anna_karenina_1202.jpg"
    book_title = "Anna Karenina"

    response = create_mp3_response(mp3_url, book_title, icon_url)

    return response


INTENTS = {
    "projects/cipaudiobooks-hwh9/agent/intents/7649237f-2b39-439d-8725-4723aa99ffa6": chapter_handler,
}


@app.post("/")
def read_root(payload: dict = Body(...)):
    intent_id = payload["queryResult"]["intent"]["name"]

    items = INTENTS.get(intent_id, lambda _: DEFAULT_RESPONSE)(payload)

    result = {
        "payload": {
            "google": {
                "expectUserResponse": False,  # TODO: make this dynamic per intent?
                "richResponse": {"items": items},
            }
        }
    }

    return result

