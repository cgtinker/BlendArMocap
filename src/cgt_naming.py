
from cgt_core.cgt_utils import cgt_json


j = cgt_json.JsonData("cgt_data/finger_data.json")
j.save("cgt_data/finger_data2.json")