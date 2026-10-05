from __future__ import annotations

from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

from datetime import datetime, timedelta

from bot.exceptions import (
	TooManyArgumentsError,
	InvalidTimeArgumentError,
	CantModerateAdminBotError,
	UserNotFoundError,
	InvalidUsernameOrIdInArgumentsError,
	DoubleUsernameInArgumentsError,
	NoUserInArgumentsError,
)

class UtilsService:
	def __init__(
		self,
		members_service: MembersService,
		telegram_service: TelegramService
	):
		self.members_service = members_service
		self.telegram_service = telegram_service

	@staticmethod
	def get_end_time(args: list) -> datetime:
		if len(args) > 3:
			raise TooManyArgumentsError

		if len(args) == 1:
			return datetime(3000, 1, 1)

		if not args[-1].isdigit():
			if len(args) == 2 and args[-1].startswith("@"):
				return datetime(3000, 1, 1)
			raise InvalidTimeArgumentError

		seconds = int(args[-1])
		if seconds <= 0:
			raise InvalidTimeArgumentError
		return datetime.utcnow() + timedelta(seconds=seconds)

	async def get_id(self, chat_id: int, target: int | str) -> int:
		if target.startswith("@"):
			username = target[1:]
			if username == "moderation_control_bot":
				raise CantModerateAdminBotError
			member = await self.members_service.get_member_by_username(
				chat_id,
				username
			)
			if member is None:
				raise UserNotFoundError(username)
			return member.user_id
		if target.isdigit():
			if int(target) == 0:
				raise InvalidUsernameOrIdInArgumentsError
			return int(target)
		raise InvalidUsernameOrIdInArgumentsError
	
	async def get_id_and_name(self, message: Message, args: list):
		if message.reply_to_message:
			if len(args) > 2:
				raise TooManyArgumentsError
			if len(args) == 2:
				if args[1].startswith("@"):
					raise DoubleUsernameInArgumentsError
				if not args[1].isdigit():
					raise InvalidTimeArgumentError
			user = message.reply_to_message.from_user
			user_id = user.id
			username = f"@{user.username}" if user.username else user.full_name
			return user_id, username

		if len(args) < 2:
			raise NoUserInArgumentsError

		if args[0] == "/kick" and len(args) > 2:
			raise TooManyArgumentsError

		user_id = await self.get_id(message.chat.id, args[1])

		try:
			member = await self.telegram_service.get_chat_member(
				message.chat.id,
				user_id
			)
		except TelegramBadRequest as e:
			if "PARTICIPANT_ID_INVALID" in str(e):
				raise UserNotFoundError(user_id)
			raise

		name = f"@{member.user.username}" if member.user.username \
										  else member.user.full_name
		return user_id, name
