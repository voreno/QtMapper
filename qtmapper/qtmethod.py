#!/usr/local/bin/python3
#import method

'''
Class representing a class method

calls: these are other QtMethods (SLOTS) called in this method through @caller
emits: these are other QtMethods (SIGNALS) emitted in this method @emit

'''
class QtMethod:
    def __init__(self, method):
        self._method = method
        self._key = self.key()
        self.symbol = None
        self.symbolPropagationEnabled = False

        self.calls = {} # QtSlots that get CALLED in this method
        self.emits = {} # QtSignals that are EMITTED in this method
        self.connections = {} # QtConnections made in this method {QtConnection.key:QtConnection}
        self.disconnections = {} # QtConnections made in this method

        self.type = 'method'

    def addCall(self, call):
        self._addNode(call, self.calls)
        if self.symbol is not None and self.symbolPropagationEnabled:
            self.symbol.addCall(call)

    def addEmit(self, emit):
        self._addNode(emit, self.emits)
        if self.symbol is not None and self.symbolPropagationEnabled:
            self.symbol.addEmit(emit)

    def addConnection(self, connection):
        # this QtMethod made a connection
        self._addNode(connection, self.connections)
        if self.symbol is not None and self.symbolPropagationEnabled:
            # the connects{} in Symbol holds this QtMethod
            self.symbol.addConnection(self, isOther = False)

    def addDisconnection(self, disconnection):
        # this QtMethod made a disconnection
        self._addNode(disconnection, self.disconnections)
        if self.symbol is not None and self.symbolPropagationEnabled:
            # the disconnects{} in Symbol holds this QtMethod
            self.symbol.addDisconnection(self, isOther = False)

    def getSymbolConnections(self, symbol):
        connections = []
        for c in self.connections:
            conn = self.connections[c]
            if symbol.symbolName == conn.emitter._method.methodClass:
                connections.append(conn)
                continue
            if symbol.symbolName == conn.receiver._method.methodClass:
                connections.append(conn)
                continue
        return connections

    def getSymbolEmittedMethods(self, symbol):
        # returns all the QtMethods (belonging to symbol) that are called by this QtMethod
        emits = []
        if self.methodClass() == symbol.symbolName:
            # this QtMethod is a method of Symbol
            for e in self.emits:
                emits.append(self.emits[e])
        else:
            # this QtMethod is not a method of Symbol, but emits a QtSignal of Symbol
            for e in self.emits:
                signal = self.emits[e]
                if signal.methodClass == symbol.symbolName:
                    emits.append(signal)
        return emits

    def getSymbolCalledMethods(self, symbol):
        # returns all the QtMethods (belonging to symbol) that are called by this QtMethod
        calls = []
        if self.methodClass() == symbol.symbolName:
            # this QtMethod is a method of Symbol
            for c in self.calls:
                calls.append(self.calls[c])
        else:
            # this QtMethod is not a method of Symbol, but calls a QtSignal of Symbol
            for c in self.calls:
                calledMethod = self.calls[c]
                if calledMethod.methodClass == symbol.symbolName:
                    calls.append(calledMethod)
        return calls

    def getSymbolDisconnections(self, symbol):
        disconnections = []
        for c in self.disconnections:
            conn = self.disconnections[c]
            if symbol.symbolName == conn.emitter._method.methodClass:
                disconnections.append(conn)
                continue
            if symbol.symbolName == conn.receiver._method.methodClass:
                disconnections.append(conn)
                continue
        return disconnections

    def setSymbol(self, symbol):
        self.symbol = symbol

    def numEmitted(self):
        return len(self.emits)

    def numCalled(self):
        return len(self.calls)

    def __str__(self):
        return self._method.__str__()

    def method(self):
        return self._method.method

    def methodClass(self):
        return self._method.methodClass

    def htmlName(self):
        return self._method.key + '.html'

    def name(self):
        return self._method.name()

    def key(self):
        return self._method.key

    def _addNode(self, methodNode, nodeContainer):
        # nodeContainer is a {} of QtMethod sub-classes
        if(methodNode.key not in nodeContainer):
            nodeContainer[methodNode.key] = methodNode


class _TestQtMethodSubclass(QtMethod):
    def __init__(self, method):
        QtMethod.__init__(self, method)
        self.nodeContainer = {}

if __name__ == '__main__':
    import method
    m = method.Method('foo(int *)', 'Bar')
    m2 = method.Method('bar()', 'Foo')
    _testMethod = _TestQtMethodSubclass(m)
    _testMethod._addNode(m2, _testMethod.nodeContainer)

    for key in _testMethod.nodeContainer:
        print(key)  # Foo__bar
        print(_testMethod.nodeContainer[key]) # Foo::bar()
        print(_testMethod.method()) # Bar::foo(int *)
        print(_testMethod)# Bar::foo(int *)
