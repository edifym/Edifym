from typing import List
import itertools


class Value:
    name: str
    values: List[int]

    def __init__(self, name, values):
        self.name = name
        self.values = values

    def __str__(self):
        return "Value {%s %s}" % (self.name, self.values)

    def __repr__(self):
        return self.__str__()


class Task:
    name: str
    depends: str
    values: List[Value]

    def __init__(self, name, depends=None, values=None):
        if values is None:
            values = []

        self.name = name
        self.depends = depends
        self.values = values

    def __str__(self):
        return "Task {%s %s %s}" % (self.name, self.depends, self.values)

    def __repr__(self):
        return self.__str__()


class Benchmark:
    name: str
    tasks: List[Task]

    def __init__(self, name: str, tasks: List[Task]):
        self.name = name
        self.tasks = tasks

    def __str__(self):
        return "Benchmark {%s, [%s]}" % (self.name, ', '.join(map(str, self.tasks)))

    def __repr__(self):
        return self.__str__()


class BenchmarkConfig:
    benchmarks: List[Benchmark]

    def __init__(self, config_json):
        self.benchmarks = []
        for key in config_json.keys():
            benchmark_name = key
            tasks: List[Task] = []
            for json_task in config_json[key]["tasks"]:
                depends = None

                if 'depends' in json_task.keys():
                    depends = json_task['depends']

                if 'values' in json_task.keys():
                    json_values = json_task['values']
                    values: List[Value] = []

                    for val in json_values:
                        name = val['name']
                        range = val['values']
                        subvalues: List[int] = []

                        for r in range:
                            subvalues.append(r)

                        values.append(Value(name, subvalues))

                    tasks.append(Task(json_task['name'], depends, values))
                else:
                    tasks.append(Task(json_task['name'], depends))

            #print(f'json tasks: {tasks}')

            self.benchmarks.append(Benchmark(benchmark_name, tasks))

    def __str__(self):
        return "BenchmarkConfig {[%s]}" % ', '.join(map(str, self.benchmarks))

    def __repr__(self):
        return self.__str__()
