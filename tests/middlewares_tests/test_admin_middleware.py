import pytest

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from bot.middleware.admin_middleware import AdminMiddleware
from bot.exceptions import (
	UserHasNoRightsError,
	AdminBotHasNoRightsError
)

@pytest.fixture
def admin_middleware():
	return AdminMiddleware()

@pytest.mark.asyncio
async def test_admin_middleware_success_skip_admin_flag(
	admin_middleware,
	services,
	message
):
	handler = AsyncMock(return_value="ok")

	data = {
		"services": services,
		"handler": SimpleNamespace(
			flags={"skip_admin": True}
		)
	}

	result = await admin_middleware(
		handler,
		message,
		data
	)

	assert result == "ok"
	handler.assert_awaited_once()

@pytest.mark.asyncio
async def test_admin_middleware_user_has_no_rights(
	admin_middleware,
	services,
	message,
	member
):
	handler = AsyncMock()

	message.chat.id = 1
	message.from_user.id = 2

	settings = Mock()
	settings.admin = {"adminerror": True}

	member.role = "user"

	services.chats_settings_service.get_settings.return_value = settings
	services.members_service.get_member.return_value = member

	with pytest.raises(UserHasNoRightsError):
		await admin_middleware(
			handler,
			message,
			{
				"services": services
			}
		)

@pytest.mark.asyncio
async def test_admin_middleware_bot_has_no_rights(
	admin_middleware,
	services,
	message,
	member,
	bot
):
	handler = AsyncMock()

	message.chat.id = 1
	message.from_user.id = 2

	settings = Mock()
	settings.admin = {"adminerror": True}

	member.role = "admin"
	bot.bot_role = "user"

	services.chats_settings_service.get_settings.return_value = settings
	services.members_service.get_member.return_value = member
	services.bot_chats_info_service.get_bot.return_value = bot

	with pytest.raises(AdminBotHasNoRightsError):
		await admin_middleware(
			handler,
			message,
			{
				"services": services
			}
		)

@pytest.mark.asyncio
async def test_admin_middleware_success(
	admin_middleware,
	services,
	message,
	member,
	bot
):
	handler = AsyncMock(return_value="success")

	message.chat.id = 1
	message.from_user.id = 2

	settings = Mock()
	settings.admin = {"adminerror": True}

	member.role = "admin"
	bot.bot_role = "admin"

	services.chats_settings_service.get_settings.return_value = settings
	services.members_service.get_member.return_value = member
	services.bot_chats_info_service.get_bot.return_value = bot

	data = {
		"services": services
	}

	result = await admin_middleware(
		handler,
		message,
		data
	)

	assert result == "success"
	assert data["adminerror"] is True

	handler.assert_awaited_once()
