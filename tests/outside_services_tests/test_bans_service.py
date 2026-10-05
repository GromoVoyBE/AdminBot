import pytest

from unittest.mock import AsyncMock, Mock

from datetime import datetime

from aiogram.types import Message, ChatPermissions

from bot.exceptions import (
	UserNotFoundError,
	AdminBotHasNoRightsError,
	CantBanAdminError,
	NeedReplyToMessageError,
	UserNotBannedError,
	CantMuteAdminError,
	UserNotMutedError,
	CantKickAdminError,
	KickMeAdminError
)

@pytest.mark.asyncio
async def test_ban_no_admin_rights(services, bot, message):
	bot.bot_admin_permissions = {
		"can_restrict_members": False,
		"can_delete_messages": True
	}

	services.bot_chats_info_service.get_bot.return_value = bot

	with pytest.raises(AdminBotHasNoRightsError):
		await services.bans_service.ban(1, 2, "@john", message)

@pytest.mark.asyncio
async def test_ban_user_not_found(services, bot, message):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = None

	with pytest.raises(UserNotFoundError):
		await services.bans_service.ban(1, 2, "@john", message)

@pytest.mark.asyncio
async def test_ban_target_is_admin(services, bot, member, message):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	member.role = "admin"

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	with pytest.raises(CantBanAdminError):
		await services.bans_service.ban(1, 2, "@john", message)

@pytest.mark.asyncio
async def test_ban_delete_without_reply(services, bot, member, message):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	member.role = "user"

	message.reply_to_message = None

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	with pytest.raises(NeedReplyToMessageError):
		await services.bans_service.ban(1, 2, "@john", message, delete=True)

@pytest.mark.asyncio
async def test_ban_success_delete(services, bot, member, message, reply):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	member.role = "user"
	member.username = "john"

	reply.message_id = 222

	message.reply_to_message = reply
	message.from_user = Mock(username="admin")

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	services.telegram_service.delete_message = AsyncMock()
	services.telegram_service.ban_chat_member = AsyncMock()
	services.members_service.update_punishments = AsyncMock()

	result = await services.bans_service.ban(
		1, 2, "@john", message, delete=True
	)
	assert result == "✅ User @john has been banned"

	services.telegram_service.ban_chat_member.assert_awaited_once_with(
		1,
		2,
		None
	)
	services.members_service.update_punishments.assert_awaited_once()

@pytest.mark.asyncio
async def test_ban_success(services, bot, member, message):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	member.role = "user"
	member.username = "john"

	message.from_user = Mock(username="admin")
	message.reply_to_message = None

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member
	services.telegram_service.ban_chat_member = AsyncMock()
	services.members_service.update_punishments = AsyncMock()

	result = await services.bans_service.ban(1, 2, "@john", message)

	assert result == "✅ User @john has been banned"

	services.telegram_service.ban_chat_member.assert_awaited_once_with(
		1,
		2,
		None
	)
	services.members_service.update_punishments.assert_awaited_once()

@pytest.mark.asyncio
async def test_ban_success_secret(services, bot, member, message):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	member.role = "user"
	member.username = "john"

	message.message_id = 123
	message.from_user = Mock(username="admin")

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	services.telegram_service.ban_chat_member = AsyncMock()
	services.telegram_service.delete_message = AsyncMock()
	services.members_service.update_punishments = AsyncMock()

	result = await services.bans_service.ban(
		1, 2, "@john", message, secret=True
	)
	assert result == "✅ User @john has been banned"

	services.telegram_service.ban_chat_member.assert_awaited_once_with(
		1,
		2,
		None
	)
	services.members_service.update_punishments.assert_awaited_once()

	services.telegram_service.delete_message.assert_awaited_once_with(1, 123)


@pytest.mark.asyncio
async def test_unban_no_admin_rights(services, bot):
	bot.bot_admin_permissions = {
		"can_restrict_members": False
	}

	services.bot_chats_info_service.get_bot.return_value = bot

	with pytest.raises(AdminBotHasNoRightsError):
		await services.bans_service.unban(1, 2, "@john")

@pytest.mark.asyncio
async def test_unban_user_not_found(services, bot):
	bot.bot_admin_permissions = {
		"can_restrict_members": True
	}

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = None

	with pytest.raises(UserNotFoundError):
		await services.bans_service.unban(1, 2, "@john")

@pytest.mark.asyncio
async def test_unban_not_banned(services, bot, member):
	bot.bot_admin_permissions = {
		"can_restrict_members": True
	}

	member.restricted_status = "muted"

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	with pytest.raises(UserNotBannedError):
		await services.bans_service.unban(1, 2, "@john")

