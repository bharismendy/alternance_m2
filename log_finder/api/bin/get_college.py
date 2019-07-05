import os
import json
from .setting import DATA_DIR, BASE_DIR

def get_list_code():
    return os.listdir(DATA_DIR)

def get_college_list():
    result = []
    with open(os.path.join(BASE_DIR,"college_nre.json")) as json_file:
        json_dic = json.load(json_file)
        for element in set(get_list_code()):
            for college in json_dic:
                if not element in json.loads(json.dumps(str(result))):
                    if college["Code"] == element:
                        result.append(college)
                    else:
                        result.append({"Nom":element, "Code":element})
    return result
