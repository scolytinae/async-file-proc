import asyncio
import logging
from itertools import chain
from reader import ThreadedReader
from processor import Processor

FILES_DIR = "generated"

logging.basicConfig(level=logging.DEBUG)

async def main():
    queue = asyncio.Queue(500)
    processor_stop_event = asyncio.Event()
    counter_condition = asyncio.Condition()
    reader = ThreadedReader(queue)
    processor = Processor(queue, processor_stop_event, counter_condition)
    try:
        async with asyncio.TaskGroup() as group:
            read_task = group.create_task(reader.read_files(FILES_DIR))
            process_task = group.create_task(processor.process())

            readed_files_count = await read_task
            logging.debug(f"Files readed: {readed_files_count}")
            async with counter_condition:
                await counter_condition.wait_for(lambda: processor.processed_count() >= readed_files_count)
                processor_stop_event.set()

    except* ValueError as eg:
        logging.warning(f"Errors in tasks: {eg.exceptions}") 
    else:
        results = list(chain.from_iterable(process_task.result()))
        logging.debug(f"Get {len(results)} results")
        # to do save results to json


if __name__ == "__main__":
    asyncio.run(main())
