import argparse
import asyncio
import logging
import os
import shutil
from pathlib import Path


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Сортування файлів за розширенням асинхронно"
    )
    parser.add_argument("source", type=str, help="Вихідна папка")
    parser.add_argument(
        "output",
        type=str,
        nargs="?",
        default="dist",
        help="Цільова папка (за замовчуванням: dist)",
    )
    return parser.parse_args()


async def create_subfolder(output: Path, extension: str) -> Path:
    subfolder = output / extension
    subfolder.mkdir(parents=True, exist_ok=True)
    return subfolder


async def copy_file(file_path: Path, output: Path) -> None:
    ext = file_path.suffix.lstrip(".") or "unknown"

    try:
        subfolder = await create_subfolder(output, ext)
        shutil.copy2(file_path, subfolder / file_path.name)
        logger.info("Файл %s скопійовано у %s", file_path, subfolder)
    except (
        FileNotFoundError,
        PermissionError,
        IsADirectoryError,
        NotADirectoryError,
        OSError,
    ) as err:
        logger.info("Помилка копіювання%s: %s", file_path, err)


async def read_folder(path: Path, output: Path) -> None:
    try:
        for root, _, files in os.walk(path):
            for file in files:
                await copy_file(Path(root) / file, output)
    except Exception as err:
        logger.info("Помилка читання папки %s: %s", path, err)


async def main():
    args = parse_arguments()
    print(f"{args.source}")
    source = Path(args.source)
    output = Path(args.output)

    if not source.exists() or not source.is_dir():
        logger.error("Вихідна папка %s не існує або не є директорією.")
        return
    if not output.exists():
        output.mkdir(parents=True, exist_ok=True)

    logger.info("Починаємо сортування файлів з %s  у %s", source, output)
    try:
        await read_folder(source, output)
        logger.info("Сортування завершено")
    except Exception:
        logger.error("Виникла помилка сортування")


if __name__ == "__main__":
    asyncio.run(main())
