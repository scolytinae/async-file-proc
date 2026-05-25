import asyncio
import logging
import statistics
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from typing import Self

from model import FileProcessingResult, FileReadResult


class Processor:
    """
    Обрабатывает FileReadResult из общей очереди в пуле процессов.

    Используется как async context manager: __aenter__ запускает воркеров
    и пул процессов, __aexit__ дожидается queue.join(), затем отменяет
    воркеров и закрывает пул.

    Remark: ProcessPoolExecutor требует picklable-объект, поэтому
    '_calculate' оставлен статическим методом.
    """

    def __init__(
        self,
        queue: asyncio.Queue,
        workers_count: int = 5,
        work_timeout: float = 2.0,
    ) -> None:
        self._queue = queue
        self._workers_count = workers_count
        self._work_timeout = work_timeout
        self._results: list[FileProcessingResult] = []
        self._workers: list[asyncio.Task] = []
        self._executor: ProcessPoolExecutor | None = None

    @property
    def results(self) -> list[FileProcessingResult]:
        return self._results

    @staticmethod
    def _calculate(read_result: FileReadResult) -> FileProcessingResult:
        words = read_result.text.split()
        if not words:
            return FileProcessingResult(
                file_name=read_result.file_name,
                words_count=0,
                average_word_length=0.0,
                words_top={},
            )

        counter = Counter(words)
        return FileProcessingResult(
            file_name=read_result.file_name,
            words_count=len(words),
            words_top=dict(counter.most_common(10)),
            average_word_length=statistics.mean(len(w) for w in words),
        )

    async def _worker(self, executor: ProcessPoolExecutor) -> None:
        loop = asyncio.get_running_loop()
        while True:
            read_result: FileReadResult = await self._queue.get()
            try:
                future = loop.run_in_executor(
                    executor, Processor._calculate, read_result
                )
                result = await asyncio.wait_for(
                    future, timeout=self._work_timeout
                )
                self._results.append(result)
            except asyncio.TimeoutError:
                logging.warning(
                    "Processing timeout for file %s", read_result.file_name
                )
            except Exception:
                logging.exception(
                    "Processing failed for file %s", read_result.file_name
                )
            finally:
                self._queue.task_done()

    async def __aenter__(self) -> Self:
        self._executor = ProcessPoolExecutor(max_workers=self._workers_count)
        self._workers = [
            asyncio.create_task(self._worker(self._executor))
            for _ in range(self._workers_count)
        ]
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        try:
            await self._queue.join()
        finally:
            for w in self._workers:
                w.cancel()
            await asyncio.gather(*self._workers, return_exceptions=True)
            if self._executor is not None:
                self._executor.shutdown(wait=True)
                self._executor = None
        return False
