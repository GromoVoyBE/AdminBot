import pytest

from unittest.mock import Mock, AsyncMock, patch

from bot.services.services_list.core.telegram_service import TelegramService

@pytest.fixture
def tg_member():
	member = Mock()

	member.status = "member"

	member.can_send_messages = True
	member.can_send_audios = True
	member.can_send_documents = True
	member.can_send_photos = True
	member.can_send_videos = True
	member.can_send_video_notes = True
	member.can_send_voice_notes = True
	member.can_send_polls = True
	member.can_send_other_messages = True
	member.can_add_web_page_previews = True
	member.can_change_info = False
	member.can_invite_users = False
	member.can_pin_messages = False
	member.can_manage_topics = False

	member.model_dump.return_value = {"id": 1}

	member.__class__.__name__ = "ChatMemberMember"

	return member


def test_tg_member_key():
	assert TelegramService._tg_member_key(1, 2) == "tg_member:1:2"

def test_tg_admins_key():
	assert TelegramService._tg_admins_key(1) == "tg_admins:1"

def test_deserialize_success():
	fake_cls = Mock()
	fake_obj = Mock()

	fake_cls.model_validate.return_value = fake_obj

	data = {
		"_type": "member",
		"data": {"id": 123}
	}

	with patch.dict(
		"bot.services.services_list.core.telegram_service.CHAT_MEMBER_TYPES",
		{"member": fake_cls}
	):
		result = TelegramService._deserialize(data)

	fake_cls.model_validate.assert_called_once_with({"id": 123})
	assert result == fake_obj

def test_extract_user_permissions_success_creator():
	member = Mock()
	member.status = "creator"

	result = TelegramService.extract_user_permissions(member)

	assert result == {"all": True}

def test_extract_user_permissions_success_member():
	member = Mock()

	member.status = "member"
	member.can_send_messages = True
	member.can_send_audios = False
	member.can_send_documents = True
	member.can_send_photos = True
	member.can_send_videos = True
	member.can_send_video_notes = True
	member.can_send_voice_notes = True
	member.can_send_polls = True
	member.can_send_other_messages = True
	member.can_add_web_page_previews = True
	member.can_change_info = False
	member.can_invite_users = False
	member.can_pin_messages = False
	member.can_manage_topics = False

	result = TelegramService.extract_user_permissions(member)

	assert result["can_send_messages"] is True
	assert result["can_send_audios"] is False

def test_extract_admin_permissions_success_creator():
	member = Mock()
	member.status = "creator"

	result = TelegramService.extract_admin_permissions(member)

	assert result == {"all": True}

def test_extract_admin_permissions_success_admin():
	member = Mock()

	member.status = "administrator"

	member.can_change_info = True
	member.can_delete_messages = True
	member.can_invite_users = True
	member.can_restrict_members = True
	member.can_pin_messages = True
	member.can_promote_members = True
	member.can_manage_video_chats = True
	member.can_manage_topics = True
	member.can_post_stories = True
	member.can_edit_stories = True
	member.can_delete_stories = True

	result = TelegramService.extract_admin_permissions(member)

	assert result["can_delete_messages"] is True


@pytest.mark.parametrize(
	"status,is_member,expected",
	[
		("creator", True, "creator"),
		("administrator", True, "admin"),
		("member", True, "user"),
		("kicked", False, "kicked"),
		("restricted", True, "restricted"),
		("restricted", False, "left"),
		("left", False, "left"),
		("unknown", True, "user"),
	]
)
def test_status_to_role_db_success(status, is_member, expected):
	assert TelegramService.status_to_role_db(
		status,
		is_member
	) == expected

@pytest.mark.asyncio
async def test_invalidate_user_admins_cache_success(
	telegram_service,
	monkeypatch
):
	delete_cache = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.telegram_service.delete_cache",
		delete_cache
	)

	await telegram_service.invalidate_user_admins_cache(1, 2)

	assert delete_cache.await_count == 2

