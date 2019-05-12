from typing import List
import itertools

class Value:
    name: str
    value: int

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return "Value {%s %s}" % (self.name, self.value)

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


class Benchmark:
    name: str
    tasks: List[Task]

    def __init__(self, name: str, tasks: List[Task]):
        self.name = name
        self.tasks = tasks

    def __str__(self):
        return "Benchmark {%s, [%s]}" % (self.name, ', '.join(map(str, self.tasks)))


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
                    values: List[List[Value]] = []

                    for val in json_values:
                        print(val)
                        name = val['name']
                        range = val['range']
                        subvalues: List[Value] = []

                        for r in range:
                            subvalues.append(Value(name, r))

                        values.append(subvalues)

                    for combination_value in itertools.product(*values):
                        print(combination_value)
                        tasks.append(Task(json_task['name'], depends, combination_value))
                else:
                    tasks.append(Task(json_task['name'], depends))

            self.benchmarks.append(Benchmark(benchmark_name, tasks))

    def __str__(self):
        return "BenchmarkConfig {[%s]}" % ', '.join(map(str, self.benchmarks))
