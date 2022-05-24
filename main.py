from typing import Any, Dict, List
from fastapi import Body, FastAPI
from pydantic import BaseModel
import json

app = FastAPI()

DEFAULT_RESPONSE = [
    {"simpleResponse": {"textToSpeech": "I did not get that."}}
]

with open('data/db.json') as f:
    DB = json.load(f)


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


def create_tts_response(text: str):
    return {"simpleResponse": {"textToSpeech": text}}


def books_by_author_handler(payload):
    # author

    return DEFAULT_RESPONSE


def play_book_author_handler(payload):
    # author

    return DEFAULT_RESPONSE


def play_book_genre_handler(payload):
    # genre

    return DEFAULT_RESPONSE


def number_of_chapters_handler(payload):
    # current_book

    return DEFAULT_RESPONSE


def author_of_book_title_handler(payload):
    # book_title

    return DEFAULT_RESPONSE


def present_books_with_genre_handler(payload):
    # genre

    return DEFAULT_RESPONSE


def play_book_title_handler(payload):
    # book_title

    return DEFAULT_RESPONSE


def book_genre_handler(payload):
    # current_book

    return DEFAULT_RESPONSE


def go_to_chapter_handler(payload):
    # chapter_number

    # Here we need to extract the information from the request and find the
    # correct information for it.
    # mp3_url = "https://ia800603.us.archive.org/14/items/annakarenina_mas_1202_librivox/annakarenina_001_tolstoy.mp3"
    # icon_url = "https://ia601601.us.archive.org/26/items/LibrivoxCdCoverArt15/anna_karenina_1202.jpg"
    # book_title = "Anna Karenina"
    #
    # response = create_mp3_response(mp3_url, book_title, icon_url)
    return DEFAULT_RESPONSE


def progress_book_handler(payload):
    # current_book

    return DEFAULT_RESPONSE


def time_to_finish_handler(payload):
    # current_book

    return DEFAULT_RESPONSE


def unread_chapters_handler(payload):
    # NO PARAMETERS

    return DEFAULT_RESPONSE


def available_books_handler(payload):
    # NO PARAMETERS

    return DEFAULT_RESPONSE


INTENTS = {
    "books_by_author": books_by_author_handler,
    "play_book_author": play_book_author_handler,
    "play_book_genre": play_book_genre_handler,
    "number_of_chapters": number_of_chapters_handler,
    "author_of_book_title": author_of_book_title_handler,
    "present_books_with_genre": present_books_with_genre_handler,
    "play_book_title": play_book_title_handler,
    "book_genre": book_genre_handler,
    "go_to_chapter": go_to_chapter_handler,
    "progress_book": progress_book_handler,
    "time_to_finish": time_to_finish_handler,
    "unread_chapters": unread_chapters_handler,
}


@app.post("/")
def read_root(payload: dict = Body(...)):
    intent_name = payload["queryResult"]["intent"]["displayName"]
    # TODO: payload["queryResult"]["outputContexts"] for contexts

    items = INTENTS.get(intent_name, lambda _: DEFAULT_RESPONSE)(payload)

    result = {
        "payload": {
            "google": {
                "expectUserResponse": False,  # TODO: make this dynamic per intent?
                "richResponse": {"items": items},
            }
        }
    }

    return result
