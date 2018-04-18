class MainConfig:
    gem5_path: str = ""

    def __init__(self, json_data):
        self.gem5_path = json_data['gem5_path']
