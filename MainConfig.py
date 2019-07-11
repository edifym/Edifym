class MainConfig:
    m5_path: str = ""
    gem5_executable_path: str = ""
    gem5_se_script_path: str = ""
    library_name: str = ""
    num_cpus: int = 0
    num_workers: int = 0
    benchmark: str = ""
    show_command_output: bool = False
    src_dir: str = ""
    build_dir: str = ""
    out_dir: str = ""
    stats_dir: str = ""

    def __init__(self, json_data):
        self.m5_path = json_data['m5_path']
        self.gem5_executable_path = json_data['gem5_executable_path']
        self.gem5_se_script_path = json_data['gem5_se_script_path']
        self.library_name = json_data['library_name']
        self.num_cpus = json_data['num_cpus']
        self.num_workers = json_data['num_workers']
        self.benchmark = json_data['benchmark']
        self.show_command_output = json_data['show_command_output']
        self.src_dir = json_data['src_dir']
        self.build_dir = json_data['build_dir']
        self.out_dir = json_data['out_dir']
        self.stats_dir = json_data['stats_dir']
