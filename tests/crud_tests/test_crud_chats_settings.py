import pytest
from unittest.mock import AsyncMock, Mock

from bot.storages.postgre.crud_chats_settings import (
	get_settings_crud,
	get_all_settings_crud,
	create_settings_crud,
	delete_settings_crud
)

@pytest.mark.asyncio
async def test_get_settings_crud_success():
	session = AsyncMock()
	obj = Mock()

	session.get.return_value = obj

	result = await get_settings_crud(session, 1)

	assert result == obj

@pytest.mark.asyncio
async def test_get_all_settings_crud_success():
	session = AsyncMock()

	result_mock = Mock()
	result_mock.scalars.return_value.all.return_value = ["settings"]

	session.execute.return_value = result_mock

	result = await get_all_settings_crud(session)

	assert result == ["settings"]

@pytest.mark.asyncio
async def test_create_settings_crud_success_default_admin():
	session = Mock()

	settings = await create_settings_crud(
		session,
		1,
		None
	)

	session.add.assert_called_once()
	assert settings.admin == {
		"anonadmin": False,
		"adminerror": True
	}

@pytest.mark.asyncio
async def test_create_settings_crud_success_custom_admin():
	session = Mock()

	settings = await create_settings_crud(
		session,
		1,
		{"test": True}
	)

	assert settings.admin == {"test": True}

@pytest.mark.asyncio
async def test_delete_settings_crud_success():
	session = AsyncMock()

	await delete_settings_crud(session, 1)

	session.execute.assert_awaited_once()
