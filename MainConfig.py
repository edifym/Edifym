class MainConfig:
    m5_path: str = ""
    library_name: str = ""

    def __init__(self, json_data):
        self.m5_path = json_data['m5_path']
        self.library_name = json_data['library_name']
