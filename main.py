from typing import Any, Dict, List
from fastapi import Body, FastAPI
from pydantic import BaseModel
import json
import random

app = FastAPI()

DEFAULT_RESPONSE = [
    {"simpleResponse": {"textToSpeech": "I did not get that."}}
]
CHAPTER_PLACEHOLDER = "$$"

# NOTE: our "db" is highly inefficient and dumb. We mainly use this since it's
# a demo!
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
    result = {
        "simpleResponse": {
            "textToSpeech": text,
            "displayText": text,
        }
    }
    return result


def books_by_author_handler(payload):
    # author
    if not (author := payload["queryResult"]["parameters"].get("author", None)):
        return DEFAULT_RESPONSE

    titles = [
        book['title'] for book in DB if book['author'] == author
    ]

    if len(titles) == 0:
        return DEFAULT_RESPONSE

    msg = f"The books for this author are: {', '.join(titles)}"

    return create_tts_response(msg)


def play_book_author_handler(payload):
    # author
    if not (author := payload["queryResult"]["parameters"].get("author", None)):
        return DEFAULT_RESPONSE

    books = [book for book in DB if book['author'] == author]

    if len(books) == 0:
        return DEFAULT_RESPONSE

    book = random.choice(books)
    mp3_url = book['mp3url'].replace(CHAPTER_PLACEHOLDER, "01")

    return create_mp3_response(mp3_url, book['title'], book['iconurl'])


def play_book_genre_handler(payload):
    # genre
    if not (genre := payload["queryResult"]["parameters"].get("genre", None)):
        return DEFAULT_RESPONSE

    books = [book for book in DB if genre in book['genres']]

    if len(books) == 0:
        return DEFAULT_RESPONSE

    book = random.choice(books)
    mp3_url = book['mp3url'].replace(CHAPTER_PLACEHOLDER, "01")

    return create_mp3_response(mp3_url, book['title'], book['iconurl'])


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
    titles = [book['title'] for book in DB]
    msg = f"You have the following books available: {', '.join(titles)}"

    return create_tts_response(msg)


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
    "available_books": available_books_handler,
}


@app.post("/")
def read_root(payload: dict = Body(...)):
    intent_name = payload["queryResult"]["intent"]["displayName"]
    # TODO: payload["queryResult"]["outputContexts"] for contexts

    print(f"GOT INTENT: {intent_name}\n")
    print(f"GOT INTENT: {payload}\n")

    items = INTENTS.get(intent_name, lambda _: DEFAULT_RESPONSE)(payload)
    # The final response expects a list of responses, but we might return a
    # single items from the handlers
    if isinstance(items, dict):
        items = [items]

    print(f"RESPONSE: {items}\n")

    result = {
        "payload": {
            "google": {
                "expectUserResponse": False,  # TODO: make this dynamic per intent?
                "richResponse": {"items": items},
            }
        }
    }

    return result
