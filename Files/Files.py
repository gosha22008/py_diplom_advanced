import json


class WorkWithFiles:

    def write_file_json(self, loc_f_name, data):
        with open(loc_f_name, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, )

    def read_file_json(self, loc_f_name):
        with open(loc_f_name, encoding='utf-8') as f:
            data = json.load(f)
            return data

    def get_token(self):
        tokens = self.read_file_json('Files/tokens.json')
        return tokens


file = WorkWithFiles()