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

            # We need the name to register the function
            if not (intent_name := intent.get("name", None)):
                continue

            if len(intent["responses"]) > 1:
                print(f"Skipped {intent_name}, more than 1 respons")
                continue

            params = intent['responses'][0]["parameters"]

            # We skip intents that don't have parameters, we assume the webhook does
            # not have to deal with this.
            if len(params) == 0:
                continue

            result[intent_name] = {
                "parameters": [param["name"] for param in params]
            }

    with open('intents_and_parameters.json', 'w') as f:
        json.dump(result, f, indent=4)


if __name__ == "__main__":
    main()
