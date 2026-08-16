from unittest.mock import AsyncMock, MagicMock

import pytest

from gateway.config import GatewayConfig, Platform, PlatformConfig
from gateway.platforms.base import SendResult
from gateway.run import GatewayRunner
from gateway.session import SessionSource


def _make_source() -> SessionSource:
    return SessionSource(
        platform=Platform.SLACK,
        chat_id="C123",
        chat_type="channel",
        user_id="U123",
        thread_id="111.222",
    )


def _make_runner(extra=None, platform=Platform.SLACK):
    runner = object.__new__(GatewayRunner)
    runner.config = GatewayConfig(
        platforms={
            platform: PlatformConfig(enabled=True, token="***", extra=extra or {})
        }
    )
    adapter = MagicMock()
    adapter.send = AsyncMock(return_value=SendResult(success=True, message_id="public-1"))
    adapter.send_private_notice = AsyncMock(return_value=SendResult(success=True, message_id="private-1"))
    runner.adapters = {platform: adapter}
    return runner, adapter


@pytest.mark.asyncio
async def test_deliver_platform_notice_uses_private_delivery_when_configured():
    runner, adapter = _make_runner(extra={"notice_delivery": "private"})

    await runner._deliver_platform_notice(_make_source(), "hello")

    adapter.send_private_notice.assert_awaited_once_with(
        "C123",
        "U123",
        "hello",
        metadata={"thread_id": "111.222"},
    )
    adapter.send.assert_not_awaited()


@pytest.mark.asyncio
async def test_whatsapp_group_operator_notice_is_suppressed():
    runner, adapter = _make_runner(platform=Platform.WHATSAPP)
    source = SessionSource(
        platform=Platform.WHATSAPP,
        chat_id="120363428948689789@g.us",
        chat_type="group",
        user_id="9720000000001@s.whatsapp.net",
    )

    await runner._deliver_platform_notice(source, "No home channel is set")

    adapter.send.assert_not_awaited()
    adapter.send_private_notice.assert_not_awaited()


@pytest.mark.asyncio
async def test_dm_operator_notice_still_uses_public_chat():
    runner, adapter = _make_runner()
    source = SessionSource(
        platform=Platform.SLACK,
        chat_id="D123",
        chat_type="dm",
        user_id="U123",
    )

    await runner._deliver_platform_notice(source, "hello")

    adapter.send.assert_awaited_once()


