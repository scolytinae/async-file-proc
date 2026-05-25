import asyncio
import logging
import random
import string
from pathlib import Path

import aiofiles

OUTPUT_DIR = "generated"
FILES_COUNT = 20

MIN_WORD_SIZE = 4
MAX_WORD_SIZE = 15
MIN_FILE_WORDS_COUNT = 2 * 1024
MAX_FILE_WORDS_COUNT = 10 * 1024


def _random_word() -> str:
    length = random.randint(MIN_WORD_SIZE, MAX_WORD_SIZE)
    return "".join(random.choices(string.ascii_lowercase, k=length))


async def generate_file(file_name: Path, words_count: int) -> None:
    text = " ".join(_random_word() for _ in range(words_count))
    async with aiofiles.open(file_name, "w") as f:
        await f.write(text)
    logging.info("File '%s' generated (%d words)", file_name, words_count)


async def main() -> None:
    files_dir = Path(OUTPUT_DIR)
    files_dir.mkdir(exist_ok=True)

    gen_functions = [
        generate_file(
            files_dir / f"file_{i}.txt",
            random.randint(MIN_FILE_WORDS_COUNT, MAX_FILE_WORDS_COUNT),
        )
        for i in range(FILES_COUNT)
    ]
    await asyncio.gather(*gen_functions)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(main())
