
import os

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()


def _load_admin_ids() -> frozenset[int]:
    raw_admin_ids = os.getenv("ADMINS", "").strip()

    if not raw_admin_ids:
        return frozenset()

    admin_ids: set[int] = set()

    for value in raw_admin_ids.split(","):
        value = value.strip()

        if not value:
            continue

        try:
            admin_ids.add(int(value))
        except ValueError:
            raise RuntimeError(
                f"Некорректный ADMIN ID в переменной ADMINS: {value!r}"
            )

    return frozenset(admin_ids)


ADMIN_IDS = _load_admin_ids()


if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN не найден в .env"
    )
