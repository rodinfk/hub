import asyncio
from handlers import dp, bot

from data_driver import sql


async def main():
    sql.create_tables()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())