import asyncio

class ThreadedReader:
    def __init__(self, files_queue: asyncio.Queue):
        self.__semaphore = asyncio.Semaphore(3)
        self.__queue = files_queue

    async def _read_file(self, file_name: string):
        pass

    async def read_files(self, files_dir: string):
        pass

