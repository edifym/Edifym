class MainConfig:
    gem5_path: str = ""
    library_name: str = ""

    def __init__(self, json_data):
        self.gem5_path = json_data['gem5_path']
        self.library_name = json_data['library_name']
