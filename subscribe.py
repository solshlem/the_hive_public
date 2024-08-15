import json
from nats.aio.client import Client as NATS
from thehive4py.api import TheHiveApi
from thehive4py.models import Case, CaseTask, CaseTaskLog

from webhook.db.db import update_case_slave_id
from webhook.db.db import get_case_by_master_id

# Конфигурация NATS-сервера
NATS_SERVER = "nats://localhost:4222"

# Конфигурация TheHive API
THEHIVE_CONFIGS = {
    "peterburg": {
        "url": "https://thehive-peterburg.example.com",
        "api_key": "your_api_key_peterburg"
    },
    "chehov": {
        "url": "http://localhost:9002",
        "api_key": "OizrMxJ9JsclvHUXCP6vH/GzWXFliBMl"
    }
}

async def main():
    # Подключение к NATS-серверу
    nats = NATS()
    await nats.connect(NATS_SERVER)

    # Подписка на тему NATS
    await nats.subscribe("theHive.cases", cb=handle_case)

    # Ожидание сообщений
    print("Waiting for messages. To exit press CTRL+C")
    #await nats.wait()
    for i in range(1, 1000000):
        await asyncio.sleep(1)

async def handle_case(msg):
    data = json.loads(msg.data.decode())

    action = data["action"]
    case_id = data["case_id"]
    tags = data["tags"]
    description = data["description"]
    organisation = data["organisation"]
    city = data["city"]

    target_thehive = THEHIVE_CONFIGS[city]
    thehive_api = TheHiveApi(target_thehive["url"], target_thehive["api_key"])

    if action == "create":    
        new_case = Case(title=f"Case from {organisation}: {case_id}",
                        description=description,
                        tags=tags)
        response = thehive_api.create_case(new_case)
        slave_id = response.json()['id']
        update_case_slave_id(case_id, slave_id)

        if response.status_code == 201:
            print(f"New case created in TheHive: {response.json()['id']}")
        else:
            print(f"Failed to create case in TheHive: {response.status_code} - {response.text}")

    if action == "update":
        slave_id = get_case_by_master_id(case_id)
        if slave_id:
            case = Case(id=slave_id,
                        title=f"Case from {organisation}: {case_id}",
                        description=description,
                        tags=tags)
            response = thehive_api.update_case(case)

            if response.status_code == 200:
                print(f"Case updated in TheHive: {slave_id}")
            else:
                print(f"Failed to update case in TheHive: {response.status_code} - {response.text}")
        else:
            print(f"No case found in the database for case_id: {case_id}")

if __name__ == "__main__":
    import asyncio
    asyncio.get_event_loop().run_until_complete(main())
