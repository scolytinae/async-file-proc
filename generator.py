import asyncio
import aiofiles
import random
import string
from pathlib import Path

OUTPUT_DIR = "generated"
FILES_COUNT = 20
MIN_FILE_TEXT_LENGTH = 2 * 1024 * 1024
MAX_FILE_TEXT_LENGTH = 10 * 1024 * 1024

async def generate_file(file_name: str, text_length: int) -> None:
    random_str = ''.join(random.choices(string.ascii_lowercase, k=text_length))
    async with aiofiles.open(file_name, "w") as f:
        await f.write(random_str)
    
    print(f"File '{file_name}' generated!")

async def main() -> None:
    files_dir = Path(OUTPUT_DIR)
    files_dir.mkdir(exist_ok=True)
    random.seed()
    gen_functions = [ 
        generate_file(
            files_dir / f"file_{i}.txt",
            random.randint(MIN_FILE_TEXT_LENGTH, MAX_FILE_TEXT_LENGTH)
        ) 
        for i in range(FILES_COUNT) 
    ]
    await asyncio.gather(*gen_functions)

if __name__ == "__main__":
    asyncio.run(main())