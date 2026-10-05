import pytest

from unittest.mock import AsyncMock, Mock

from bot.middleware.user_sync_middleware import UserSyncMiddleware

@pytest.fixture
def middleware():
	return UserSyncMiddleware()

@pytest.mark.asyncio
async def test_user_sync_middleware_success_message_is_none(
	middleware,
	services
):
	handler = AsyncMock(return_value="ok")

	event = Mock()
	event.message = None

	result = await middleware(
		handler,
		event,
		{"services": services}
	)

	assert result == "ok"

	handler.assert_awaited_once()

@pytest.mark.asyncio
async def test_user_sync_middleware_success_empty_text(
	middleware,
	services,
	message
):
	handler = AsyncMock(return_value="ok")

	message.text = ""

	event = Mock()
	event.message = message

	result = await middleware(
		handler,
		event,
		{"services": services}
	)

	assert result == "ok"

	handler.assert_awaited_once()

@pytest.mark.asyncio
async def test_user_sync_middleware_success_member_exists(
	middleware,
	services,
	message,
	member
):
	handler = AsyncMock(return_value="ok")

	message.chat.id = 1
	message.from_user.id = 2
	message.from_user.username = "john"
	message.text = "/ban"

	event = Mock()
	event.message = message

	services.members_service.get_member.return_value = member
	services.members_service.upsert_member = AsyncMock()

	result = await middleware(
		handler,
		event,
		{"services": services}
	)

	assert result == "ok"

	services.members_service.upsert_member.assert_not_called()

	handler.assert_awaited_once()

@pytest.mark.asyncio
async def test_user_sync_middleware_success_create_member(
	middleware,
	services,
	message,
	member
):
	handler = AsyncMock(return_value="ok")

	message.chat.id = 1
	message.from_user.id = 2
	message.from_user.username = "john"
	message.text = "/start"

	event = Mock()
	event.message = message

	member.status = "member"

	services.members_service.get_member.return_value = None
	services.telegram_service.get_chat_member.return_value = member

	services.telegram_service.status_to_role_db = Mock(
		return_value="user"
	)
	services.telegram_service.extract_user_permissions = Mock(
		return_value={"send": True}
	)
	services.telegram_service.extract_admin_permissions = Mock(
		return_value={}
	)

	services.members_service.upsert_member = AsyncMock()

	result = await middleware(
		handler,
		event,
		{"services": services}
	)

	assert result == "ok"

	services.members_service.upsert_member.assert_awaited_once_with(
		1,
		2,
		"john",
		"user",
		{"send": True},
		{}
	)

	handler.assert_awaited_once()
