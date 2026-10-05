import pytest

from unittest.mock import AsyncMock, Mock

from bot.middleware.error_middleware import ErrorMiddleware
from bot.exceptions import BotError

@pytest.fixture
def error_middleware():
	return ErrorMiddleware()

class DummyBotError(BotError):
	def log(self, event):
		return "TEST_ERROR"

	def __str__(self):
		return "Test error"

@pytest.mark.asyncio
async def test_error_middleware_success(error_middleware):
	handler = AsyncMock(return_value="success")

	event = Mock()
	data = {"request_start": 0}

	result = await error_middleware(handler,event,data)

	assert result == "success"
	handler.assert_awaited_once()

@pytest.mark.asyncio
async def test_error_middleware_bot_error(error_middleware):
	handler = AsyncMock(
		side_effect=DummyBotError()
	)

	event = Mock()
	event.reply = AsyncMock()

	data = {"request_start": 0}

	result = await error_middleware(handler, event, data)

	assert result is None

	event.reply.assert_awaited_once_with("Test error")
