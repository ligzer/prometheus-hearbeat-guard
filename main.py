import pytz
from fastapi import FastAPI
import os, asyncio
from datetime import datetime
from telegram import get_me, send_message
from uvicorn import Config, Server
import logging


logger = logging.getLogger('uvicorn')

URL_KEY = os.getenv('URL_KEY')
HOST = os.getenv('HOST', "0.0.0.0")
PORT = int(os.getenv('PORT', 8000))
DELAY = int(os.getenv('DELAY', 600))
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
    return {"prometheus_hearbeat_guard_telegram_access_errors": errors}


async def process_notification():
    try:
        await asyncio.sleep(DELAY)
        send_message(
            CHAT, TOPIC,
            f"Prometheus has not send hearbeat request since "
            f"{last_request.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        )
        logger.info("Send alert")
    except asyncio.CancelledError as e:
        pass
    except Exception as e:
        logger.error(e)


async def monitor_telegram():
    global errors
    while True:
        try:
            get_me()
        except Exception as e:
            errors += 1
            logger.error(e)
        await asyncio.sleep(60)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.create_task(monitor_telegram())
    config = Config(app=fastapi_app, loop=loop, host=HOST, port=int(PORT))
    server = Server(config)
    loop.run_until_complete(server.serve())
