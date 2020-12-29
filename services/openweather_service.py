from typing import Optional, Tuple
from infrastructure import weather_cache
import httpx

from models.validation_error import ValidationError

api_key: Optional[str] = None


async def get_report_async(city: str, state: Optional[str], country: str, unit: str) -> dict:
    city, state, country, unit = validate_units(city, state, country, unit)
    if forecast := weather_cache.get_weather(city, state, country, unit):
        return forecast

    if state:
        q = f'{city},{state},{country}'
    else:
        q = f'{city},{country}'
    url = f'https://api.openweathermap.org/data/2.5/weather?q={q}&appid={api_key}&units={unit}'

    async with httpx.AsyncClient() as client:
        resp: httpx.Response = await client.get(url=url)
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)

    data = resp.json()
    forecast = data["main"]
    weather_cache.set_weather(city, state, country, unit, forecast)
    return forecast


def validate_units(city: str, state: Optional[str], country: Optional[str], unit: str) -> \
        Tuple[str, Optional[str], str, str]:
    city = city.lower().strip()
    if not country:
        country = "us"
    else:
        country = country.lower().strip()

    if len(country) != 2:
        error = f"Invalid country: {country}. It must be a two letter abbreviation such as US or GB."
        raise ValidationError(status_code=400, error_msg=error)

    if state:
        state = state.strip().lower()

    if state and len(state) != 2:
        error = f"Invalid state: {state}. It must be a two letter abbreviation such as CA or KS (use for US only)."
        raise ValidationError(status_code=400, error_msg=error)

    if unit:
        unit = unit.strip().lower()

    valid_units = {'standard', 'metric', 'imperial'}
    if unit not in valid_units:
        error = f"Invalid units '{unit}', it must be one of {valid_units}."
        raise ValidationError(status_code=400, error_msg=error)

    return city, state, country, unit
