from fastapi.testclient import TestClient
from server import app, get_message_usage
from unittest.mock import patch, AsyncMock
import httpx


from unittest.mock import patch, AsyncMock

import unittest
from unittest.mock import patch
from server import REPORT_URL

from interfaces import Message, Usage, Report

client = TestClient(app)


class TestCostCalculations(unittest.IsolatedAsyncioTestCase):

    async def test_falls_back_on_calculations(self):
        TEXT_COST = 123
        message = Message(id=1, text="text", timestamp="timestamp", report_id=123)

        with patch(
            "server.httpx.AsyncClient.get", new_callable=AsyncMock
        ) as mock_get, patch(
            "server.calculate_text_cost", return_value=TEXT_COST
        ) as mock_calculate:

            expected_usage = Usage(
                message_id=message.id,
                timestamp=message.timestamp,
                credits_used=TEXT_COST,
            )
            mock_get.return_value = httpx.Response(status_code=404)

            self.assertEqual(await get_message_usage(message), expected_usage)
            mock_get.assert_called_once_with(f"{REPORT_URL}/{message.report_id}")
            mock_calculate.assert_called_once_with(message.text)

    async def test_calls_api_if_report_id(self):
        TEXT_COST = 123
        message = Message(id=1, text="text", timestamp="timestamp", report_id=123)
        report = Report(id=123, name="name", credit_cost=TEXT_COST)

        with patch(
            "server.httpx.AsyncClient.get", new_callable=AsyncMock
        ) as mock_get, patch(
            "server.calculate_text_cost", return_value=TEXT_COST
        ) as mock_calculate:

            expected_usage = Usage(
                message_id=message.id,
                timestamp=message.timestamp,
                credits_used=TEXT_COST,
                report_name=report.name,
            )

            mock_get.return_value = httpx.Response(
                status_code=200, json=report.model_dump()
            )

            self.assertEqual(await get_message_usage(message), expected_usage)
            mock_get.assert_called_once_with(f"{REPORT_URL}/{message.report_id}")
            mock_calculate.assert_not_called()

    async def test_calculates_if_no_report_id(self):
        TEXT_COST = 123
        message = Message(id=1, text="text", timestamp="timestamp")

        with patch(
            "server.httpx.AsyncClient.get", new_callable=AsyncMock
        ) as mock_get, patch(
            "server.calculate_text_cost", return_value=TEXT_COST
        ) as mock_calculate:

            expected_usage = Usage(
                message_id=message.id,
                timestamp=message.timestamp,
                credits_used=TEXT_COST,
            )

            self.assertEqual(await get_message_usage(message), expected_usage)
            mock_get.assert_not_called()
            mock_calculate.assert_called_once_with(message.text)

    async def test_correct_final_output(self):

        message_one = Message(id=1, text="text", timestamp="timestamp")
        message_two = Message(
            id=2, text="text", timestamp="timestamp_two", report_id=123
        )

        usage_one = Usage(
            message_id=message_one.id, timestamp=message_one.timestamp, credits_used=123
        )
        usage_two = Usage(
            message_id=message_two.id,
            timestamp=message_two.timestamp,
            credits_used=150,
            report_name="name",
        )

        get_response = httpx.Response(
            status_code=200,
            json={"messages": [message_one.model_dump(), message_two.model_dump()]},
        )

        with patch(
            "server.httpx.AsyncClient.get",
            new_callable=AsyncMock,
            return_value=get_response,
        ), patch("server.get_message_usage") as mock_get_usage:

            async def get_message_usage_side_effect(message: Message) -> Usage:
                print(message)
                print("+")
                if message == message_one:
                    return usage_one
                else:
                    return usage_two

            mock_get_usage.side_effect = get_message_usage_side_effect

            response = client.get("/usage")
            # self.assertEqual(response.json(), {"usage" : [usage_one.model_dump(), usage_two.model_dump()]})
