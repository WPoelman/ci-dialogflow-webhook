from fastapi import Body, FastAPI
from pydantic import BaseModel

app = FastAPI()


class IntentRequest(BaseModel):
    pass


@app.post("/")
def read_root(payload: dict = Body(...)):
    print(payload)
    result = {
        "payload": {
            "google": {
                "expectUserResponse": False,
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": f"Hello there, playing chapter {payload['queryResult']['parameters']['number']}"
                            }
                        },
                        {
                            "mediaResponse": {
                                "mediaType": "AUDIO",
                                "mediaObjects": [
                                    {
                                        "contentUrl": "https://ia800603.us.archive.org/14/items/annakarenina_mas_1202_librivox/annakarenina_001_tolstoy.mp3",
                                        "description": "Hello this is description",
                                        "icon": {
                                            "url": "https://ia601601.us.archive.org/26/items/LibrivoxCdCoverArt15/anna_karenina_1202.jpg",
                                            "accessibilityText": "Album cover of an ocean view",
                                        },
                                        "name": "BOOK BOOK BOOK",
                                    }
                                ],
                            }
                        },
                    ],
                },
            }
        }
    }

    return result

