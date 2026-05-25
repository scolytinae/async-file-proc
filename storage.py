import json
import logging
from collections import Counter

import aiofiles

from model import FileProcessingResult


class StatisticSaver:
    """
    Считает общую статистику по полученным результатам и пишет JSON.
    """

    @staticmethod
    def _calc_common_statistic(
        processing_results: list[FileProcessingResult],
    ) -> dict:
        if not processing_results:
            return {
                "words_count": 0,
                "words_average_len": 0.0,
                "words_top": {},
            }

        words_count = sum(item.words_count for item in processing_results)
        if words_count == 0:
            words_average_len = 0.0
        else:
            weighted_sum = sum(
                item.words_count * item.average_word_length
                for item in processing_results
            )
            words_average_len = round(weighted_sum / words_count, 2)

        words_top: Counter[str] = Counter()
        for item in processing_results:
            words_top.update(item.words_top)

        return {
            "words_count": words_count,
            "words_average_len": words_average_len,
            "words_top": dict(words_top.most_common(10)),
        }

    async def save_statistic(
        self,
        file_name: str,
        processing_results: list[FileProcessingResult],
    ) -> None:
        out_dict = {
            "common_statistic": self._calc_common_statistic(processing_results),
            "files_statistic": [
                item.model_dump(mode="json") for item in processing_results
            ],
        }

        async with aiofiles.open(file_name, "w") as f:
            await f.write(json.dumps(out_dict, indent=4, ensure_ascii=False))

        logging.info("Statistic written to %s", file_name)
