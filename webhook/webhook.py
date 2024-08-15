from flask import Flask, request, jsonify
from nats.aio.client import Client as NATS
import json

from db.db import init_db
from db.db import add_new_case
from db.db import get_case_by_master_id

app = Flask(__name__)

NATS_SERVER = "nats://172.22.0.11:4222"

@app.route('/webhook', methods=['POST'])
async def handle_webhook():
    data = request.get_json()
    app.logger.error(data)

    action = data["action"]
    case_id = data["object"]["_id"]
    tags = data["object"]["tags"]
    description = data["object"]["description"]
    organisation = data["organisation"]["organisation"]

    city = None
    for tag in tags:
        if tag.startswith("send-to"):
            city = tag.split('=')[1]
            break

    if not city:
        return jsonify({
            "status": "error",
            "msg": "invalid case"
        })

    if action == "create":
        add_new_case(case_id, city)
        await publish_to_nats(action, case_id, tags, description, organisation, city)

    elif action == "update":
        slave_id = get_case_by_master_id(case_id)

        if not slave_id:
            return jsonify({
                "status": "error",
                "msg": "no such case in database"
            })
        
        await publish_to_nats(action, case_id, tags, description, organisation, city)

    return jsonify({
        "status": "ok"
    })

async def publish_to_nats(action, case_id, tags, description, organisation, city):
    nats = NATS()
    
    await nats.connect(NATS_SERVER)

    message = {
        "action": action,
        "case_id": case_id,
        "tags": tags,
        "description": description,
        "organisation": organisation,
        "city": city
    }

    await nats.publish("theHive.cases", json.dumps(message).encode())
    await nats.close()

if __name__ == '__main__':
    app.run()
