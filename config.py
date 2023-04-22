import os
import shutil
import json


class Config:
    def __init__(self):
        config_path = "/etc/enhancedocs"
        data_path = "/data/enhancedocs"
        config_file_name = "config.json"
        config_file_path = config_path + "/" + config_file_name
        os.makedirs(config_path, exist_ok=True)
        os.makedirs(data_path, exist_ok=True)
        if not os.path.exists(config_file_path):
            shutil.copyfile(config_file_name, config_file_path)
        with open(config_file_path, 'r') as f:
            config_json = json.load(f)
            self.docs_base_url = config_json["docs_base_url"]
            self.project_name = config_json["project_name"]
        with open("prompt_template.txt", 'r') as f:
            self.prompt_template = f.read()
        self.vector_index_file_path = data_path + "/vectorstore.index"
        self.vector_store_file_path = data_path + "/vectorstore.pkl"
