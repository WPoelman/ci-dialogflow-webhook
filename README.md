# ci-dialogflow-webhook
Webhook for Dialogflow for the course Conversational Interfaces: Practice.

## Install
1. (OPTIONAL) create and activate a virtual environment
2. Run `pip install -r requirements.txt`
3. Download and install `ngrok`: https://dl.equinox.io/ngrok/ngrok/stable
4. Run ngrok: `ngrok http 8000 --region=eu`
5. Copy the `https` url from ngrok into Dialogflow
6. Run the server with `uvicorn main:app --reload`
7. Try it out with invoking an intent that calls the webhook (make sure it's enabled for the intent)
