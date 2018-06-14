

var_1 = True

var_2 = var_3  # var_3 undefined

def function_1(var_4, *var_5, **var_6):
    return var_4 + var_5[var_7] + var_6.get(var_8)  # var_7 & var_8 undefined


def function_2(var_9):

    def closure(var_10):
        return var_1 + var_9 + var_10 + var_11()  # var 11 undefined

    return closure


class Class(var_12):  # var_12 undefined

    var_13 = var_2

    var_14 = var_1 + abs(var_9)  # var_9 undefined

    def __init__(self):
        super().__init__(var_15+var_13)  # var_13 & var_15 undefined
