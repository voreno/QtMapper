#!/usr/local/bin/python3
from qtmapper import utils

def methodStr(method):
    return method.methodClass + '::' + method.method

'''
Method represents a C++ class method: MethodClass::method(args)

method.key converts MethodClass::method(args) to a format without characters (see utils.cppSymbolEncoder)
'''
class Method:
    def __init__(self, method, methodClass):
        self.method = method
        self.methodClass = methodClass

        self.key = ''
        self._computeKey()

    def __str__(self):
        return methodStr(self)

    def name(self):
        return self.__str__()

    def _computeKey(self):
        self.key = utils.cppSymbolEncoder(methodStr(self))

if __name__ == '__main__':
    m = Method('foo(int *)', 'Bar')
    print(methodStr(m))
    print(utils.cppSymbolEncoder(methodStr(m)))
