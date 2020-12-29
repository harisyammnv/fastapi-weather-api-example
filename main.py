import asyncio

import fastapi
import json
import uvicorn
from starlette.staticfiles import StaticFiles
from pathlib import Path

from models.location import Location
from services import openweather_service, report_service
from api import weather_api
from views import home

api = fastapi.FastAPI()


def configure():
    configure_routing()
    configure_api_keys()
    configure_fake_data()


def configure_api_keys():
    file = Path('settings.json').absolute()
    if not file.exists():
        raise Exception("settings.json file not found")
    with open('settings.json') as fin:
        settings = json.load(fin)
        openweather_service.api_key = settings.get('api_key')


def configure_routing():
    api.include_router(home.router)
    api.include_router(weather_api.router)
    api.mount('/static', StaticFiles(directory='static'), name='static')
# for static files


def configure_fake_data():
    # This was added to make it easier to test the weather event reporting
    # We have /api/reports but until you submit new data each run, it's missing
    # So this will give us something to start from.
    loc = Location(city="Portland", state="OR", country="US")
    asyncio.run(report_service.add_report("Misty sunrise today, beautiful!", loc))
    asyncio.run(report_service.add_report("Clouds over downtown.", loc))


if __name__ == "__main__":
    configure()
    uvicorn.run(api, port=8000, host='127.0.0.1')
else:
    configure()