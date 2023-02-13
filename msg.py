import json
from cal_msg import cal_msg
import re


class MSG:

    def __init__(self, group_id, infos, translations, translations_):
        self.id = group_id
        self.infos = infos
        self.translations = translations
        self.translations_ = translations_


class MSGInfo:

    def __init__(self, info):
        self.space_operator = info["space_operator"]
        self.msg_operator = info["msg_operator"]
        self.translation = info["translation"]

    def display(self):
        print("space operater:")
        print(self.space_operator)
        print("msg operator:")
        print(self.msg_operator)
        print("translation:")
        print(self.translation)

    def dic(self):
        return {"space_operator": self.space_operator,
                "msg_operator": self.msg_operator,
                "translation": self.translation}


with open("data/wyckoff_position.json", "r") as f:
    wp = json.load(f)
msg = []
msg_dicts = cal_msg()
for msg_dict in msg_dicts:
    g_infos = []
    for info in msg_dict["info"]:
        g_infos.append(MSGInfo(info))
    msg.append(MSG(msg_dict["id"], g_infos, translations=msg_dict["translation"], translations_=msg_dict["translation_"]))

