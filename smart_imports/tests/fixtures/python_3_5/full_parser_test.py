

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


var_16 = [var_17 for var_17 in range(10)]
var_18 = {var_19 for var_19 in range(10)}
var_20 = {var_21:var_22 for var_21 in zip(range(10), range(10, 20))}
var_23 = (var_24 for var_23 in range(10))


for var_25 in range(10):
    pass

    var_26 = var_27


var_28 = {var_29:[var_20[var_31] for var_31 in range(10)]
          for var_29 in range(10)}


class OtherClass:

    var_32 = 1

    def var_33(self, func):
        pass

    @var_33
    def method_1(self, var_34=var_32):
        pass


var_35 = lambda var_36, var_37=var_38: var_36+var_37+var_39
