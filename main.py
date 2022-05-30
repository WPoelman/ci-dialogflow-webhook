from copy import copy
from typing import Any, Dict, List
from fastapi import Body, FastAPI
from pydantic import BaseModel
import json
import random

app = FastAPI()

DEFAULT_RESPONSE = "I did not get that."
CHAPTER_PLACEHOLDER = "$$"

# NOTE: our "db" is highly inefficient and dumb. We mainly use this approach
# since it's a demo!
with open("data/db.json") as f:
    DB = json.load(f)


def match(a: str, b: str):
    return a.lower().strip() == b.lower().strip()


def ensure_str(item):
    if isinstance(item, list):
        return item[0]
    return item


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
    result = {"simpleResponse": {"textToSpeech": text, "displayText": text}}
    return result


def books_by_author_handler(payload):
    # author
    if not (author := payload["queryResult"]["parameters"].get("author", None)):
        return None

    titles = [book["title"] for book in DB if match(book["author"], author)]

    if len(titles) == 0:
        return None

    msg = f"The books for this author are: {', '.join(titles)}"

    return create_tts_response(msg)


def play_book_author_handler(payload):
    # author
    if not (author := payload["queryResult"]["parameters"].get("author", None)):
        return None

    books = [book for book in DB if match(book["author"], author)]

    if len(books) == 0:
        return None

    book = random.choice(books)
    mp3_url = book["mp3url"].replace(CHAPTER_PLACEHOLDER, "01")

    return [
        create_tts_response(f"Now playing {book['title']}"),
        create_mp3_response(mp3_url, book["title"], book["iconurl"]),
    ]


def play_book_genre_handler(payload):
    # genre
    if not (genre := payload["queryResult"]["parameters"].get("genre", None)):
        return None

    books = [book for book in DB if any(
        match(genre, g) for g in book["genres"])]

    if len(books) == 0:
        return None

    book = random.choice(books)
    mp3_url = book["mp3url"].replace(CHAPTER_PLACEHOLDER, "01")

    return [
        create_tts_response(f"Now playing {book['title']}"),
        create_mp3_response(mp3_url, book["title"], book["iconurl"]),
    ]


def number_of_chapters_handler(payload):
    # current_book
    session = payload['session']
    context_key = f'{session}/contexts/book_title_context'
    book_title = None

    for context in payload['queryResult']['outputContexts']:
        if context['name'] == context_key:
            if book_title := context['parameters'].get('book_title', None):
                break

    if not book_title:
        return None

    chapters = None
    for book in DB:
        if match(book["title"], book_title):
            chapters = book["chapters"]
            break

    if not chapters:
        return None

    msg = f"{book_title} has {chapters} chapters."

    return create_tts_response(msg)


def author_of_book_title_handler(payload):
    # book_title
    if not (book_title := payload["queryResult"]["parameters"].get("book_title", None)):
        return None

    book_title = ensure_str(book_title)

    author = None
    for book in DB:
        if match(book["title"], book_title):
            author = book["author"]
            break

    if not author:
        return None

    msg = f"{author} is the author of {book_title}."

    return create_tts_response(msg)


def present_books_with_genre_handler(payload):
    # genre
    if not (genre := payload["queryResult"]["parameters"].get("genre", None)):
        return None

    titles = [
        book["title"] for book in DB if any(match(genre, g) for g in book["genres"])
    ]

    if len(titles) == 0:
        return None

    msg = f"You have the following books with genre {genre}: {', '.join(titles)}."

    return create_tts_response(msg)


def play_book_title_handler(payload):
    # book_title
    if not (book_title := payload["queryResult"]["parameters"].get("book_title", None)):
        return None

    book = None
    for b in DB:
        if match(b["title"], book_title):
            book = b
            break

    if not book:
        return None

    mp3_url = book["mp3url"].replace(CHAPTER_PLACEHOLDER, "01")

    return [
        create_tts_response(f"Now playing {book['title']}"),
        create_mp3_response(mp3_url, book["title"], book["iconurl"]),
    ]


def book_genre_handler(payload):
    # current_book
    # TODO: this probably needs to come from the context, not sure though:
    #   payload["queryResult"]["outputContexts"]
    if not (current_book := payload["queryResult"]["parameters"].get("current_book", None)):
        return None

    genres = None
    for book in DB:
        if match(book["title"], current_book):
            genres = book["genres"]
            break

    if not genres:
        return None

    item = "genres" if len(genres) > 1 else "genre"
    msg = f"{current_book} has {item}: {', '.join(genres)}."

    return create_tts_response(msg)


