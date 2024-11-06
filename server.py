from fastapi import FastAPI
from pydantic import TypeAdapter
from typing import List
from http import HTTPStatus
import httpx
import uvicorn
import asyncio

from cost_calculation import calculate_message_cost
from interfaces import Message, Usage, Report

app = FastAPI()

BASE_CORE_URL = "https://owpublic.blob.core.windows.net/tech-task"
CURRENT_PERIOD_URL = f"{BASE_CORE_URL}/messages/current-period"
REPORT_URL = f"{BASE_CORE_URL}/reports"

async def get_current_period() -> List[Message]:

    async with httpx.AsyncClient() as client:
        response = await client.get(CURRENT_PERIOD_URL)
        data = response.json()  
        messages: List[Message] = TypeAdapter(List[Message]).validate_python(data["messages"])

    return messages


async def get_message_usage(message: Message) -> Usage:
    report = None

    # save an I/O call
    if not message.report_id:
        cost = calculate_message_cost(message)
    else:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{REPORT_URL}/{message.report_id}")

            if response.status_code != HTTPStatus.OK:  
                print(f"Error getting response for report id: {message.report_id}\n{response}")
                return calculate_message_cost(message) 
            else:
                data = response.json()  
                report = Report.parse_obj(data)
                cost = Report.parse_obj(data).credit_cost

    return Usage(message_id=message.id, timestamp = message.timestamp, credits_used = cost, report_name = report.name if report else None) 


async def get_current_period_usages() -> List[Usage]:
    messages = await get_current_period()
    return await asyncio.gather(*(get_message_usage(message) for message in messages))

@app.get("/usage")
async def get_usage():
    return {"usage" : await get_current_period_usages()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)