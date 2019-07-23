import json
import os
from datetime import datetime

from MainConfig import MainConfig
from typing import Tuple


def get_lowest_mtime(a_dir: str) -> Tuple[int, str]:
    dirs = os.listdir(a_dir)
    lowest = (9999999999.0, '')

    for name in dirs:
        if name == "zstd-dict" or name == "dict.pkl":
            continue
        path = os.path.join(a_dir, name)
        mtime = os.path.getmtime(path)
        if mtime < lowest[0]:
            lowest = (mtime, name)

    return lowest


if __name__ == "__main__":
    start = datetime.now()
    main_data = json.load(open('config.json'))
    main_config = MainConfig(main_data)

    data = get_lowest_mtime(main_config.stats_dir)
    print(f'{data}')

    end = datetime.now()
    print(f'done {end - start}')
