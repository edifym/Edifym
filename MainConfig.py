class MainConfig:
    m5_path: str = ""
    gem5_executable_path: str = ""
    gem5_se_script_path: str = ""
    library_name: str = ""
    num_cpus: int = 0
    num_workers: int = 0
    benchmark: str = ""
    show_command_output: bool = False

    def __init__(self, json_data):
        self.m5_path = json_data['m5_path']
        self.gem5_executable_path = json_data['gem5_executable_path']
        self.gem5_se_script_path = json_data['gem5_se_script_path']
        self.library_name = json_data['library_name']
        self.num_cpus = json_data['num_cpus']
        self.num_workers = json_data['num_workers']
        self.benchmark = json_data['benchmark']
        self.show_command_output = json_data['show_command_output']
