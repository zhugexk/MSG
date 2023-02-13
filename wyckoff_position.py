import json
import re
import pylab as p

from cal_msg import *
from msg import MSGInfo
from msg import msg
import numpy as np
import sympy
import pprint
import pickle


class WyckoffPositionGroup:

    def __init__(self, group_dict):
        self.id = group_dict["id"]

        self.translations = []
        self.translations_ = []
        for translation in group_dict["translation"]:
            if not re.findall(r"'", translation):
                coors = re.split(r',', translation[1:-1])
                self.translations.append([cal_translation_from_coordinate(coor) for coor in coors])
            else:
                coors = re.split(r',', translation[1:-2])
                self.translations_.append([cal_translation_from_coordinate(coor) for coor in coors])
        no_trans = [0, 0, 0]
        if not self.translations:
            self.translations.append(no_trans)

        self.position_groups = []
        for positions in group_dict["wyckoff_positions"]:
            position_group = {"letter": positions["letter"], "info": []}
            for position in positions["positions"]:
                coors = re.split(r"\|", position)[0][1:-1]
                spin = re.split(r"\|", position)[1][1:-1]
                coors = re.split(r",", coors)
                spin = re.split(r",", spin)
                space_operator, translation = cal_space_operator_and_translation_from_coordinates(coors)
                msg_operator = cal_msg_operator_from_spin(spin)
                msg_info = MSGInfo({
                    "space_operator": space_operator,
                    "translation": translation,
                    "msg_operator": msg_operator})
                position_group["info"].append(msg_info)
            self.position_groups.append(position_group)
        self.operations = self.position_groups[0]["info"]

    def display(self):
        print("id: " + self.id)
        print("------no time inverse translation------")
        for trans in self.translations:
            print(trans)
        print("------time inverse translation------")
        for trans_ in self.translations_:
            print(trans_)
        for position_group in self.position_groups:
            print("letter:" + position_group["letter"])
            for info in position_group["info"]:
                info.display()


def check_solve_of_translation(sol, t):
    if not isinstance(sol, dict):
        return False
    for axis in t:
        if axis not in sol.keys():
            return False
        elif not sol[axis].as_coeff_add()[1]:
            continue
        else:
            return False
    return True


def find_symmetry_operator_on_position(wyckoff_position, wpg):
    coor = np.array([sympy.Symbol("x"), sympy.Symbol("y"), sympy.Symbol("z")])
    spin = np.array([sympy.Symbol("mx"), sympy.Symbol("my"), sympy.Symbol("mz")])
    coor = np.matmul(wyckoff_position.space_operator, coor) + wyckoff_position.translation
    spin = np.matmul(wyckoff_position.msg_operator, spin)
    t = sympy.symarray('t', 3, integer=True)
    res = []
    for info in wpg.operations:
        spin_ = np.matmul(info.msg_operator, spin)
        if np.all(spin == spin_):
            for trans in wpg.translations:
                _coor = np.matmul(info.space_operator, coor) + info.translation + np.array(trans) + t
                fc = _coor - coor
                sol_fc = sympy.solve(fc.reshape(-1), list(t))
                if check_solve_of_translation(sol_fc, t):
                    res.append({"operator": info.dic(), "translation": trans})
        if np.all(spin == -spin_):
            for trans in wpg.translations_:
                _coor = np.matmul(info.space_operator, coor) + info.translation + np.array(trans) + t
                fc = _coor - coor
                sol_fc = sympy.solve(fc.reshape(-1), list(t))
                if check_solve_of_translation(sol_fc, t):
                    res.append({"operator": info.dic(), "translation_": trans})
        else:
            continue
    return res


def cal_symmetry_operations_of_positions():
    with open("data/wyckoff_position.json") as f:
        wp = json.load(f)
    wyckoff_position_groups = []
    for group in wp:
        wpg = WyckoffPositionGroup(group)
        wyckoff_position_groups.append(wpg)
    group_id_2_index = {}
    for index, wpg in enumerate(wyckoff_position_groups):
        group_id_2_index[wpg.id] = index
    res = []
    for wpg in wyckoff_position_groups:
        print(wpg.id)
        for position_group in wpg.position_groups:
            for position in position_group["info"]:
                res.append({"position": position.dic(),
                            "letter": position_group["letter"],
                            "group_id": wpg.id,
                            "operations": find_symmetry_operator_on_position(position, wpg)})
    return res


if __name__ == "__main__":
    operations = cal_symmetry_operations_of_positions()
    # with open("data/operations_of_positions.py", "w") as f:
    #     f.write(pprint.pformat(operations))
    with open("data/operations_of_positions", "wb") as f:
        pickle.dump(operations, f)
    # with open("data/operations_of_positions", "rb") as f:
    #     operations = pickle.load(f)
    # print(operations)
