import json
import aiofiles
import logging
import statistics
from functools import reduce
from model import FileProcessingResult

class StatisticSaver:

    '''
    Считаем общую статистику по полученным результатам
    '''

    def _calc_common_statistic(self, processing_results: List[FileProcessingResult]) -> Dict:
        words_count = reduce(lambda total, item: total + item.words_count, processing_results, 0)
        words_average_len = round(reduce(lambda total, item: total + item.words_count * item.average_word_length, processing_results, 0) / words_count)
        words_top = {}
        for item in processing_results:
            for word, count in item.words_top.items():
                if word in words_top:
                    words_top[word] += count
                else:
                    words_top[word] = count

        sorted_words_top = sorted(words_top.items(), key=lambda item: item[1], reverse=True)
        return {
            "words_count": words_count,
            "words_average_len": words_average_len,
            "words_top": dict(sorted_words_top[:10])
        }

    async def saveStatistic(self, file_name:str, processing_results: List[FileProcessingResult]) -> None:

        out_dict = {
            "common_statistic" : self._calc_common_statistic(processing_results),
            "files_statistic" : [ item.model_dump(mode="json") for item in processing_results ]
        }

        async with aiofiles.open(file_name, "w") as f:
            json_data = json.dumps(out_dict, indent=4)
            await f.write(json_data)

        logging.debug(f"Statistic written to { file_name }")
        