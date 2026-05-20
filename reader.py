import asyncio
import aiofiles
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from model import FileReadResult

class AsyncReader:
    '''
    Тут читатель сделан через aiofiles
    '''
    def __init__(self, files_queue: asyncio.Queue):
        self.__semaphore = asyncio.Semaphore(3)
        self.__queue = files_queue

    async def _read_file(self, file_name: str) -> str: 
        async with self.__semaphore:
            async with aiofiles.open(file_name, "r") as f:
                return await f.read()
        
    async def _process_file(self, file_name: str) -> None:
        data = await self._read_file(file_name)
        await self.__queue.put(
            FileReadResult(
                file_name=file_name,
                text=data
            )
        )

    async def read_files(self, files_dir: str) -> None:
        files = [ f for f in Path(files_dir).iterdir() if f.is_file() ]
        read_functions = [ self._process_file(f) for f in files ]
        await asyncio.gather(*read_functions)


class ThreadedReader:
    '''
    Тут читатель реализован через ThreadPoolExecutor
    '''
    def __init__(self, files_queue: asyncio.Queue):
        self.__semaphore = asyncio.Semaphore(3)
        self.__queue = files_queue

    def _read_file(self, file_name: Path) -> str:
        with open(file_name, "r") as f:
            return f.read()

    async def _process_file(self, executor: ThreadPoolExecutor, file_name: Path) -> None:
        async with self.__semaphore:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(executor, self._read_file, file_name)
            await self.__queue.put(
                FileReadResult(
                    file_name=str(file_name),
                    text=result
                )
            )
            
    async def read_files(self, files_dir: str) -> int:
        files = [ f for f in Path(files_dir).iterdir() if f.is_file() ]
        with ThreadPoolExecutor(max_workers=5) as executor:            
            read_functions = [ self._process_file(executor, f) for f in files ]
            await asyncio.gather(*read_functions)
        return len(files)
