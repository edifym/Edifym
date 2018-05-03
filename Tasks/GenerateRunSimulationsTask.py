import itertools
from queue import Queue

import MainConfig
from Tasks.ITask import ITask
import os
from typing import List

from Tasks.RunSingleSimulationTask import RunSingleSimulationTask


class GenerateRunSimulationsTask(ITask):
    main_config: MainConfig
    q: Queue

    def __init__(self, main_config: MainConfig, q: Queue):
        self.main_config = main_config
        self.q = q

    @staticmethod
    def get_immediate_subdirectories(a_dir: str) -> List[str]:
        return [name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))]

    def produce_permutations(self, ids: List[int]) -> List[List[int]]:
        permutations: List[List[int]] = []

        for sub_id in itertools.permutations(ids, self.main_config.num_cpus):
            permutations.append(sub_id)

        return permutations

    def execute(self):
        id = 1
        ids = list(map(int, self.get_immediate_subdirectories('out')))
        permutations = self.produce_permutations(ids)

        for sub_simulation in permutations:
            new_task = RunSingleSimulationTask(self.main_config, self.main_config.num_cpus, sub_simulation, id)
            self.q.put(new_task)
            id += 1
