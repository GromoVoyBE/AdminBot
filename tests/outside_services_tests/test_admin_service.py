import pytest
from unittest.mock import AsyncMock, Mock
from aiogram.exceptions import TelegramBadRequest

from bot.exceptions import (
	CantChangeBotsRightsError,
	CantModerateAssignedNotByBotAdminsError,
	AdminBotHasNoRightsError
)

@pytest.mark.asyncio
async def test_change_admin_role_no_promote_right(services, bot):
	bot.bot_admin_permissions = {
		"can_promote_members": False
	}

	services.bot_chats_info_service.get_bot.return_value = bot

	with pytest.raises(AdminBotHasNoRightsError):
		await services.admin_service.change_admin_role(1, 2, "@john", True)

@pytest.mark.asyncio
async def test_change_admin_role_missing_rights(services, bot):
	bot.bot_admin_permissions = {
		"can_promote_members": True,
		"can_change_info": False
	}

	services.bot_chats_info_service.get_bot.return_value = bot

	with pytest.raises(AdminBotHasNoRightsError):
		await services.admin_service.change_admin_role(1, 2, "@john", True)

@pytest.mark.asyncio
async def test_change_admin_role_promote_bot(services, bot, member):
	bot.bot_admin_permissions = {
		"can_promote_members": True,
		"can_change_info": True,
		"can_delete_messages": True,
		"can_invite_users": True,
		"can_restrict_members": True,
		"can_pin_messages": True
	}

	member.username = "somebot"

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	with pytest.raises(CantChangeBotsRightsError):
		await services.admin_service.change_admin_role(1, 2, "@john", True)

@pytest.mark.asyncio
async def test_change_admin_role_chat_assigned_not_by_adminbot(
	services,
	bot,
	member
):
	bot.bot_admin_permissions = {
		"can_promote_members": True,
		"can_change_info": True,
		"can_delete_messages": True,
		"can_invite_users": True,
		"can_restrict_members": True,
		"can_pin_messages": True
	}

	member.username = "john"

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	services.telegram_service.promote_chat_member = AsyncMock(
		side_effect=TelegramBadRequest(
			method=Mock(),
			message="CHAT_ADMIN_REQUIRED"
		)
	)

	with pytest.raises(CantModerateAssignedNotByBotAdminsError):
		await services.admin_service.change_admin_role(1, 2, "@john", True)

@pytest.mark.asyncio
async def test_change_admin_role_success(services, bot, member):
	bot.bot_admin_permissions = {
		"can_promote_members": True,
		"can_change_info": True,
		"can_delete_messages": True,
		"can_invite_users": True,
		"can_restrict_members": True,
		"can_pin_messages": True
	}

	member.username = "john"

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member
	services.telegram_service.promote_chat_member = AsyncMock()

	result = await services.admin_service.change_admin_role(1, 2, "@john", True)

	assert result == "✅ User @john promoted to admin"

	services.telegram_service.promote_chat_member.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_chat_administrators(services):
	expected = [{"id": 1}, {"id": 2}]

	services.telegram_service.get_chat_administrators = AsyncMock(
		return_value=expected
	)

	result = await services.admin_service.get_chat_administrators(123)

	assert result == expected

@pytest.mark.asyncio
async def test_chat_settings_switch(services):
	services.chats_settings_service.chat_settings_switch = AsyncMock(
		return_value="ok"
	)

	result = await services.admin_service.chat_settings_switch(123, ["arg1"])

	assert result == "ok"
