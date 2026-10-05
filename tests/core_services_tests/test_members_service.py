import pytest

from unittest.mock import Mock, AsyncMock

from bot.services.services_list.core.members_service import MembersService

@pytest.fixture
def member():
	member = Mock()

	member.chat_id = 1
	member.user_id = 2
	member.username = "john"
	member.role = "user"

	member.user_permissions = {}
	member.admin_permissions = {}

	member.restricted_status = None
	member.admin_who_restricted = None
	member.start_time = None
	member.end_time = None

	return member

@pytest.fixture
def cached_member():
	return {
		"chat_id": 1,
		"user_id": 2,
		"username": "john",
		"role": "user",
		"user_permissions": {},
		"admin_permissions": {},
		"restricted_status": None,
		"admin_who_restricted": None,
		"start_time": None,
		"end_time": None
	}


def test_key():
	assert MembersService._key(1, 2) == "member:1:2"

def test_username_key():
	assert MembersService._username_key(1, "john") == "member:1:john"

def test_members_key():
	assert MembersService._members_key(1) == "members:1"

@pytest.mark.asyncio
async def test_get_member_success_from_cache(
	members_service,
	cached_member,
	monkeypatch
):
	get_cache = AsyncMock(return_value=cached_member)

	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_cache",
		get_cache
	)

	result = await members_service.get_member(1, 2)

	assert result.chat_id == 1
	assert result.user_id == 2

@pytest.mark.asyncio
async def test_get_member_not_found(
	members_service,
	fake_session,
	monkeypatch
):
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_cache",
		AsyncMock(return_value=None)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_member_crud",
		AsyncMock(return_value=None)
	)

	result = await members_service.get_member(1, 2)

	assert result is None

@pytest.mark.asyncio
async def test_get_member_success_from_db(
	members_service,
	member,
	fake_session,
	monkeypatch
):
	set_cache = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_cache",
		AsyncMock(return_value=None)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.set_cache",
		set_cache
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_member_crud",
		AsyncMock(return_value=member)
	)

	result = await members_service.get_member(1, 2)

	assert result == member
	set_cache.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_member_by_username_success_from_cache(
	members_service,
	cached_member,
	monkeypatch
):
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_cache",
		AsyncMock(return_value=cached_member)
	)

	result = await members_service.get_member_by_username(
		1,
		"john"
	)

	assert result.username == "john"

@pytest.mark.asyncio
async def test_get_member_by_username_not_found(
	members_service,
	fake_session,
	monkeypatch
):
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_cache",
		AsyncMock(return_value=None)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_member_by_username_crud",
		AsyncMock(return_value=None)
	)

	result = await members_service.get_member_by_username(
		1,
		"john"
	)

	assert result is None

@pytest.mark.asyncio
async def test_get_member_by_username_success_from_db(
	members_service,
	member,
	fake_session,
	monkeypatch
):
	set_cache = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_cache",
		AsyncMock(return_value=None)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.set_cache",
		set_cache
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_member_by_username_crud",
		AsyncMock(return_value=member)
	)

	result = await members_service.get_member_by_username(
		1,
		"john"
	)

	assert result == member

@pytest.mark.asyncio
async def test_get_members_success_from_cache(
	members_service,
	cached_member,
	monkeypatch
):
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_cache",
		AsyncMock(return_value=[cached_member])
	)

	result = await members_service.get_members(1)

	assert len(result) == 1

@pytest.mark.asyncio
async def test_get_members_success_from_db(
	members_service,
	member,
	fake_session,
	monkeypatch
):
	set_cache = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_cache",
		AsyncMock(return_value=None)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.set_cache",
		set_cache
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_members_crud",
		AsyncMock(return_value=[member])
	)

	result = await members_service.get_members(1)

	assert result == [member]


@pytest.mark.asyncio
async def test_upsert_member_success_update_existing(
	members_service,
	member,
	fake_session,
	monkeypatch
):
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_member_crud",
		AsyncMock(return_value=member)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.set_cache",
		AsyncMock()
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.delete_cache",
		AsyncMock()
	)

	result = await members_service.upsert_member(
		1,
		2,
		"new",
		"admin",
		{},
		{}
	)

	assert result == member
	assert member.username == "new"

@pytest.mark.asyncio
async def test_upsert_member_success_create_new(
	members_service,
	member,
	fake_session,
	monkeypatch
):
	create_member = AsyncMock(return_value=member)

	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_member_crud",
		AsyncMock(return_value=None)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.create_member_crud",
		create_member
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.set_cache",
		AsyncMock()
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.delete_cache",
		AsyncMock()
	)

	result = await members_service.upsert_member(1, 2)

	assert result == member

@pytest.mark.asyncio
async def test_delete_member_success(
	members_service,
	fake_session,
	monkeypatch
):
	delete_member = AsyncMock()
	delete_cache = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.delete_member_crud",
		delete_member
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.delete_cache",
		delete_cache
	)

	await members_service.delete_member(1, 2)

	delete_member.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_punishments_success(
	members_service,
	member,
	fake_session,
	monkeypatch
):
	set_cache = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_session",
		lambda: fake_session
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.get_member_crud",
		AsyncMock(return_value=member)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.set_cache",
		set_cache
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.members_service.delete_cache",
		AsyncMock()
	)

	result = await members_service.update_punishments(
		1,
		2,
		"banned",
		"admin"
	)

	assert result == member
	assert member.restricted_status == "banned"
	assert member.admin_who_restricted == "admin"
