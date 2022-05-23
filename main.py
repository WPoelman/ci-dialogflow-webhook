from typing import Any, Dict, List
from fastapi import Body, FastAPI
from pydantic import BaseModel

app = FastAPI()

DEFAULT_RESPONSE = [
    {"simpleResponse": {"textToSpeech": "I did not get that."}}
]


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


def read_preface_handler(request):
    # book_title

    return DEFAULT_RESPONSE


def books_by_author_handler(request):
    # author

    return DEFAULT_RESPONSE


def look_up_search_word_handler(request):
    # search_word

    return DEFAULT_RESPONSE


def remove_favorite_book_handler(request):
    # book_title

    return DEFAULT_RESPONSE


def play_book_author_handler(request):
    # author

    return DEFAULT_RESPONSE


def play_book_genre_handler(request):
    # genre

    return DEFAULT_RESPONSE


def author_of_book_title_handler(request):
    # book_title

    return DEFAULT_RESPONSE


def present_books_with_genre_handler(request):
    # genre

    return DEFAULT_RESPONSE


def opinion_positive_handler(request):
    # person

    return DEFAULT_RESPONSE


def play_book_title_handler(request):
    # book_title

    return DEFAULT_RESPONSE


def go_to_chapter_handler(request):
    # chapter_number

    # Here we need to extract the information from the request and find the
    # correct information for it.
    mp3_url = "https://ia800603.us.archive.org/14/items/annakarenina_mas_1202_librivox/annakarenina_001_tolstoy.mp3"
    icon_url = "https://ia601601.us.archive.org/26/items/LibrivoxCdCoverArt15/anna_karenina_1202.jpg"
    book_title = "Anna Karenina"

    response = create_mp3_response(mp3_url, book_title, icon_url)

    return response


def opinion_negative_handler(request):
    # character_name
    # book_title
    # chapter_number
    pass


INTENTS = {
    "read_preface": read_preface_handler,
    "books_by_author": books_by_author_handler,
    "look_up_search_word": look_up_search_word_handler,
    "remove_favorite_book": remove_favorite_book_handler,
    "play_book_author": play_book_author_handler,
    "play_book_genre": play_book_genre_handler,
    "author_of_book_title": author_of_book_title_handler,
    "present_books_with_genre": present_books_with_genre_handler,
    "opinion_positive": opinion_positive_handler,
    "play_book_title": play_book_title_handler,
    "go_to_chapter": go_to_chapter_handler,
    "opinion_negative": opinion_negative_handler,
}


@app.post("/")
def read_root(payload: dict = Body(...)):
    intent_name = payload["queryResult"]["intent"]["name"]

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
