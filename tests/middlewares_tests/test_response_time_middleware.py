import pytest

from unittest.mock import AsyncMock

from bot.middleware.response_time_middleware import ResponseTimeMiddleware

@pytest.mark.asyncio
async def test_response_time_middleware_success():
	response_time_middleware = ResponseTimeMiddleware()

	handler = AsyncMock(return_value="success")

	data = {}

	result = await response_time_middleware(
		handler,
		None,
		data
	)

	assert result == "success"
	assert "request_start" in data

	handler.assert_awaited_once()