@pytest.mark.asyncio
async def test_unban_success(services, bot, member):
	bot.bot_admin_permissions = {
		"can_restrict_members": True
	}

	member.restricted_status = "banned"

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member
	services.telegram_service.unban_chat_member = AsyncMock()
	services.members_service.update_punishments = AsyncMock()

	result = await services.bans_service.unban(1, 2, "@john")

	assert result == "✅ User @john has been unbanned"

	services.telegram_service.unban_chat_member.assert_awaited_once_with(1, 2)
	services.members_service.update_punishments.assert_awaited_once()


@pytest.mark.asyncio
async def test_mute_no_admin_rights(services, bot):
	bot.bot_admin_permissions = {
		"can_restrict_members": False,
		"can_delete_messages": True
	}

	services.bot_chats_info_service.get_bot.return_value = bot

	with pytest.raises(AdminBotHasNoRightsError):
		await services.bans_service.mute(1, 2, "@john", Mock())

@pytest.mark.asyncio
async def test_mute_user_not_found(services, bot):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = None

	with pytest.raises(UserNotFoundError):
		await services.bans_service.mute(1, 2, "@john", Mock())

@pytest.mark.asyncio
async def test_mute_target_is_admin(services, bot, member):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	member.role = "admin"

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	with pytest.raises(CantMuteAdminError):
		await services.bans_service.mute(1, 2, "@john", Mock())

@pytest.mark.asyncio
async def test_mute_delete_without_reply(services, bot, member, message):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	member.role = "user"

	message.reply_to_message = None

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	with pytest.raises(NeedReplyToMessageError):
		await services.bans_service.mute(1, 2, "@john", message, delete=True)

@pytest.mark.asyncio
async def test_mute_success_delete(services, bot, member, message, reply):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	member.role = "user"
	member.username = "john"

	reply.message_id = 222

	message.reply_to_message = reply
	message.from_user = Mock(username="admin")

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	services.telegram_service.delete_message = AsyncMock()
	services.telegram_service.restrict_chat_member = AsyncMock()
	services.members_service.update_punishments = AsyncMock()

	result = await services.bans_service.mute(
		1, 2, "@john", message, delete=True
	)
	assert result == "✅ User @john has been muted"

	services.telegram_service.restrict_chat_member.assert_awaited_once()

	services.members_service.update_punishments.assert_awaited_once()

@pytest.mark.asyncio
async def test_mute_success(services, bot, member, message):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	member.role = "user"
	member.username = "john"

	message.from_user = Mock(username="admin")
	message.reply_to_message = None

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member
	services.telegram_service.restrict_chat_member = AsyncMock()
	services.members_service.update_punishments = AsyncMock()

	result = await services.bans_service.mute(1, 2, "@john", message)

	assert result == "✅ User @john has been muted"

	services.telegram_service.restrict_chat_member.assert_awaited_once()

	services.members_service.update_punishments.assert_awaited_once()

@pytest.mark.asyncio
async def test_mute_success_secret(services, bot, member, message):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	member.role = "user"

	message.message_id = 123
	message.from_user = Mock(username="admin")

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	services.telegram_service.restrict_chat_member = AsyncMock()
	services.telegram_service.delete_message = AsyncMock()
	services.members_service.update_punishments = AsyncMock()

	result = await services.bans_service.mute(
		1, 2, "@john", message, secret=True
	)
	assert result == "✅ User @john has been muted"

	services.telegram_service.restrict_chat_member.assert_awaited_once()

	services.members_service.update_punishments.assert_awaited_once()

	services.telegram_service.delete_message.assert_awaited_once_with(1, 123)


@pytest.mark.asyncio
async def test_unmute_no_admin_rights(services, bot):
	bot.bot_admin_permissions = {
		"can_restrict_members": False
	}

	services.bot_chats_info_service.get_bot.return_value = bot

	with pytest.raises(AdminBotHasNoRightsError):
		await services.bans_service.unmute(1, 2, "@john")

@pytest.mark.asyncio
async def test_unmute_user_not_found(services, bot):
	bot.bot_admin_permissions = {
		"can_restrict_members": True
	}

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = None

	with pytest.raises(UserNotFoundError):
		await services.bans_service.unmute(1, 2, "@john")

@pytest.mark.asyncio
async def test_unmute_not_muted(services, bot, member):
	bot.bot_admin_permissions = {
		"can_restrict_members": True
	}

	member.restricted_status = "banned"

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	with pytest.raises(UserNotMutedError):
		await services.bans_service.unmute(1, 2, "@john")

