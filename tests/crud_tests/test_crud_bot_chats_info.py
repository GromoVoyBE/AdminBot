import pytest
from unittest.mock import AsyncMock, Mock

from bot.storages.postgre.crud_bot_chats_info import (
	get_bot_crud,
	get_bots_crud,
	create_bot_crud,
	delete_bot_crud
)

@pytest.mark.asyncio
async def test_get_bot_crud():
	session = AsyncMock()
	obj = Mock()

	session.get.return_value = obj

	result = await get_bot_crud(session, 123)

	session.get.assert_awaited_once()
	assert result == obj

@pytest.mark.asyncio
async def test_get_bots_crud_success():
	session = AsyncMock()

	result_mock = Mock()
	result_mock.scalars.return_value.all.return_value = ["bot1"]

	session.execute.return_value = result_mock

	result = await get_bots_crud(session)

	assert result == ["bot1"]

@pytest.mark.asyncio
async def test_create_bot_crud_success():
	session = Mock()

	bot = await create_bot_crud(
		session,
		1, "group", None,
		"admin", {}, {}
	)

	session.add.assert_called_once()
	assert bot.chat_id == 1

@pytest.mark.asyncio
async def test_delete_bot_crud_success():
	session = AsyncMock()

	await delete_bot_crud(session, 1)

	session.execute.assert_awaited_once()
