import asyncio
import logging
import statistics
from model import FileProcessingResult
from concurrent.futures import ProcessPoolExecutor


class Processor:
    '''
    Обработка файлов реализована через ProcessPoolExecutor
    '''
    def __init__(self, queue: asyncio.Queue, stop_event: asyncio.Event, processed_condition: asyncio.Condition):
        self.__workers_count = 5
        self.__work_timeout = 2.0
        self.__queue = queue
        self.__stop_event = stop_event
        self.__results = []
        self.__processed_count = 0
        self.__processed_condition = processed_condition

    @staticmethod
    def _calculate(text: str) -> FileProcessingResult:
        words_count = 0
        words_dict = {}
        words_len = []
        for word in text.split():
            words_count += 1
            words_len.append(len(word))
            if word in words_dict:
                words_dict[word] = words_dict[word] + 1
            else:
                words_dict[word] = 1

        sorted_by_count = sorted(words_dict.items(), key=lambda item: item[1], reverse=True)
        sorted_by_len = sorted(words_dict.keys(), key=lambda item: len(item))
        return FileProcessingResult(
            words_count=words_count,
            words_top=dict(sorted_by_count[:10]),
            average_word_length=statistics.median(words_len)
        )

    def processed_count(self):
        return self.__processed_count

    async def _process(self, executor: ProcessPoolExecutor) -> FileProcessingResult | None:
        results = []
        while not self.__stop_event.is_set():
            try:
                text = await asyncio.wait_for(self.__queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(executor, Processor._calculate, text)
            try:
                result = await asyncio.wait_for(future, timeout=self.__work_timeout)
            except asyncio.TimeoutError:
                logging.warn("Processing too long...")
            else:
                results.append(result)

            async with self.__processed_condition:
                self.__processed_count += 1
                logging.debug(f"Processed count: {self.__processed_count}")
                self.__processed_condition.notify_all()
        
        return results

    async def process(self) -> None:
        with ProcessPoolExecutor(max_workers=self.__workers_count) as executor:
            process_functions = [ self._process(executor) for _ in range(self.__workers_count) ]
            return await asyncio.gather(*process_functions)
        