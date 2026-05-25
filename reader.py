import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import aiofiles

from model import FileReadResult


class AsyncReader:
    """
    Читатель на aiofiles. Семафор ограничивает число одновременно
    открытых файловых дескрипторов.
    """

    def __init__(
        self,
        files_queue: asyncio.Queue,
        max_concurrency: int = 5,
    ) -> None:
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._queue = files_queue

    async def _read_file(self, file_name: Path) -> str:
        async with self._semaphore:
            async with aiofiles.open(file_name, "r") as f:
                return await f.read()

    async def _process_file(self, file_name: Path) -> None:
        try:
            data = await self._read_file(file_name)
        except OSError:
            logging.exception("Failed to read file %s", file_name)
            return

        await self._queue.put(
            FileReadResult(file_name=str(file_name), text=data)
        )

    async def read_files(self, files_dir: str) -> int:
        files = [f for f in Path(files_dir).iterdir() if f.is_file()]
        await asyncio.gather(*(self._process_file(f) for f in files))
        return len(files)


class ThreadedReader:
    """
    Читатель на ThreadPoolExecutor. Без отдельного семафора —
    конкурентность ограничивается размером пула.
    """

    def __init__(
        self,
        files_queue: asyncio.Queue,
        max_workers: int = 5,
    ) -> None:
        self._queue = files_queue
        self._max_workers = max_workers

    @staticmethod
    def _read_file(file_name: Path) -> str:
        with open(file_name, "r") as f:
            return f.read()

    async def _process_file(
        self, executor: ThreadPoolExecutor, file_name: Path
    ) -> None:
        loop = asyncio.get_running_loop()
        try:
            text = await loop.run_in_executor(
                executor, ThreadedReader._read_file, file_name
            )
        except OSError:
            logging.exception("Failed to read file %s", file_name)
            return

        await self._queue.put(
            FileReadResult(file_name=str(file_name), text=text)
        )

    async def read_files(self, files_dir: str) -> int:
        files = [f for f in Path(files_dir).iterdir() if f.is_file()]
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            await asyncio.gather(
                *(self._process_file(executor, f) for f in files)
            )
        return len(files)
