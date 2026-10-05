import pytest

from unittest.mock import Mock, AsyncMock

from bot.exceptions import (
	TooManyArgumentsError,
	MissingArgumentsError,
	InvalidSettingModeError
)

from bot.services.services_list.core.chats_settings_service import (
	ChatsSettingsService
)


@pytest.fixture
def settings():
	settings = Mock()

	settings.chat_id = 1
	settings.admin = {
		"anonadmin": False,
		"adminerror": True
	}

	return settings

@pytest.fixture
def cached_settings():
	return {
		"chat_id": 1,
		"admin": {
			"anonadmin": False,
			"adminerror": True
		}
	}


def test_key():
	assert ChatsSettingsService._key(1) == "settings:1"

def test_all_settings_key():
	assert ChatsSettingsService._all_settings_key() == "all_settings:"

@pytest.mark.asyncio
async def test_get_settings_success_from_cache(
	chats_settings_service,
	cached_settings,
	monkeypatch
):
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_cache",
		AsyncMock(return_value=cached_settings)
	)

	result = await chats_settings_service.get_settings(1)

	assert result.chat_id == 1
	assert result.admin["adminerror"] is True

@pytest.mark.asyncio
async def test_get_settings_not_found(
	chats_settings_service,
	fake_session,
	monkeypatch
):
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_cache",
		AsyncMock(return_value=None)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_settings_crud",
		AsyncMock(return_value=None)
	)

	result = await chats_settings_service.get_settings(1)

	assert result is None

@pytest.mark.asyncio
async def test_get_settings_success_from_db(
	chats_settings_service,
	settings,
	fake_session,
	monkeypatch
):
	set_cache = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_cache",
		AsyncMock(return_value=None)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.set_cache",
		set_cache
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_settings_crud",
		AsyncMock(return_value=settings)
	)

	result = await chats_settings_service.get_settings(1)

	assert result == settings
	set_cache.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_all_settings_success_from_cache(
	chats_settings_service,
	cached_settings,
	monkeypatch
):
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_cache",
		AsyncMock(return_value=[cached_settings])
	)

	result = await chats_settings_service.get_all_settings()

	assert len(result) == 1

@pytest.mark.asyncio
async def test_get_all_settings_success_from_db(
	chats_settings_service,
	settings,
	fake_session,
	monkeypatch
):
	set_cache = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_cache",
		AsyncMock(return_value=None)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.set_cache",
		set_cache
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_all_settings_crud",
		AsyncMock(return_value=[settings])
	)

	result = await chats_settings_service.get_all_settings()

	assert result == [settings]

@pytest.mark.asyncio
async def test_upsert_settings_success_update_existing(
	chats_settings_service,
	settings,
	fake_session,
	monkeypatch
):
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_settings_crud",
		AsyncMock(return_value=settings)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.set_cache",
		AsyncMock()
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.delete_cache",
		AsyncMock()
	)

	result = await chats_settings_service.upsert_settings(
		1,
		{"anonadmin": True}
	)

	assert result == settings
	assert settings.admin["anonadmin"] is True

@pytest.mark.asyncio
async def test_upsert_settings_success_create_new(
	chats_settings_service,
	settings,
	fake_session,
	monkeypatch
):
	create_settings = AsyncMock(return_value=settings)

	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_settings_crud",
		AsyncMock(return_value=None)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.create_settings_crud",
		create_settings
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.set_cache",
		AsyncMock()
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.delete_cache",
		AsyncMock()
	)

	result = await chats_settings_service.upsert_settings(1)

	assert result == settings

@pytest.mark.asyncio
async def test_delete_settings_success(
	chats_settings_service,
	fake_session,
	monkeypatch
):
	delete_settings = AsyncMock()
	delete_cache = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.delete_settings_crud",
		delete_settings
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.delete_cache",
		delete_cache
	)

	await chats_settings_service.delete_settings(1)

	delete_settings.assert_awaited_once()

@pytest.mark.asyncio
async def test_chat_settings_switch_too_many_arguments(chats_settings_service):
	with pytest.raises(TooManyArgumentsError):
		await chats_settings_service.chat_settings_switch(
			1,
			["/anonadmin", "on", "extra"],
			"admin"
		)

@pytest.mark.asyncio
async def test_chat_settings_switch_missing_arguments(chats_settings_service):
	with pytest.raises(MissingArgumentsError):
		await chats_settings_service.chat_settings_switch(
			1,
			["/anonadmin"],
			"admin"
		)

@pytest.mark.asyncio
async def test_chat_settings_switch_invalid_mode(
	chats_settings_service
):
	with pytest.raises(InvalidSettingModeError):
		await chats_settings_service.chat_settings_switch(
			1,
			["/anonadmin", "test"],
			"admin"
		)

@pytest.mark.asyncio
async def test_chat_settings_switch_success_enabled(
	chats_settings_service,
	settings,
	fake_session,
	monkeypatch
):
	upsert_settings = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_settings_crud",
		AsyncMock(return_value=settings)
	)

	chats_settings_service.upsert_settings = upsert_settings

	result = await chats_settings_service.chat_settings_switch(
		1,
		["/anonadmin", "on"],
		"admin"
	)

	assert result == "✅ The setting /anonadmin is now enabled"
	upsert_settings.assert_awaited_once()

@pytest.mark.asyncio
async def test_chat_settings_switch_success_disabled(
	chats_settings_service,
	settings,
	fake_session,
	monkeypatch
):
	upsert_settings = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.chats_settings_service.get_settings_crud",
		AsyncMock(return_value=settings)
	)

	chats_settings_service.upsert_settings = upsert_settings

	result = await chats_settings_service.chat_settings_switch(
		1,
		["/anonadmin", "off"],
		"admin"
	)

	assert result == "✅ The setting /anonadmin is now disabled"
	upsert_settings.assert_awaited_once()
