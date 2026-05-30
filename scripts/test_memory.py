import asyncio

from app.services.memory_service import MemoryService


async def main():

    memory = MemoryService()

    await memory.get_or_create_session(
        "demo-session"
    )

    await memory.save_message(
        "demo-session",
        "user",
        "Hello"
    )

    history = await memory.get_history(
        "demo-session"
    )

    print(history)


asyncio.run(main())