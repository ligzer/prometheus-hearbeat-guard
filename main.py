import pytz
from fastapi import FastAPI, BackgroundTasks
import os, asyncio
from datetime import datetime
from telegram import get_me, send_message


URL_KEY = os.getenv('URL_KEY','empty')
HOST = os.getenv('HOST', "0.0.0.0")
PORT = os.getenv('PORT', 8000)
DELAY = os.getenv('DELAY', 600)
CHAT = os.getenv('CHAT', 0)
TOPIC = os.getenv('TOPIC', 0)

timezone_name = os.getenv('TIMEZONE', 'UTC')

if timezone_name not in pytz.all_timezones:
    raise ValueError(f"The timezone '{timezone_name}' is not valid.")

timezone = pytz.timezone(timezone_name)


last_request = None
fastapi_app = FastAPI()
running_tasks = []
errors = 0


@fastapi_app.get(f"/{URL_KEY}/heartbeat/")
async def heartbeat():
    global running_tasks, errors, last_request

    last_request = datetime.now(timezone)
    for task in running_tasks:
        task.cancel()
    running_tasks = [task for task in running_tasks if not task.cancelled]
    loop = asyncio.get_running_loop()
    task = loop.create_task(process_notification())
    running_tasks.append(task)
    return {"errors": errors}


async def process_notification():
    try:
        await asyncio.sleep(DELAY)
        send_message(
            CHAT, TOPIC,
            f"Prometheus has'not send hearbeat request since "
            f"{last_request.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        )
    except asyncio.CancelledError as e:
        pass





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host=HOST, port=PORT)
