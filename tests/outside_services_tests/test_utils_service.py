import pytest

from datetime import datetime
from unittest.mock import AsyncMock, Mock

from aiogram.exceptions import TelegramBadRequest

from bot.exceptions import (
	TooManyArgumentsError,
	InvalidTimeArgumentError,
	CantModerateAdminBotError,
	UserNotFoundError,
	InvalidUsernameOrIdInArgumentsError,
	DoubleUsernameInArgumentsError,
	NoUserInArgumentsError
)

from bot.services.services_list.utils_service import UtilsService

def test_get_end_time_too_many_arguments():
	with pytest.raises(TooManyArgumentsError):
		UtilsService.get_end_time(["/ban", "@user", "60", "123"])

def test_get_end_time_success_one_argument():
	result = UtilsService.get_end_time(["/ban"])

	assert result.year == 3000

def test_get_end_time_success_username_only():
	result = UtilsService.get_end_time(["/ban", "@user"])

	assert result.year == 3000

def test_get_end_time_invalid_three_argument():
	with pytest.raises(InvalidTimeArgumentError):
		result = UtilsService.get_end_time(["/ban", "asd"])

def test_get_end_time_invalid_two_argument():
	with pytest.raises(InvalidTimeArgumentError):
		UtilsService.get_end_time(["/ban", "@user", "abc"])

def test_get_end_time_zero():
	with pytest.raises(InvalidTimeArgumentError):
		UtilsService.get_end_time(["/ban", "@user", "0"])

def test_get_end_time_negative():
	with pytest.raises(InvalidTimeArgumentError):
		UtilsService.get_end_time(["/ban", "@user", "-100"])

def test_get_end_time_temporary():
	result = UtilsService.get_end_time(["/ban", "@user", "60"])

	assert result > datetime.utcnow()


@pytest.mark.asyncio
async def test_get_id_adminbot(services):
	with pytest.raises(CantModerateAdminBotError):
		await services.utils_service.get_id(1, "@moderation_control_bot")

@pytest.mark.asyncio
async def test_get_id_user_not_found(services):
	services.members_service.get_member_by_username.return_value = None

	with pytest.raises(UserNotFoundError):
		await services.utils_service.get_id(1, "@john")

@pytest.mark.asyncio
async def test_get_id_success_username_found(services, member):
	member.user_id = 777

	services.members_service.get_member_by_username.return_value = member

	result = await services.utils_service.get_id(1, "@john")

	assert result == 777

	services.members_service.get_member_by_username.assert_awaited_once_with(
		1,
		"john"
	)

@pytest.mark.asyncio
async def test_get_id_zero(services):
	with pytest.raises(InvalidUsernameOrIdInArgumentsError):
		await services.utils_service.get_id(1, "0")

@pytest.mark.asyncio
async def test_get_id_success_numeric(services):
	result = await services.utils_service.get_id(1, "123456")

	assert result == 123456

@pytest.mark.asyncio
async def test_get_id_invalid_argument(services):
	with pytest.raises(InvalidUsernameOrIdInArgumentsError):
		await services.utils_service.get_id(1, "user!")


@pytest.mark.asyncio
async def test_get_id_and_name_reply_too_many_arguments(
	services,
	message,
	reply
):
	reply.from_user = Mock()
	message.reply_to_message = reply

	with pytest.raises(TooManyArgumentsError):
		await services.utils_service.get_id_and_name(
			message,
			["/ban", "@john", "60"]
		)

@pytest.mark.asyncio
async def test_get_id_and_name_reply_double_username(
	services,
	message,
	reply
):
	reply.from_user = Mock()
	message.reply_to_message = reply

	with pytest.raises(DoubleUsernameInArgumentsError):
		await services.utils_service.get_id_and_name(message, ["/ban", "@john"])

@pytest.mark.asyncio
async def test_get_id_and_name_reply_invalid_time(
	services,
	message,
	reply
):
	reply.from_user = Mock()
	message.reply_to_message = reply

	with pytest.raises(InvalidTimeArgumentError):
		await services.utils_service.get_id_and_name(message, ["/ban", "abc"])

@pytest.mark.asyncio
async def test_get_id_and_name_success_reply_username(
	services,
	message,
	reply,
	user
):
	user.id = 100
	user.username = "john"

	reply.from_user = user
	message.reply_to_message = reply

	result = await services.utils_service.get_id_and_name(message, ["/ban"])

	assert result == (100, "@john")

@pytest.mark.asyncio
async def test_get_id_and_name_success_reply_fullname(
	services,
	message,
	reply,
	user
):
	user.id = 100
	user.username = None
	user.full_name = "John Doe"

	reply.from_user = user
	message.reply_to_message = reply

	result = await services.utils_service.get_id_and_name(message, ["/ban"])

	assert result == (100, "John Doe")

@pytest.mark.asyncio
async def test_get_id_ad_name_no_user_in_arguments(
	services,
	message
):
	message.reply_to_message = None

	with pytest.raises(NoUserInArgumentsError):
		await services.utils_service.get_id_and_name(message, ["/ban"])

@pytest.mark.asyncio
async def test_get_id_and_name_kick_too_many_arguments(
	services,
	message
):
	message.reply_to_message = None

	with pytest.raises(TooManyArgumentsError):
		await services.utils_service.get_id_and_name(
			message,
			["/kick", "@john", "60"]
		)

@pytest.mark.asyncio
async def test_get_id_and_name_user_not_found_via_telegram(
	services,
	message
):
	message.reply_to_message = None
	message.chat.id = 123

	services.utils_service.get_id = AsyncMock(return_value=555)

	services.telegram_service.get_chat_member.side_effect = TelegramBadRequest(
		method=Mock(),
		message="PARTICIPANT_ID_INVALID"
	)

	with pytest.raises(UserNotFoundError):
		await services.utils_service.get_id_and_name(message, ["/ban", "@john"])

@pytest.mark.asyncio
async def test_get_id_and_name_success_username(
	services,
	message,
	member
):
	message.reply_to_message = None
	message.chat.id = 123

	member.user.username = "john"

	services.utils_service.get_id = AsyncMock(return_value=555)
	services.telegram_service.get_chat_member.return_value = member

	result = await services.utils_service.get_id_and_name(
		message,
		["/ban", "@john"]
	)

	assert result == (555, "@john")

@pytest.mark.asyncio
async def test_get_id_and_name_success_fullname(
	services,
	message,
	member
):
	message.reply_to_message = None
	message.chat.id = 123

	member.user.username = None
	member.user.full_name = "John Doe"

	services.utils_service.get_id = AsyncMock(return_value=555)
	services.telegram_service.get_chat_member.return_value = member

	result = await services.utils_service.get_id_and_name(
		message,
		["/ban", "@john"]
	)

	assert result == (555, "John Doe")
