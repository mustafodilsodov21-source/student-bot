
import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message


class ManualThrottlingMiddleware(BaseMiddleware):
    """
    Simple per-user message throttling middleware.

    Prevents users from sending messages too frequently.
    """

    def __init__(
        self,
        delay_seconds: float = 2.0,
    ) -> None:
        self.delay = delay_seconds
        self.user_last_time: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        """
        Process incoming messages and apply throttling.
        """

        user = event.from_user

        if user is None:
            return await handler(event, data)

        user_id = user.id
        current_time = time.monotonic()

        last_time = self.user_last_time.get(
            user_id,
            0.0,
        )

        elapsed = current_time - last_time

        if elapsed < self.delay:
            await event.answer(
                "Iltimos, sekinroq yozing 🕒"
            )
            return

        self.user_last_time[user_id] = current_time

        return await handler(event, data)

