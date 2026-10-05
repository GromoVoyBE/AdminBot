import pytest

from unittest.mock import Mock, AsyncMock

from bot.services.services_list.core.bot_chats_info_service import (
	BotChatsInfoService
)

@pytest.fixture
def bot():
	bot = Mock()

	bot.chat_id = 1
	bot.chat_type = "group"
	bot.chat_username = "testchat"
	bot.bot_role = "admin"
	bot.bot_user_permissions = {}
	bot.bot_admin_permissions = {}

	return bot

@pytest.fixture
def cached_bot():
	return {
		"chat_id": 1,
		"chat_type": "group",
		"chat_username": "testchat",
		"bot_role": "admin",
		"bot_user_permissions": {},
		"bot_admin_permissions": {}
	}


def test_key():
	assert BotChatsInfoService._key(1) == "bot:1"

def test_bots_key():
	assert BotChatsInfoService._bots_key() == "bots:"

@pytest.mark.asyncio
async def test_get_bot_success_from_cache(
	bot_chats_info_service,
	cached_bot,
	monkeypatch
):
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.get_cache",
		AsyncMock(return_value=cached_bot)
	)

	result = await bot_chats_info_service.get_bot(1)

	assert result.chat_id == 1

@pytest.mark.asyncio
async def test_get_bot_not_found(
	bot_chats_info_service,
	fake_session,
	monkeypatch
):
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.get_cache",
		AsyncMock(return_value=None)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.get_bot_crud",
		AsyncMock(return_value=None)
	)

	result = await bot_chats_info_service.get_bot(1)

	assert result is None

@pytest.mark.asyncio
async def test_get_bot_success_from_db(
	bot_chats_info_service,
	bot,
	fake_session,
	monkeypatch
):
	set_cache = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.get_cache",
		AsyncMock(return_value=None)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.set_cache",
		set_cache
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.get_bot_crud",
		AsyncMock(return_value=bot)
	)

	result = await bot_chats_info_service.get_bot(1)

	assert result == bot
	set_cache.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_bots_success_from_cache(
	bot_chats_info_service,
	cached_bot,
	monkeypatch
):
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.get_cache",
		AsyncMock(return_value=[cached_bot])
	)

	result = await bot_chats_info_service.get_bots()

	assert len(result) == 1

@pytest.mark.asyncio
async def test_get_bots_success_from_db(
	bot_chats_info_service,
	bot,
	fake_session,
	monkeypatch
):
	set_cache = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.get_cache",
		AsyncMock(return_value=None)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.set_cache",
		set_cache
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.get_bots_crud",
		AsyncMock(return_value=[bot])
	)

	result = await bot_chats_info_service.get_bots()

	assert result == [bot]

@pytest.mark.asyncio
async def test_upsert_bot_success_update_existing(
	bot_chats_info_service,
	bot,
	fake_session,
	monkeypatch
):
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.get_bot_crud",
		AsyncMock(return_value=bot)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.set_cache",
		AsyncMock()
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.delete_cache",
		AsyncMock()
	)

	result = await bot_chats_info_service.upsert_bot(
		1,
		"supergroup",
		"newchat",
		"admin",
		{},
		{}
	)

	assert result == bot
	assert bot.chat_type == "supergroup"
	assert bot.chat_username == "newchat"
	assert bot.bot_role == "admin"

@pytest.mark.asyncio
async def test_upsert_bot_success_create_new(
	bot_chats_info_service,
	bot,
	fake_session,
	monkeypatch
):
	create_bot = AsyncMock(return_value=bot)

	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.get_bot_crud",
		AsyncMock(return_value=None)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.create_bot_crud",
		create_bot
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.set_cache",
		AsyncMock()
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.delete_cache",
		AsyncMock()
	)

	result = await bot_chats_info_service.upsert_bot(
		1,
		"supergroup"
	)

	assert result == bot

@pytest.mark.asyncio
async def test_delete_bot_success(
	bot_chats_info_service,
	fake_session,
	monkeypatch
):
	delete_bot = AsyncMock()
	delete_cache = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.delete_bot_crud",
		delete_bot
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.bot_chats_info_service.delete_cache",
		delete_cache
	)

	await bot_chats_info_service.delete_bot(1)

	delete_bot.assert_awaited_once()
