from typing import List


class Task:
    name: str
    depends: str

    def __init__(self, name, depends=None):
        self.name = name
        self.depends = depends

    def __str__(self):
        return "Task {%s %s}" % (self.name, self.depends)


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
                tasks.append(Task(json_task['name'], depends))

            self.benchmarks.append(Benchmark(benchmark_name, tasks))

    def __str__(self):
        return "BenchmarkConfig {[%s]}" % ', '.join(map(str, self.benchmarks))