@pytest.mark.asyncio
async def test_get_chat_member_success_from_cache(
	telegram_service,
	monkeypatch
):
	member = Mock()

	deserialize = Mock(return_value=member)

	monkeypatch.setattr(
		"bot.services.services_list.core.telegram_service.get_cache",
		AsyncMock(return_value={"cached": True})
	)
	monkeypatch.setattr(
		TelegramService,
		"_deserialize",
		deserialize
	)

	result = await telegram_service.get_chat_member(1, 2)

	assert result == member

@pytest.mark.asyncio
async def test_get_chat_member_success_from_api(
	telegram_service,
	tg_member,
	monkeypatch
):
	set_cache = AsyncMock()

	telegram_service.bot.get_chat_member = AsyncMock(
		return_value=tg_member
	)

	monkeypatch.setattr(
		"bot.services.services_list.core.telegram_service.get_cache",
		AsyncMock(return_value=None)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.telegram_service.set_cache",
		set_cache
	)

	result = await telegram_service.get_chat_member(1, 2)

	assert result == tg_member

	set_cache.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_chat_administrators_success_from_cache(
	telegram_service,
	monkeypatch
):
	admin = Mock()

	deserialize = Mock(return_value=admin)

	monkeypatch.setattr(
		"bot.services.services_list.core.telegram_service.get_cache",
		AsyncMock(return_value=[{"cached": True}])
	)
	monkeypatch.setattr(
		TelegramService,
		"_deserialize",
		deserialize
	)

	result = await telegram_service.get_chat_administrators(1)

	assert result == [admin]

@pytest.mark.asyncio
async def test_get_chat_administrators_success_from_api(
	telegram_service,
	tg_member,
	monkeypatch
):
	set_cache = AsyncMock()

	telegram_service.bot.get_chat_administrators = AsyncMock(
		return_value=[tg_member]
	)

	monkeypatch.setattr(
		"bot.services.services_list.core.telegram_service.get_cache",
		AsyncMock(return_value=None)
	)
	monkeypatch.setattr(
		"bot.services.services_list.core.telegram_service.set_cache",
		set_cache
	)

	result = await telegram_service.get_chat_administrators(1)

	assert result == [tg_member]

	set_cache.assert_awaited_once()

@pytest.mark.asyncio
async def test_promote_chat_member_success(telegram_service, monkeypatch):
	delete_cache = AsyncMock()

	telegram_service.bot.promote_chat_member = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.telegram_service.delete_cache",
		delete_cache
	)

	await telegram_service.promote_chat_member(
		1,
		2,
		{"can_delete_messages": True}
	)

	telegram_service.bot.promote_chat_member.assert_awaited_once()

	assert delete_cache.await_count == 2

@pytest.mark.asyncio
async def test_ban_chat_member_success(telegram_service, monkeypatch):
	delete_cache = AsyncMock()

	telegram_service.bot.ban_chat_member = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.telegram_service.delete_cache",
		delete_cache
	)

	await telegram_service.ban_chat_member(1, 2)

	telegram_service.bot.ban_chat_member.assert_awaited_once()
	delete_cache.assert_awaited_once()

@pytest.mark.asyncio
async def test_unban_chat_member_success(telegram_service, monkeypatch):
	delete_cache = AsyncMock()

	telegram_service.bot.unban_chat_member = AsyncMock()

	monkeypatch.setattr(
		"bot.services.services_list.core.telegram_service.delete_cache",
		delete_cache
	)

	await telegram_service.unban_chat_member(1, 2)

	telegram_service.bot.unban_chat_member.assert_awaited_once()
	delete_cache.assert_awaited_once()

@pytest.mark.asyncio
async def test_restrict_chat_member_success(telegram_service, monkeypatch):
	delete_cache = AsyncMock()

	telegram_service.bot.restrict_chat_member = AsyncMock()

	permissions = Mock()

	monkeypatch.setattr(
		"bot.services.services_list.core.telegram_service.delete_cache",
		delete_cache
	)

	await telegram_service.restrict_chat_member(1, 2, permissions)

	telegram_service.bot.restrict_chat_member.assert_awaited_once()
	delete_cache.assert_awaited_once()

@pytest.mark.asyncio
async def test_delete_message_success(telegram_service):
	telegram_service.bot.delete_message = AsyncMock()

	await telegram_service.delete_message(1, 100)

	telegram_service.bot.delete_message.assert_awaited_once_with(
		1,
		100
	)
