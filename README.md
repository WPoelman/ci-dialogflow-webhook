# ci-dialogflow-webhook
Webhook for Dialogflow for the course Conversational Interfaces: Practice.

## Install
1. (OPTIONAL) create and activate a virtual environment
2. Run `pip install -r requirements.txt`
3. Download and install ngrok: https://dl.equinox.io/ngrok/ngrok/stable
4. Run ngrok: `ngrok http 8000 --region=eu`
5. Copy the `https` url into Dialogflow (webhook url)
6. Run the server with `uvicorn main:app --reload` (make sure it's using the same port as ngrok, 8000 is default so should be good)
7. Test it out with invoking an intent that calls the webhook (make sure it's enabled for the intent, probably also enable the 'slot filling', otherwise you cannot access the entities/parameters from the intent)

## Extract intents
The script `extract_intents.py` helps with extracting the intents and their parameters from the project.

1. In Dialogflow export the project as a zip and extract it.
2. Run `python extract_intents.py <extracted_folder_path>/intents`
3. This creates `intents_and_parameters.json`
