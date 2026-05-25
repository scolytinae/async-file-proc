import asyncio
import logging

from processor import Processor
from reader import ThreadedReader
from storage import StatisticSaver

FILES_DIR = "generated"
OUT_FILE = "out.json"
QUEUE_SIZE = 500
WORKERS_COUNT = 5
READER_THREADS = 5
WORK_TIMEOUT_SEC = 2.0


async def main() -> None:
    queue: asyncio.Queue = asyncio.Queue(QUEUE_SIZE)
    reader = ThreadedReader(queue, max_workers=READER_THREADS)
    processor = Processor(
        queue,
        workers_count=WORKERS_COUNT,
        work_timeout=WORK_TIMEOUT_SEC,
    )

    try:
        async with processor:
            files_count = await reader.read_files(FILES_DIR)
            logging.info("Files read: %d", files_count)
    except Exception:
        logging.exception("Pipeline failed")

    results = processor.results
    logging.info("Got %d results", len(results))

    if results:
        await StatisticSaver().save_statistic(OUT_FILE, results)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(main())
