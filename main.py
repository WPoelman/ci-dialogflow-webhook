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

### Helpers ###


def match(a: str, b: str):
    return a.lower().strip() == b.lower().strip()


def ensure_str(item):
    if isinstance(item, list):
        return item[0]
    return item


def get_context_param(payload, context_name, param_name):
    """
    Gets the current book title from the context, if it's there and return our
    database entry for that book.
    """
    session = payload['session']
    context_key = f'{session}/contexts/{context_name}'

    param = None
    for context in payload['queryResult']['outputContexts']:
        if context['name'] == context_key:
            if param := context['parameters'].get(param_name, None):
                break

    return param


def get_current_book(payload):
    """
    Gets the current book title from the context, if it's there and return our
    database entry for that book.
    """
    if not (book_title := get_context_param(payload, 'book_title_context', 'book_title')):
        return None

    book = None
    for b in DB:
        if match(b["title"], book_title):
            book = b
            break

    return book


def get_param(payload, param_name: str):
    return payload["queryResult"]["parameters"].get(param_name, None)


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
    return {"simpleResponse": {"textToSpeech": text, "displayText": text}}


#### No parameters intents ###


def available_books_handler(payload):
    titles = [book["title"] for book in DB]
    msg = f"You have the following books available: {', '.join(titles)}"

    return create_tts_response(msg)


def number_of_books_handler(payload):
    msg = f"You have the following number of books available: {len(DB)}"

    return create_tts_response(msg)

#### Parameter intents ###


def books_by_author_handler(payload):
    if not (author := get_param(payload, 'author')):
        return None

    titles = [book["title"] for book in DB if match(book["author"], author)]

    if len(titles) == 0:
        return None

    return create_tts_response(f"The books for this author are: {', '.join(titles)}")


def play_book_author_handler(payload):
    if not (author := get_param(payload, 'author')):
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
    if not (genre := get_param(payload, "genre")):
        return None

    books = [
        book for book in DB
        if any(match(genre, g) for g in book["genres"])
    ]

    if len(books) == 0:
        return None

    book = random.choice(books)
    mp3_url = book["mp3url"].replace(CHAPTER_PLACEHOLDER, "01")

    return [
        create_tts_response(f"Now playing {book['title']}"),
        create_mp3_response(mp3_url, book["title"], book["iconurl"]),
    ]


def author_of_book_title_handler(payload):
    if not (book_title := get_param(payload, "book_title")):
        return None

    book_title = ensure_str(book_title)

    author = None
    for book in DB:
        if match(book["title"], book_title):
            author = book["author"]
            break

    if not author:
        return None

    return create_tts_response(f"{author} is the author of {book_title}.")


def present_books_with_genre_handler(payload):
    if not (genre := get_param(payload, "genre")):
        return None

    titles = [
        book["title"] for book in DB if any(match(genre, g) for g in book["genres"])
    ]

    if len(titles) == 0:
        return None

    msg = f"You have the following books with genre {genre}: {', '.join(titles)}."
    return create_tts_response(msg)


def play_book_title_handler(payload):
    if not (book_title := get_param(payload, "book_title")):
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


def summarize_book_handler(payload):
    if not (book_title := get_param(payload, 'book_title')):
        return None

    book_title = ensure_str(book_title)

    summary = None
    for b in DB:
        if match(b["title"], book_title):
            summary = b["summary"]
            break

    if not summary:
        return None

    return create_tts_response(f"Here is a summary of {book_title}: {summary}.")


def book_genre_handler(payload):
    if not (book_title := get_param(payload, 'book_title')):
        return None

    book_title = ensure_str(book_title)

    genres = None
    for b in DB:
        if match(b["title"], book_title):
            genres = b["genres"]
            break

    if not genres:
        return None

    item = "genres" if len(genres) > 1 else "genre"
    msg = f"{book_title} has {item}: {', '.join(genres)}."
    return create_tts_response(msg)


