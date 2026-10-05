import pytest
from unittest.mock import Mock, AsyncMock, patch

from bot.storages.postgre.database import get_session, init_db

@pytest.mark.asyncio
async def test_get_session_success(monkeypatch):
	session = AsyncMock()

	class FakeContext:
		async def __aenter__(self):
			return session

		async def __aexit__(self, *args):
			pass

	monkeypatch.setattr(
		"bot.storages.postgre.database.async_session",
		lambda: FakeContext()
	)

	async with get_session() as s:
		assert s == session

	session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_session_exception(monkeypatch):
	session = AsyncMock()

	class FakeContext:
		async def __aenter__(self):
			return session

		async def __aexit__(self, *args):
			pass

	monkeypatch.setattr(
		"bot.storages.postgre.database.async_session",
		lambda: FakeContext()
	)

	with pytest.raises(ValueError):
		async with get_session():
			raise ValueError()

	session.rollback.assert_awaited_once()

@pytest.mark.asyncio
async def test_init_db(monkeypatch):
	conn = AsyncMock()

	class FakeContext:
		async def __aenter__(self):
			return conn

		async def __aexit__(self, *args):
			pass

	engine_mock = Mock()
	engine_mock.begin.return_value = FakeContext()

	monkeypatch.setattr(
		"bot.storages.postgre.database.engine",
		engine_mock
	)

	await init_db()

	conn.run_sync.assert_awaited_once()
