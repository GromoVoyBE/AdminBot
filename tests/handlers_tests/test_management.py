import pytest

from unittest.mock import AsyncMock, Mock

from bot.handlers.group.management import (
	get_event_type,
	chat_member,
	when_bot_added,
	my_chat_member
)

@pytest.mark.parametrize(
	"old,new,old_member,new_member,is_adminbot,expected",
	[
		("member", "administrator", None, None, False, "USER_TO_ADMIN"),
		("left", "member", None, None, False, "LEFT_TO_USER"),
		("restricted", "restricted", False, True, False, "LEFT_TO_RESTRICTED"),
		("left", "creator", None, None, True, "BOT_LEFT_TO_CREATOR"),
		("unknown", "member", None, None, False, "UNKNOWN"),
	]
)
def test_get_event_type(
	old,
	new,
	old_member,
	new_member,
	is_adminbot,
	expected
):
	assert get_event_type(
		old,
		new,
		old_member,
		new_member,
		is_adminbot
	) == expected

@pytest.mark.asyncio
async def test_when_bot_added(services):
	admin = Mock()
	admin.user.id = 10
	admin.user.username = "admin"
	admin.status = "administrator"

	services.telegram_service.get_chat_administrators = AsyncMock(
		return_value=[admin]
	)

	services.telegram_service.status_to_role_db = Mock(
		return_value="admin"
	)

	services.telegram_service.extract_user_permissions = Mock(
		return_value={}
	)

	services.telegram_service.extract_admin_permissions = Mock(
		return_value={}
	)

	services.members_service.upsert_member = AsyncMock()
	services.chats_settings_service.upsert_settings = AsyncMock()

	await when_bot_added(1, services)

	services.members_service.upsert_member.assert_awaited_once()

	services.chats_settings_service.upsert_settings.assert_awaited_once_with(
		1,
		None
	)

@pytest.mark.asyncio
async def test_chat_member_creator(services):
	event = Mock()

	event.chat.id = 1
	event.old_chat_member.status = "left"

	event.new_chat_member.user.id = 2
	event.new_chat_member.user.username = "user"
	event.new_chat_member.status = "creator"

	services.telegram_service.invalidate_user_admins_cache = AsyncMock()

	services.telegram_service.status_to_role_db = Mock(
		return_value="creator"
	)

	services.members_service.upsert_member = AsyncMock()
	services.members_service.update_punishments = AsyncMock()

	await chat_member(
		event,
		services,
		0
	)

	services.members_service.upsert_member.assert_awaited_once()
	services.members_service.update_punishments.assert_not_called()

@pytest.mark.asyncio
async def test_chat_member_admin_update_punishment(services):
	event = Mock()

	event.chat.id = 1

	event.old_chat_member.status = "member"

	event.new_chat_member.user.id = 2
	event.new_chat_member.user.username = "user"
	event.new_chat_member.status = "administrator"

	services.telegram_service.invalidate_user_admins_cache = AsyncMock()

	services.telegram_service.status_to_role_db = Mock(
		return_value="admin"
	)

	services.telegram_service.extract_admin_permissions = Mock(
		return_value={}
	)

	services.telegram_service.extract_user_permissions = Mock(
		return_value={}
	)

	services.members_service.upsert_member = AsyncMock()
	services.members_service.update_punishments = AsyncMock()

	await chat_member(
		event,
		services,
		0
	)

	services.members_service.upsert_member.assert_awaited_once()

	services.members_service.update_punishments.assert_awaited_once()

@pytest.mark.asyncio
async def test_my_chat_member(services):
	event = Mock()

	event.chat.id = 1
	event.chat.type = "group"
	event.chat.username = "group"

	event.old_chat_member.status = "left"

	event.new_chat_member.user.id = 2
	event.new_chat_member.status = "administrator"

	services.telegram_service.invalidate_user_admins_cache = AsyncMock()

	services.telegram_service.status_to_role_db = Mock(
		return_value="admin"
	)

	services.telegram_service.extract_admin_permissions = Mock(
		return_value={}
	)

	services.telegram_service.extract_user_permissions = Mock(
		return_value={}
	)

	services.bot_chats_info_service.upsert_bot = AsyncMock()

	await my_chat_member(
		event,
		services,
		0
	)

	services.bot_chats_info_service.upsert_bot.assert_awaited_once()

@pytest.mark.asyncio
async def test_my_chat_member_calls_when_bot_added(services, monkeypatch):
	event = Mock()

	event.chat.id = 1
	event.chat.type = "group"
	event.chat.username = "group"

	event.old_chat_member.status = "left"
	event.new_chat_member.status = "creator"
	event.new_chat_member.user.id = 2

	services.telegram_service.invalidate_user_admins_cache = AsyncMock()

	services.telegram_service.status_to_role_db = Mock(
		return_value="creator"
	)

	services.telegram_service.extract_admin_permissions = Mock(
		return_value={}
	)

	services.telegram_service.extract_user_permissions = Mock(
		return_value={}
	)

	services.bot_chats_info_service.upsert_bot = AsyncMock()

	when_added = AsyncMock()

	monkeypatch.setattr(
		"bot.handlers.group.management.when_bot_added",
		when_added
	)

	await my_chat_member(
		event,
		services,
		0
	)

	when_added.assert_awaited_once_with(1, services)
