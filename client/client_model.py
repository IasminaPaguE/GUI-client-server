class ClientModel:
    def __init__(self):
        self.selected_path = None
        self.metrics = {}
        self.logs = []

    def set_selected_path(self, path):
        self.selected_path = path

    def add_metric(self, key, value):
        self.metrics[key] = value

    def add_log(self, message):
        self.logs.append(message)
