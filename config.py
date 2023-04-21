import os
import shutil
import json


class Config:
    def __init__(self):
        self.chroma_collection_name = "enhancedocs"
        config_path = "/etc/enhancedocs"
        self.data_path = "/data/enhancedocs"
        config_file_name = "config.json"
        prompt_template_file_name = "prompt_template.txt"
        config_file_path = config_path + "/" + config_file_name
        prompt_template_file_path = config_path + "/" + prompt_template_file_name
        os.makedirs(config_path, exist_ok=True)
        os.makedirs(self.data_path, exist_ok=True)
        if not os.path.exists(config_file_path):
            shutil.copyfile(config_file_name, config_file_path)
        if not os.path.exists(prompt_template_file_path):
            shutil.copyfile(prompt_template_file_name, prompt_template_file_path)
        with open(config_file_path, 'r') as f:
            config_json = json.load(f)
            self.docs_base_url = config_json["docs_base_url"]
        with open(prompt_template_file_path, 'r') as f:
            self.prompt_template = f.read()
        self.vector_index_file_path = self.data_path + "/vectorstore.index"
        self.vector_store_file_path = self.data_path + "/vectorstore.pkl"
