

var_1 = True

var_2 = var_3  # var_3 undefined


def function_1(var_4: annotation_1, *var_5, **var_6) -> annotation_2:
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


var_40 = [var_41 + var_42 + var_43
          for var_41, var_43 in var_35
          if var_43 and var_44]


{(var_45, var_46)
 for var_45 in {(var_46, var_47)
                for var_46 in var_48}}


try:
    var_49 = var_50
except var_51 as var_52:
    var_53(var_50, var_52, var_51, var_49)
    raise var_55


async def function_3():
    var_56 = 1

    def function_4():
        print(var_56)  # defined

    await var_49

    await var_57

    return function_4


# formatted string literals

var_58 = 'Fred'

f'He said his name is {var_58} and {var_59}.'

var_60 = 10

f'result: {var_58:{var_60}.{var_61}}'


# variable annotations

var_62: var_63[var_58] = var_65

var_66: var_67  # Note: no initial value!


class var_68:
    var_69: var_70(var_66, var_72) = {}


# asynchronous comprehensions

async def fuction_4():
    var_66 = [(var_73 + var_74+var_81) async for var_73, var_74 in var_75() if (var_76 + var_74) % 2]

    var_66 = [await var_77() for var_77, var_78 in var_79 if await var_80(var_78)]


# unicode

переменная_1 = перменная_2 + var_1


# assigment expressions

if (var_82 := var_83 + var_66) > var_84 + var_82:
    pass


# position only parameters

def var_85(var_86, var_87, /, var_89):
    return var_86 + var_87 + var_89


# f-string self-documenting expressions

f'{var_82=}, {var_90=}'


# extended decorator syntax
@var_91[var_62].value
def var_92():
    pass


# extended decorator syntax
@function_2[var_93].value
def var_94():
    pass


# context managers in parents
with (var_82.manager(),
      var_93.manager() as var_95,
      var_96(),
      var_97() as var_98):
    pass


# match expression
match var_99:
    case (0, 0):
        var_100 = var_99 + var_101
    case (0, var_102):
        var_100 = 0
    case (var_103, 0):
        var_100 = var_103 + 1
    case var_104:
        var_100 = var_104 + 1
    case (var_105, var_106):
        var_100 = var_105 + var_106
    case var_108(var_109=var_110, var_111=0):
        var_100 = var_110 + 1 + var_111
    case (var_112, var_113) if var_112 == var_113 and var_112 != var_114:
        var_100 = var_112 + var_113
    case (1, 2, *var_115):
        var_100 = var_115 + 0
    case {"a": var_116, 'b': var_117, 'c': var_94}:
        var_100 = var_116 + var_117 + var_94
    case {"a": var_116, **var_118}:
        var_100 = var_116 + var_118
    case (var_108(var_109=var_110), var_119(var_120=var_121) as var_122):
        var_100 = var_108 + var_110 + var_119 + var_121 + var_122
    case var_123.var_124:
        var_100 = var_123
    case {var_125.var_126: var_127}:
        var_100 = var_125 + var_127
    case _:
        var_100 = var_107