def start_reading_from_chapter_handler(payload):
    if not (book_title := get_param(payload, "book_title")):
        return None

    if not (chapter_number := get_param(payload, "chapter_number")):
        return None

    book_title = ensure_str(book_title)

    book = None
    for b in DB:
        if match(b["title"], book_title):
            book = b
            break

    if not book:
        return None

    chapter = int(chapter_number)
    if chapter < 1:
        return None

    if chapter > book["chapters"]:
        return create_tts_response(f"{book['title']} only has {book['chapters']} chapters!")

    # NOTE: currently we assume chapters range from 01-99!
    mp3_url = book["mp3url"].replace(CHAPTER_PLACEHOLDER, f"{chapter:02d}")

    return [
        create_tts_response(f"Now playing chapter {chapter}"),
        create_mp3_response(mp3_url, book["title"], book["iconurl"]),
    ]


def number_of_chapters_handler(payload):
    if not (book_title := get_param(payload, 'book_title')):
        return None

    book_title = ensure_str(book_title)

    num_chapters = None
    for b in DB:
        if match(b["title"], book_title):
            num_chapters = b["chapters"]
            break

    if not num_chapters:
        return None

    return create_tts_response(f"{book_title} has {num_chapters} chapters.")


### Context intents ###


def number_of_chapters_context_handler(payload):
    if not (book := get_current_book(payload)):
        return None

    return create_tts_response(f"{book['title']} has {book['chapters']} chapters.")


def book_genre_context_handler(payload):
    if not (book := get_current_book(payload)):
        return None

    genres = book['genres']
    item = "genres" if len(genres) > 1 else "genre"
    msg = f"{book['title']} has {item}: {', '.join(genres)}."

    return create_tts_response(msg)


def go_to_chapter_handler(payload):
    if not (book := get_current_book(payload)):
        return None

    if not (chapter_number := get_context_param(payload, 'book_title_context', 'chapter_number')):
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
    if not (book := get_current_book(payload)):
        return None

    # TODO: we also need to know how far along the mp3 file is, again context?
    if not (minutes_played := payload["queryResult"]["parameters"].get("minutes_played", None)):
        return None

    book = None
    for b in DB:
        if match(b["title"], book):
            book = b
            break

    if not book:
        return None

    progress = int(100 * (int(minutes_played) / book["runtime"]))
    return create_tts_response(f"You are {progress}% into {book}.")


def time_to_finish_handler(payload):
    if not (current_book := get_current_book(payload)):
        return None

    # TODO: we also need to know how far along the mp3 file is, again context?
    if not (minutes_played := payload["queryResult"]["parameters"].get("minutes_played", None)):
        return None

    book = None
    for b in DB:
        if match(b["title"], current_book['title']):
            book = b
            break

    if not book:
        return None

    left = book["runtime"] - int(minutes_played)
    return create_tts_response(f"{book['title']} has {left} minutes left.")


def author_of_current_book_handler(payload):
    if not (book := get_current_book(payload)):
        return None

    msg = f"{book['title']} has author: {book['author']}."

    return create_tts_response(msg)


def unread_chapters_handler(payload):
    # TODO: implement
    return None


INTENTS = {
    # No parameters intents
    "available_books": available_books_handler,
    "number_of_books": number_of_books_handler,

    # Parameter intents
    "books_by_author": books_by_author_handler,
    "play_book_author": play_book_author_handler,
    "play_book_genre": play_book_genre_handler,
    "author_of_book_title": author_of_book_title_handler,
    "present_books_with_genre": present_books_with_genre_handler,
    "play_book_title": play_book_title_handler,
    "book_genre": book_genre_handler,
    "start_reading_from_chapter": start_reading_from_chapter_handler,
    "summarize_book": summarize_book_handler,
    "number_of_chapters": number_of_chapters_handler,

    # Context intents
    "book_genre_context": book_genre_context_handler,
    "progress_book": progress_book_handler,
    "author_of_current_book": author_of_current_book_handler,
    "number_of_chapters_context": number_of_chapters_context_handler,
    "go_to_chapter": go_to_chapter_handler,

    # Not implemented
    "time_to_finish": time_to_finish_handler,
    "unread_chapters": unread_chapters_handler,
}


@app.post("/")
def read_root(payload: dict = Body(...)):
    intent_name = payload["queryResult"]["intent"]["displayName"]

    print(f"GOT INTENT: {intent_name}\n")
    print(f"GOT payload: {json.dumps(payload, indent=2)}\n")

    if not (items := INTENTS.get(intent_name, lambda _: None)(payload)):
        msg = payload["queryResult"].get("fulfillmentText", DEFAULT_RESPONSE)
        items = create_tts_response(msg)

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
