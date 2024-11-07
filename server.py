from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import TypeAdapter
from typing import List
from http import HTTPStatus

from aiocache import Cache
from aiocache.serializers import JsonSerializer

import httpx
import uvicorn
import asyncio

from cost_calculation import calculate_text_cost
from interfaces import Message, Usage, Report

app = FastAPI()

BASE_CORE_URL = "https://owpublic.blob.core.windows.net/tech-task"
CURRENT_PERIOD_URL = f"{BASE_CORE_URL}/messages/current-period"
REPORT_URL = f"{BASE_CORE_URL}/reports"
CLIENT_SIDE_CACHE_EXPIRY_TIME = 60
SERVER_SIDE_CACHE_EXPIRY_TIME = 60

cache = Cache.from_url("memory://")
cache.serializer = JsonSerializer()


async def get_current_period() -> List[Message]:

    async with httpx.AsyncClient() as client:
        response = await client.get(CURRENT_PERIOD_URL)
        data = response.json()
        messages: List[Message] = TypeAdapter(List[Message]).validate_python(
            data["messages"]
        )

    return messages


async def get_message_usage(message: Message) -> Usage:
    report = None

    if not message.report_id:
        cost = calculate_text_cost(message.text)
    else:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{REPORT_URL}/{message.report_id}")

            if response.status_code != HTTPStatus.OK:
                print(
                    f"Error getting response for report id: {message.report_id}\n{response}"
                )
                cost = calculate_text_cost(message.text)
            else:
                data = response.json()
                report = Report.model_validate(data)
                cost = report.credit_cost

    return Usage(
        message_id=message.id,
        timestamp=message.timestamp,
        credits_used=cost,
        report_name=report.name if report else None,
    )


@app.get("/usage")
async def get_usage(request: Request):

    # try returning from the cache as much as possible
    usages_serialised = await cache.get(request.url.path)

    if not usages_serialised:
        messages = await get_current_period()
        data = await asyncio.gather(
            *[get_message_usage(message) for message in messages]
        )
        usages_serialised = [usage.model_dump() for usage in data]
        await cache.set(
            request.url.path, usages_serialised, ttl=SERVER_SIDE_CACHE_EXPIRY_TIME
        )

    return JSONResponse(
        content={"usage": usages_serialised},
        headers={"Cache-Control": f"public, max-age={CLIENT_SIDE_CACHE_EXPIRY_TIME}"},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
