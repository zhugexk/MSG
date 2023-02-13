import sympy
import numpy as np
from msg import msg
import re
import pickle


def cal_zero_order_coefficients_from_msg_group(msg_group):
    coefficient = sympy.symarray("c", 3)
    for info in msg_group.infos:
        space_operator = info.space_operator
        fc = np.matmul(space_operator, coefficient) - coefficient
        sol = sympy.solve(fc.reshape(-1))
        if not sol:
            continue
        for i in range(3):
            coefficient[i] = coefficient[i].subs(sol)
    return coefficient


def cal_electric_polar_on_position(position):
    p = np.array([sympy.Symbol("px"), sympy.Symbol("py"), sympy.Symbol("pz")])
    for operation in position.operations:
        p_ = np.matmul(operation.space_operator, p)
        fc = p_ - p
        sol = sympy.solve(fc.reshape(-1))
        if not sol:
            continue
        for i in range(3):
            p[i] = p[i].subs(sol)
    return p


def cal_zero_order_coefficients():
    coefficients = []
    for group in msg:
        coefficient = cal_zero_order_coefficients_from_msg_group(group)
        coefficients.append(coefficient)
    return coefficients


class OperationOnPosition:
    def __init__(self, space_operator,
                 magent_operator, space_translation,
                 magnet_translation,
                 is_time_inverse):
        self.space_operator = space_operator
        self.magnet_operator = magent_operator
        self.space_translation = space_translation
        self.magnet_translation = magnet_translation
        self.is_time_inverse = is_time_inverse

    def display(self):
        print("space operater:")
        print(self.space_operator)
        print("msg operator:")
        print(self.magnet_operator)
        print("translation:")
        print(self.space_translation)


class PositionWithOperation:
    def __init__(self, dic):
        self.group_id = dic["group_id"]
        self.letter = dic["letter"]
        position = dic["position"]
        self.position = OperationOnPosition(position["space_operator"],
                                            position["msg_operator"],
                                            position["translation"],
                                            [0, 0, 0],
                                            False)
        self.operations = []
        for operation in dic["operations"]:
            operator = operation["operator"]
            if "translation" in operation.keys():
                self.operations.append(OperationOnPosition(
                    operator["space_operator"],
                    operator["msg_operator"],
                    operator["translation"],
                    operation["translation"],
                    False))
            elif "translation_" in operation.keys():
                self.operations.append(OperationOnPosition(
                    operator["space_operator"],
                    operator["msg_operator"],
                    operator["translation"],
                    operation["translation_"],
                    True))


def cal_first_order_coefficients():
    with open("data/operations_of_positions", 'rb') as f:
        positions = [PositionWithOperation(dic) for dic in pickle.load(f)]
    res = []
    group_id = positions[0].group_id
    print(group_id)
    for position in positions:
        if group_id != position.group_id:
            group_id = position.group_id
            print(position.group_id)
        res.append(cal_first_order_coefficient_from_position(position))
    return res


def cal_first_order_coefficient_from_position(position):
    coefficient = sympy.symarray("c", (3, 3))
    for operation in position.operations:
        p = np.matmul(coefficient, position.position.magnet_operator)
        p_ = np.matmul(operation.space_operator, p)
        fc = p - p_
        sol = sympy.solve(fc.reshape(-1))
        if not sol:
            continue
        for i in range(3):
            for j in range(3):
                coefficient[i][j] = coefficient[i][j].subs(sol)
    print(coefficient)
    return coefficient


def cal_and_save():
    zero_order = cal_zero_order_coefficients()
    np.save("data/magnetoelectric_coefficient/zero_order.npy", zero_order)
    first_order = cal_first_order_coefficients()
    np.save("data/magnetoelectric_coefficient/first_order.npy", first_order)


def cal_polar_space_group_id():
    c = np.load("data/magnetoelectric_coefficient/zero_order.npy", allow_pickle=True)
    res = []
    for i in range(1651):
        if np.all(c[i] == [0, 0, 0]):
            continue
        else:
            space_group_id = int(re.split(r"\.", msg[i].id)[0])
            if not res or res[-1] != space_group_id:
                res.append(space_group_id)
    return res


def print_zero_order_coefficients():
    c = np.load("data/magnetoelectric_coefficient/zero_order.npy", allow_pickle=True)
    msg_id = [g.id for g in msg]
    c_dict = dict(zip(msg_id, c))
    for key, value in c_dict.items():
        if not np.all(value == np.zeros_like(value)):
            print("id: " + key)
            print(value)


def print_first_order_coefficients():
    coefficients = np.load("data/magnetoelectric_coefficient/first_order.npy", allow_pickle=True)
    for c in coefficients:
        if not np.all(c == np.zeros_like(c)):
            print(c)


if __name__ == "__main__":
    # first_order = cal_first_order_coefficients()
    # np.save("data/magnetoelectric_coefficient/first_order.npy", first_order)
    # with open("data/operations_of_positions", 'rb') as f:
    #     positions = [PositionWithOperation(dic) for dic in pickle.load(f)]
    # for position in positions:
    #     print(cal_electric_polar_on_position(position))
    print_first_order_coefficients()