def start_reading_from_chapter_handler(payload):
    # chapter_number
    session = payload['session']
    context_key = f'{session}/contexts/book_title_context'
    book_title, chapter_number = None, None

    for context in payload['queryResult']['outputContexts']:
        if context['name'] == context_key:
            book_title = context['parameters'].get('book_title', None)
            chapter_number = context['parameters'].get('chapter_number', None)
            if book_title and chapter_number:
                break

    if (not book_title) or (not chapter_number):
        return None

    book = None
    for b in DB:
        if match(b["title"], book_title):
            book = b
            break

    if not book:
        return None

    chapter = int(chapter_number)
    if (chapter > book["chapters"]) or (chapter < 1):
        return None

    # NOTE: currently we assume chapters range from 01-99!
    mp3_url = book["mp3url"].replace(CHAPTER_PLACEHOLDER, f"{chapter:02d}")

    return [
        create_tts_response(f"Now playing chapter {chapter}"),
        create_mp3_response(mp3_url, book["title"], book["iconurl"]),
    ]


def progress_book_handler(payload):
    # current_book
    # TODO: we also need to know how far along the mp3 file is, again context?
    if not (current_book := payload["queryResult"]["parameters"].get("current_book", None)):
        return None
    if not (minutes_played := payload["queryResult"]["parameters"].get("minutes_played", None)):
        return None

    book = None
    for b in DB:
        if match(b["title"], current_book):
            book = b
            break

    if not book:
        return None

    progress = int(100 * (int(minutes_played) / book["runtime"]))
    msg = f"You are {progress}% into {current_book}."

    return create_tts_response(msg)


def time_to_finish_handler(payload):
    # current_book
    # TODO: we also need to know how far along the mp3 file is, again context?
    if not (current_book := payload["queryResult"]["parameters"].get("current_book", None)):
        return None
    if not (minutes_played := payload["queryResult"]["parameters"].get("minutes_played", None)):
        return None

    book = None
    for b in DB:
        if match(b["title"], current_book):
            book = b
            break

    if not book:
        return None

    left = book["runtime"] - int(minutes_played)
    msg = f"{current_book} has {left} minutes left."

    return create_tts_response(msg)


def unread_chapters_handler(payload):
    # NO PARAMETERS

    return None


def available_books_handler(payload):
    # NO PARAMETERS
    titles = [book["title"] for book in DB]
    msg = f"You have the following books available: {', '.join(titles)}"

    return create_tts_response(msg)


def summarize_book_handler(payload):
    # book_title
    if not (book_title := payload["queryResult"]["parameters"].get("book_title", None)):
        return None

    book_title = ensure_str(book_title)

    summary = None
    for b in DB:
        if match(b["title"], book_title):  # Note: index to avoid data type mismatch (str/list)
            summary = b["summary"]
            break

    if not summary:
        return None

    msg = f"Here is a summary of {book_title}: {summary}."

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
    "start_reading_from_chapter": start_reading_from_chapter_handler,
    "progress_book": progress_book_handler,
    "time_to_finish": time_to_finish_handler,
    "unread_chapters": unread_chapters_handler,
    "available_books": available_books_handler,
    "summarize_book": summarize_book_handler,
}


@app.post("/")
def read_root(payload: dict = Body(...)):
    intent_name = payload["queryResult"]["intent"]["displayName"]
    # NOTE: payload["queryResult"]["outputContexts"] for contexts

    print(f"GOT INTENT: {intent_name}\n")
    print(f"GOT payload: {json.dumps(payload, indent=2)}\n")
    if not (items := INTENTS.get(intent_name, lambda _: None)(payload)):
        fallback_msg = payload["queryResult"].get(
            "fulfillmentText", DEFAULT_RESPONSE)
        items = create_tts_response(fallback_msg)

    # The final response expects a list of responses, so we assume the handlers
    # return a single item.
    if isinstance(items, dict):
        items = [items]

    result = {
        "payload": {
            "google": {
                "expectUserResponse": True,
                "richResponse": {
                    "items": items,
                    "suggestions": [{"title": "Exit"}]
                }
            }
        }
    }

    print(f"RESPONSE: {json.dumps(result, indent=2)}\n")

    return result
