from pathlib import Path
import json
import sys


def main():
    if len(sys.argv) < 2:
        raise ValueError("Please provide the path to the intents directory.")

    intent_dir = Path(sys.argv[1])
    result = dict()
    for intent_file in intent_dir.glob("*.json"):
        with open(intent_file) as f:
            intent = json.load(f)

            # We skip intents that are lists (these are specific responses)
            if isinstance(intent, list):
                continue

            # Only keep intents that require the webhook
            if not intent.get("webhookUsed", None):
                continue

            # We need the name to register the function
            if not (intent_name := intent.get("name", None)):
                continue

            # Filter out invalid names
            if " " in intent_name:
                print(f"Skipped {intent_name}, invalid name")
                continue

            if len(intent["responses"]) > 1:
                print(f"Skipped {intent_name}, more than 1 respons")
                continue

            params = intent['responses'][0]["parameters"]

            result[intent_name] = {
                "parameters": [param["name"] for param in params]
            }

    with open('data/intents_and_parameters.json', 'w') as f:
        json.dump(result, f, indent=4)


if __name__ == "__main__":
    main()
