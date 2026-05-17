import asyncio
import logging

from core.prefect_support.admin import rename_scheduled_runs


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    asyncio.run(rename_scheduled_runs())
