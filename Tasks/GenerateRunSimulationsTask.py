import itertools
from multiprocessing import Queue, Value

import MainConfig
from Tasks.ITask import ITask
import os
from typing import List

from Tasks.RunSingleSimulationTask import RunSingleSimulationTask


class GenerateRunSimulationsTask(ITask):
    main_config: MainConfig
    q: Queue
    shm_quit: Value

    def __init__(self, main_config: MainConfig, q: Queue, shm_quit: Value):
        self.main_config = main_config
        self.q = q
        self.shm_quit = shm_quit

    @staticmethod
    def get_immediate_subdirectories(a_dir: str) -> List[str]:
        dirs = os.listdir(a_dir)
        #eqcheck = dirs[0][0] != 'r'
        #print(f'dirs: {dirs} {dirs[0][0]} {eqcheck}')
        subdirs = []

        for name in dirs:
            if os.path.isdir(os.path.join(a_dir, name)) and name[0] != 'r':
                subdirs.append(name)

        #subdirs = [name for name in dirs if os.path.isdir(os.path.join(a_dir, name) and name[0] != 'r')]
        print(f'subdirs: {subdirs}')
        return subdirs

    def produce_permutations(self, ids: List[int]) -> List[List[int]]:
        permutations: List[List[int]] = []

        print(f'ids {ids} num_cpus {self.main_config.num_cpus}')

        for sub_id in itertools.permutations(ids, self.main_config.num_cpus):
            print(f'Adding sub_id {sub_id}')
            permutations.append(list(sub_id))

        return permutations

    def execute(self):
        print('Starting GenerateRunSimulationsTask')

        id = 1
        ids = list(map(int, self.get_immediate_subdirectories(self.main_config.out_dir)))

        if not ids:
            print('no out directories detected, aborting')
            raise ValueError

        permutations = self.produce_permutations(ids)

        for sub_simulation in permutations:
            print(f'going to run simulation {sub_simulation} with id {id}')
            new_task = RunSingleSimulationTask(self.main_config, self.main_config.num_cpus, sub_simulation, id)
            self.q.put(new_task)
            id += 1

            if self.shm_quit.value:
                break

        print('GenerateRunSimulationsTask done')
