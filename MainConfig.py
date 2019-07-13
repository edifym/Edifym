class MainConfig:
    gem5_executable_path: str = ""
    gem5_se_script_path: str = ""
    num_cpus: int = 0
    num_workers: int = 0
    benchmark: str = ""
    show_command_output: bool = False
    show_command_error: bool = True
    out_dir: str = ""
    stats_dir: str = ""
    executable: str = ""
    cpu_freq: str = ""

    def __init__(self, json_data):
        self.gem5_executable_path = json_data['gem5_executable_path']
        self.gem5_se_script_path = json_data['gem5_se_script_path']
        self.num_cpus = json_data['num_cpus']
        self.num_workers = json_data['num_workers']
        self.benchmark = json_data['benchmark']
        self.show_command_output = json_data['show_command_output']
        self.show_command_error = json_data['show_command_error']
        self.out_dir = json_data['out_dir']
        self.stats_dir = json_data['stats_dir']
        self.executable = json_data['executable']
        self.cpu_freq = json_data['cpu_freq']
