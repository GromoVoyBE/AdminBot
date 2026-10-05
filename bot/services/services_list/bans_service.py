from __future__ import annotations

from aiogram.types import Message, ChatPermissions
from aiogram.exceptions import TelegramBadRequest

from datetime import datetime

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

class BansService:
	def __init__(
		self,
		members_service: MembersService,
		bot_chats_info_service: BotChatsInfoService,
		telegram_service: TelegramService
	):
		self.members_service = members_service
		self.bot_chats_info_service = bot_chats_info_service
		self.telegram_service = telegram_service

	async def ban(
		self,
		chat_id: int,
		user_id: int,
		username: str,
		message: Message,
		delete: bool = False,
		secret: bool = False,
		until_date: datetime | None = None
	) -> str:
		bot = await self.bot_chats_info_service.get_bot(chat_id)
		if not bot.bot_admin_permissions["can_restrict_members"] or \
		   not bot.bot_admin_permissions["can_delete_messages"]:
			raise AdminBotHasNoRightsError

		member = await self.members_service.get_member(chat_id, user_id)
		if member is None:
			raise UserNotFoundError(user_id)
		if member.role in ("creator", "admin"):
			raise CantBanAdminError(user_id)

		if delete:
			if not message.reply_to_message:
				raise NeedReplyToMessageError
			await self.telegram_service.delete_message(
				chat_id,
				message.reply_to_message.message_id
			)

		await self.telegram_service.ban_chat_member(
			chat_id,
			user_id,
			until_date
		)

		if secret:
			await self.telegram_service.delete_message(
				chat_id,
				message.message_id
			)

		user = message.from_user
		await self.members_service.update_punishments(
			chat_id,
			user_id,
			"banned",
			f"@{user.username}" if user.username else user.full_name,
			datetime.utcnow(),
			until_date
		)
		return f"✅ User {username} has been banned"

	async def unban(
		self,
		chat_id: int,
		user_id: int,
		username: str
	) -> str:
		bot = await self.bot_chats_info_service.get_bot(chat_id)
		if not bot.bot_admin_permissions["can_restrict_members"]:
			raise AdminBotHasNoRightsError

		member = await self.members_service.get_member(chat_id, user_id)
		if member is None:
			raise UserNotFoundError(user_id)
		if member.restricted_status != "banned":
			raise UserNotBannedError(user_id)

		await self.telegram_service.unban_chat_member(chat_id, user_id)
		await self.members_service.update_punishments(
			chat_id,
			user_id,
			None,
			None,
			None,
			None
		)
		return f"✅ User {username} has been unbanned"

	async def mute(
		self,
		chat_id: int,
		user_id: int,
		username: str,
		message: Message,
		delete: bool = False,
		secret: bool = False,
		until_date: datetime | None = None
	) -> str:
		bot = await self.bot_chats_info_service.get_bot(chat_id)
		if not bot.bot_admin_permissions["can_restrict_members"] or \
		   not bot.bot_admin_permissions["can_delete_messages"]:
			raise AdminBotHasNoRightsError

		member = await self.members_service.get_member(chat_id, user_id)
		if member is None:
			raise UserNotFoundError(user_id)
		if member.role in ("creator", "admin"):
			raise CantMuteAdminError(user_id)

		if delete:
			if not message.reply_to_message:
				raise NeedReplyToMessageError
			await self.telegram_service.delete_message(
				chat_id,
				message.reply_to_message.message_id
			)

		await self.telegram_service.restrict_chat_member(
			chat_id=chat_id,
			user_id=user_id,
			permissions=ChatPermissions(
				can_send_messages=False,
				can_send_polls=False,
				can_change_info=False,
				can_send_audios=False,
				can_send_photos=False,
				can_send_videos=False,
				can_invite_users=False,
				can_pin_messages=False,
				can_manage_topics=False,
				can_send_documents=False,
				can_send_video_notes=False,
				can_send_voice_notes=False,
				can_send_other_messages=False,
				can_add_web_page_previews=False
			),
			until_date=until_date
		)

		if secret:
			await self.telegram_service.delete_message(
				chat_id,
				message.message_id
			)

		user = message.from_user
		await self.members_service.update_punishments(
			chat_id,
			user_id,
			"muted",
			f"@{user.username}" if user.username else user.full_name,
			datetime.utcnow(),
			until_date
		)
		return f"✅ User {username} has been muted"

	async def unmute(
		self,
		chat_id: int,
		user_id: int,
		username: str
	) -> str:
		bot = await self.bot_chats_info_service.get_bot(chat_id)
		if not bot.bot_admin_permissions["can_restrict_members"]:
			raise AdminBotHasNoRightsError

		member = await self.members_service.get_member(chat_id, user_id)
		if member is None:
			raise UserNotFoundError(user_id)
		if member.restricted_status != "muted":
			raise UserNotMutedError(user_id)

		await self.telegram_service.restrict_chat_member(
			chat_id=chat_id,
			user_id=user_id,
			permissions=ChatPermissions(
				can_send_messages=True,
				can_send_polls=True,
				can_change_info=False,
				can_send_audios=True,
				can_send_photos=True,
				can_send_videos=True,
				can_invite_users=True,
				can_pin_messages=False,
				can_manage_topics=False,
				can_send_documents=True,
				can_send_video_notes=True,
				can_send_voice_notes=True,
				can_send_other_messages=True,
				can_add_web_page_previews=True,
			)
		)
		await self.members_service.update_punishments(
			chat_id,
			user_id,
			None,
			None,
			None,
			None
		)		
		return f"✅ User {username} has been unmuted"

	async def kick(
		self,
		chat_id: int,
		user_id: int,
		username: str,
		message: Message,
		delete: bool = False,
		secret: bool = False
	) -> str:
		bot = await self.bot_chats_info_service.get_bot(chat_id)
		if not bot.bot_admin_permissions["can_restrict_members"] or \
		   not bot.bot_admin_permissions["can_delete_messages"]:
			raise AdminBotHasNoRightsError

		member = await self.members_service.get_member(chat_id, user_id)
		if member is None:
			raise UserNotFoundError(user_id)
		if member.role in ("creator", "admin"):
			raise CantKickAdminError(user_id)

		if delete:
			if not message.reply_to_message:
				raise NeedReplyToMessageError
			await self.telegram_service.delete_message(
				chat_id,
				message.reply_to_message.message_id
			)

		await self.telegram_service.ban_chat_member(chat_id, user_id)
		await self.telegram_service.unban_chat_member(chat_id, user_id)

		if secret:
			await self.telegram_service.delete_message(
				chat_id,
				message.message_id
			)
		return f"✅ User {username} has been kicked"

	async def kickme(self, chat_id, user_id, username) -> str:
		bot = await self.bot_chats_info_service.get_bot(chat_id)
		if not bot.bot_admin_permissions["can_restrict_members"]:
			raise AdminBotHasNoRightsError

		member = await self.members_service.get_member(chat_id, user_id)
		if member.role in ("creator", "admin"):
			raise KickMeAdminError

		await self.telegram_service.ban_chat_member(chat_id, user_id)
		await self.telegram_service.unban_chat_member(chat_id, user_id)
		return f"✅ User {username} left the chat"
