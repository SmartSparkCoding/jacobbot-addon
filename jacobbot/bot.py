from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import json
import os
import re

DATA_FILE = "/app/data/acronyms.json"

def load_acronyms():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_acronyms(acronyms):
    with open(DATA_FILE, "w") as f:
        json.dump(acronyms, f, indent=4)

acronyms = load_acronyms()

app = App(token=os.environ["SLACK_BOT_TOKEN"])

ACRONYM_REGEX = r"\b[A-Z]{2,10}\b"
pending = {}

@app.event("message")
def detect_acronyms(event, say):
    if "text" not in event:
        return
    if event.get("subtype") == "bot_message":
        return

    text = event["text"]
    thread_ts = event["ts"]

    found = re.findall(ACRONYM_REGEX, text)

    for word in found:
        key = word.upper()
        if key in acronyms:
            say(
                text=f"*Meaning of {key}:* {acronyms[key]}",
                thread_ts=thread_ts
            )

@app.command("/jacobbothelper")
def command(ack, body, client):
    ack()
    user = body["user_id"]
    channel = body["channel_id"]
    text = body["text"].strip().lower()

    if text == "addnew":
        pending[user] = {"mode": "add_wait_acronym"}
        client.chat_postEphemeral(
            channel=channel,
            user=user,
            text="Send the acronym you want to add."
        )

    elif text == "delete":
        pending[user] = {"mode": "delete_wait_acronym"}
        client.chat_postEphemeral(
            channel=channel,
            user=user,
            text="Send the acronym you want to delete."
        )

    else:
        client.chat_postEphemeral(
            channel=channel,
            user=user,
            text="Use: addnew or delete"
        )

@app.event("message")
def handle_user_input(event, client):
    user = event.get("user")
    text = event.get("text")
    channel = event.get("channel")

    if event.get("subtype") == "bot_message":
        return
    if user not in pending:
        return

    state = pending[user]

    if state["mode"] == "add_wait_acronym":
        pending[user] = {
            "mode": "add_wait_meaning",
            "acronym": text.upper()
        }
        client.chat_postEphemeral(
            channel=channel,
            user=user,
            text=f"Meaning of {text.upper()}?"
        )
        return

    if state["mode"] == "add_wait_meaning":
        acronym = state["acronym"]
        acronyms[acronym] = text
        save_acronyms(acronyms)
        client.chat_postEphemeral(
            channel=channel,
            user=user,
            text=f"Added {acronym}: {text}"
        )
        del pending[user]
        return

    if state["mode"] == "delete_wait_acronym":
        acronym = text.upper()
        if acronym in acronyms:
            del acronyms[acronyms]
            save_acronyms(acronyms)
            client.chat_postEphemeral(
                channel=channel,
                user=user,
                text=f"Deleted {acronym}"
            )
        else:
            client.chat_postEphemeral(
                channel=channel,
                user=user,
                text=f"{acronym} not found."
            )
        del pending[user]
        return

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
