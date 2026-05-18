import asyncio
from reader import AsyncReader

FILES_DIR = "generated"

async def main():
    queue = asyncio.Queue(500)
    reader = AsyncReader(queue)
    await reader.read_files(FILES_DIR)
    print(queue.qsize())


if __name__ == "__main__":
    asyncio.run(main())
