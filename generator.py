import asyncio
import aiofiles
import random
import string
from pathlib import Path

OUTPUT_DIR = "generated"
FILES_COUNT = 20

MIN_WORD_SIZE=4
MAX_WORD_SIZE=15
MIN_FILE_WORDS_COUNT = 2  * 1024
MAX_FILE_WORDS_COUNT = 10 * 1024

async def generate_file(file_name: str, words_count: int) -> None:
    async with aiofiles.open(file_name, "w") as f:
        for _ in range(words_count - 1):
            word_length = random.randint(MIN_WORD_SIZE, MAX_WORD_SIZE)
            random_str = ''.join(random.choices(string.ascii_lowercase, k=word_length))
            await f.write(random_str + ' ')

        word_length = random.randint(MIN_WORD_SIZE, MAX_WORD_SIZE)
        random_str = ''.join(random.choices(string.ascii_lowercase, k=word_length))
        await f.write(random_str + ' ')

    print(f"File '{file_name}' generated!")

async def main() -> None:
    files_dir = Path(OUTPUT_DIR)
    files_dir.mkdir(exist_ok=True)
    random.seed()
    gen_functions = [ 
        generate_file(
            files_dir / f"file_{i}.txt",
            random.randint(MIN_FILE_WORDS_COUNT, MAX_FILE_WORDS_COUNT)
        ) 
        for i in range(FILES_COUNT) 
    ]
    await asyncio.gather(*gen_functions)

if __name__ == "__main__":
    asyncio.run(main())