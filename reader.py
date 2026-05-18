import asyncio
import aiofiles
from pathlib import Path

class AsyncReader:
    def __init__(self, files_queue: asyncio.Queue):
        self.__semaphore = asyncio.Semaphore(3)
        self.__queue = files_queue

    async def _read_file(self, file_name: str):
        async with self.__semaphore:
            async with aiofiles.open(file_name, "r") as f:
                return await f.read()
        
    async def _process_file(self, file_name: str):
        print(file_name)
        data = await self._read_file(file_name)
        await self.__queue.put(data)

    async def read_files(self, files_dir: str):
        files = [ f for f in Path(files_dir).iterdir() if f.is_file() ]
        read_functions = [ self._process_file(f) for f in files ]
        await asyncio.gather(*read_functions)
        await self.__queue.put(None)
