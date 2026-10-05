import pytest

from unittest.mock import AsyncMock, Mock

from types import SimpleNamespace

from bot.services.services_list.admin_service import AdminService
from bot.services.services_list.bans_service import BansService
from bot.services.services_list.utils_service import UtilsService

from bot.services.services_list.core.members_service import MembersService
from bot.services.services_list.core.chats_settings_service import (
	ChatsSettingsService
)
from bot.services.services_list.core.bot_chats_info_service import (
	BotChatsInfoService
)
from bot.services.services_list.core.telegram_service import TelegramService

@pytest.fixture
def fake_session():
	class FakeSession:
		async def __aenter__(self):
			return Mock()

		async def __aexit__(self, exc_type, exc, tb):
			pass

	return FakeSession()

@pytest.fixture
def bot():
	return Mock()

@pytest.fixture
def members_service():
	return MembersService()

@pytest.fixture
def bot_chats_info_service():
    return BotChatsInfoService()

@pytest.fixture
def chats_settings_service():
    return ChatsSettingsService()

@pytest.fixture
def telegram_service():
    return TelegramService(bot)

@pytest.fixture
def message():
	return Mock()

@pytest.fixture
def member():
	return Mock()

@pytest.fixture
def user():
	return Mock()

@pytest.fixture
def reply():
	return Mock()

@pytest.fixture
def services():
	services = SimpleNamespace()

	services.members_service = AsyncMock()
	services.chats_settings_service = AsyncMock()
	services.bot_chats_info_service = AsyncMock()
	services.telegram_service = AsyncMock()

	services.admin_service = AdminService(
		services.members_service,
		services.bot_chats_info_service,
		services.chats_settings_service,
		services.telegram_service
	)

	services.bans_service = BansService(
		services.members_service,
		services.bot_chats_info_service,
		services.telegram_service
	)

	services.utils_service = UtilsService(
		services.members_service,
		services.telegram_service
	)

	return services
