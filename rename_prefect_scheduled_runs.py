import asyncio

from core.prefect_support.admin import rename_scheduled_runs


if __name__ == "__main__":
    asyncio.run(rename_scheduled_runs())
