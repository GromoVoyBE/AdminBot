import pytest

from unittest.mock import AsyncMock, Mock

from bot.scheduler.scheduler import Scheduler

@pytest.mark.asyncio
async def test_scheduler_success_banned(monkeypatch):
	user = Mock()

	user.chat_id = 1
	user.user_id = 2
	user.restricted_status = "banned"

	services = Mock()

	services.members_service.update_punishments = AsyncMock()
	services.telegram_service.unban_chat_member = AsyncMock()

	scheduler = Scheduler(services)

	class FakeSession:
		async def __aenter__(self):
			return Mock()

		async def __aexit__(self, *args):
			pass

	monkeypatch.setattr(
		"bot.scheduler.scheduler.get_session",
		lambda: FakeSession()
	)

	monkeypatch.setattr(
		"bot.scheduler.scheduler.get_punishments_crud",
		AsyncMock(return_value=[user])
	)

	async def stop_sleep(*args):
		raise RuntimeError()

	monkeypatch.setattr(
		"bot.scheduler.scheduler.asyncio.sleep",
		stop_sleep
	)

	with pytest.raises(RuntimeError):
		await scheduler.run()

	services.telegram_service.unban_chat_member.assert_awaited_once_with(
		1,
		2
	)

	services.members_service.update_punishments.assert_awaited_once_with(
		1,
		2,
		None,
		None,
		None,
		None
	)

@pytest.mark.asyncio
async def test_scheduler_success_muted(monkeypatch):
	user = Mock()

	user.chat_id = 1
	user.user_id = 2
	user.restricted_status = "muted"

	services = Mock()

	services.members_service.update_punishments = AsyncMock()
	services.telegram_service.restrict_chat_member = AsyncMock()

	scheduler = Scheduler(services)

	class FakeSession:
		async def __aenter__(self):
			return Mock()

		async def __aexit__(self, *args):
			pass

	monkeypatch.setattr(
		"bot.scheduler.scheduler.get_session",
		lambda: FakeSession()
	)

	monkeypatch.setattr(
		"bot.scheduler.scheduler.get_punishments_crud",
		AsyncMock(return_value=[user])
	)

	async def stop_sleep(*args):
		raise RuntimeError()

	monkeypatch.setattr(
		"bot.scheduler.scheduler.asyncio.sleep",
		stop_sleep
	)

	with pytest.raises(RuntimeError):
		await scheduler.run()

	services.telegram_service.restrict_chat_member.assert_awaited_once()

	services.members_service.update_punishments.assert_awaited_once_with(
		1,
		2,
		None,
		None,
		None,
		None
	)

@pytest.mark.asyncio
async def test_scheduler_exception(monkeypatch):
	user = Mock()

	user.chat_id = 1
	user.user_id = 2
	user.restricted_status = "banned"

	services = Mock()

	services.telegram_service.unban_chat_member = AsyncMock(
		side_effect=Exception("fail")
	)

	services.members_service.update_punishments = AsyncMock()

	scheduler = Scheduler(services)

	class FakeSession:
		async def __aenter__(self):
			return Mock()

		async def __aexit__(self, *args):
			pass

	monkeypatch.setattr(
		"bot.scheduler.scheduler.get_session",
		lambda: FakeSession()
	)

	monkeypatch.setattr(
		"bot.scheduler.scheduler.get_punishments_crud",
		AsyncMock(return_value=[user])
	)

	async def stop_sleep(*args):
		raise RuntimeError()

	monkeypatch.setattr(
		"bot.scheduler.scheduler.asyncio.sleep",
		stop_sleep
	)

	with pytest.raises(RuntimeError):
		await scheduler.run()

	services.telegram_service.unban_chat_member.assert_awaited_once()