@pytest.mark.asyncio
async def test_unmute_success(services, bot, member):
	bot.bot_admin_permissions = {
		"can_restrict_members": True
	}

	member.restricted_status = "muted"

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member
	services.telegram_service.restrict_chat_member = AsyncMock()
	services.members_service.update_punishments = AsyncMock()

	result = await services.bans_service.unmute(1, 2, "@john")

	assert result == "✅ User @john has been unmuted"

	services.telegram_service.restrict_chat_member.assert_awaited_once()

	services.members_service.update_punishments.assert_awaited_once()


@pytest.mark.asyncio
async def test_kick_no_admin_rights(services, bot):
	bot.bot_admin_permissions = {
		"can_restrict_members": False,
		"can_delete_messages": True
	}

	services.bot_chats_info_service.get_bot.return_value = bot

	with pytest.raises(AdminBotHasNoRightsError):
		await services.bans_service.kick(1, 2, "@john", Mock())

@pytest.mark.asyncio
async def test_kick_user_not_found(services, bot):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = None

	with pytest.raises(UserNotFoundError):
		await services.bans_service.kick(1, 2, "@john", Mock())

@pytest.mark.asyncio
async def test_kick_target_is_admin(services, bot, member):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	member.role = "admin"

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	with pytest.raises(CantKickAdminError):
		await services.bans_service.kick(1, 2, "@john", Mock())

@pytest.mark.asyncio
async def test_kick_delete_without_reply(services, bot, member, message):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	member.role = "user"
	message.reply_to_message = None

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	with pytest.raises(NeedReplyToMessageError):
		await services.bans_service.kick(1, 2, "@john", message, delete=True)

@pytest.mark.asyncio
async def test_kick_delete_success(services, bot, member, message, reply):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	member.role = "user"
	member.username = "john"

	reply.message_id = 222

	message.reply_to_message = reply
	message.from_user = Mock(username="admin")

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	services.telegram_service.delete_message = AsyncMock()
	services.telegram_service.ban_chat_member = AsyncMock()
	services.telegram_service.unban_chat_member = AsyncMock()

	result = await services.bans_service.kick(
		1, 2, "@john", message, delete=True
	)
	assert result == "✅ User @john has been kicked"

	services.telegram_service.ban_chat_member.assert_awaited_once_with(1, 2)
	services.telegram_service.unban_chat_member.assert_awaited_once()

@pytest.mark.asyncio
async def test_kick_success(services, bot, member):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	member.role = "user"

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member
	services.telegram_service.ban_chat_member = AsyncMock()
	services.telegram_service.unban_chat_member = AsyncMock()

	result = await services.bans_service.kick(1, 2, "@john", Mock())

	assert result == "✅ User @john has been kicked"

	services.telegram_service.ban_chat_member.assert_awaited_once_with(1, 2)
	services.telegram_service.unban_chat_member.assert_awaited_once()

@pytest.mark.asyncio
async def test_kick_success_secret(services, bot, member, message):
	bot.bot_admin_permissions = {
		"can_restrict_members": True,
		"can_delete_messages": True
	}

	member.role = "user"
	message.message_id = 123

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	services.telegram_service.delete_message = AsyncMock()

	result = await services.bans_service.kick(
		1, 2, "@john", message, secret=True
	)
	assert result == "✅ User @john has been kicked"

	services.telegram_service.ban_chat_member.assert_awaited_once_with(1, 2)
	services.telegram_service.unban_chat_member.assert_awaited_once()

	services.telegram_service.delete_message.assert_awaited_once_with(1, 123)


@pytest.mark.asyncio
async def test_kickme_no_admin_rights(services, bot):
	bot.bot_admin_permissions = {
		"can_restrict_members": False
	}

	services.bot_chats_info_service.get_bot.return_value = bot

	with pytest.raises(AdminBotHasNoRightsError):
		await services.bans_service.kickme(1, 2, "@john")

@pytest.mark.asyncio
async def test_kickme_admin_error(services, bot, member):
	bot.bot_admin_permissions = {
		"can_restrict_members": True
	}

	member.role = "admin"

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member

	with pytest.raises(KickMeAdminError):
		await services.bans_service.kickme(1, 2, "@john")

@pytest.mark.asyncio
async def test_kickme_success(services, bot, member):
	bot.bot_admin_permissions = {
		"can_restrict_members": True
	}

	member.role = "user"

	services.bot_chats_info_service.get_bot.return_value = bot
	services.members_service.get_member.return_value = member
	services.telegram_service.ban_chat_member = AsyncMock()
	services.telegram_service.unban_chat_member = AsyncMock()

	result = await services.bans_service.kickme(1, 2, "@john")

	assert result == "✅ User @john left the chat"

	services.telegram_service.ban_chat_member.assert_awaited_once_with(1, 2)
	services.telegram_service.unban_chat_member.assert_awaited_once()
