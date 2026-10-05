import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from bot.storages.postgre.crud_members import (
	get_member_crud,
	get_member_by_username_crud,
	get_members_crud,
	create_member_crud,
	delete_member_crud,
	get_punishments_crud
)

@pytest.mark.asyncio
async def test_get_member_crud_success():
	session = AsyncMock()

	session.get.return_value = "member"

	result = await get_member_crud(session, 1, 2)

	assert result == "member"

@pytest.mark.asyncio
async def test_get_member_by_username_crud_success():
	session = AsyncMock()

	result_mock = Mock()
	result_mock.scalar_one_or_none.return_value = "member"

	session.execute.return_value = result_mock

	result = await get_member_by_username_crud(
		session,
		1,
		"test"
	)

	assert result == "member"

@pytest.mark.asyncio
async def test_get_members_crud_success():
	session = AsyncMock()

	result_mock = Mock()
	result_mock.scalars.return_value.all.return_value = ["m1"]

	session.execute.return_value = result_mock

	result = await get_members_crud(session, 1)

	assert result == ["m1"]

@pytest.mark.asyncio
async def test_create_member_crud_success():
	session = Mock()

	member = await create_member_crud(
		session,
		1,
		2
	)

	session.add.assert_called_once()
	assert member.user_id == 2

@pytest.mark.asyncio
async def test_delete_member_crud_success():
	session = AsyncMock()

	await delete_member_crud(session, 1, 2)

	session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_punishments_crud_success():
	session = AsyncMock()

	result_mock = Mock()
	result_mock.scalars.return_value.all.return_value = ["punishment"]

	session.execute.return_value = result_mock

	result = await get_punishments_crud(
		session,
		datetime.now()
	)

	assert result == ["punishment"]
