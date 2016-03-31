
'''
Represents a full C++ class

If it is a Qt class, then header and source should stay None

Symbol contains:
- signals
- slots
- connections/disconnections made or received by others
- emits
- calls
'''
class Symbol:
    def __init__(self, symbolName):
        self.symbolName = symbolName
        self.key = symbolName.replace('::', '__')

        self.header = None
        self.source = None

        self.signals = {} # {QtMethod.key : QtMethod} representing a class signal
        self.slots = {} # {QtMethod.key : QtMethod} representing a class slot
        self.connections = {} # a connection made by this class between a QtSignal & QtSlot
        self.otherConnections = {} # a connection made by another class
        # connections = {QtMethod : {QtConnection.key : QtConnection}}
        self.disconnections = {} # same as above
        self.otherDisconnections = {} # same as above

        self.emits = {} # a QtMethod that emits something of this class
        self.calls = {} # a QtMethod that calls something of this class

        self.emitters = {} # QtMethod of this class that emits something
        self.callers = {} # QtMethod of this class that calls something

    def numConnections(self):
        return (len(self.connections) + len(self.otherConnections))

    def numDisconnections(self):
        return (len(self.disconnections) + len(self.otherDisconnections))

    def totalConnections(self):
        return (self.numConnections() + self.numDisconnections())

    def addSlot(self, slot):
        if slot._key not in self.slots:
            self.slots[slot._key] = slot

    def addSignal(self, signal):
        if signal._key not in self.signals:
            self.signals[signal._key] = signal

    def addCall(self, call):
        self._addNode(call, self.calls)

    def addEmit(self, emit):
        self._addNode(emit, self.emits)

    def addCaller(self, caller):
        self._addNode(caller, self.callers)

    def addEmitter(self, emitter):
        self._addNode(emitter, self.emitters)

    def addConnection(self, connection, isOther):
        if isOther:
            self._addNode(connection, self.otherConnections)
        else:
            self._addNode(connection, self.connections)

    def addDisconnection(self, disconnection, isOther):
        if isOther:
            self._addNode(disconnection, self.otherDisconnections)
        else:
            self._addNode(disconnection, self.disconnections)

    def _addNode(self, methodNode, nodeContainer):
        # nodeContainer is a { key : QtMethod } of QtMethod sub-classes
        if(methodNode.key not in nodeContainer):
            nodeContainer[methodNode.key] = methodNode

    def __str__(self):
        s = self.symbolName
        if(self.hasHeader()):
            s += '\n\t' + self.header.path
        if(self.hasSource()):
            s += '\n\t' + self.source.path
        if(len(self.signals)):
            s += '\n\t%s Signals' % str(len(self.signals))
            for x in self.signals:
                s += '\n\t\t' + self.signals[x].name()
        if(len(self.slots)):
            s += '\n\t%s Slots' % str(len(self.slots))
            for x in self.slots:
                s += '\n\t\t' + self.slots[x].name()
        if(len(self.connections)):
            s += '\n\t%s Connections' % str(len(self.connections))
            for x in self.connections:
                s += '\n\t\t' + self.connections[x].name()
        if(len(self.otherConnections)):
            s += '\n\t%s Other Connections' % str(len(self.otherConnections))
            for x in self.otherConnections:
                s += '\n\t\t' + self.otherConnections[x].name()
        if(len(self.disconnections)):
            s += '\n\t%s Disconnections' % str(len(self.disconnections))
            for x in self.disconnections:
                s += '\n\t\t' + self.disconnections[x].name()
        if(len(self.otherDisconnections)):
            s += '\n\t%s Other Disconnections' % str(len(self.otherDisconnections))
            for x in self.otherDisconnections:
                s += '\n\t\t' + self.otherDisconnections[x].name()
        if(len(self.emits)):
            s += '\n\t%s Emits' % str(len(self.emits))
            for x in self.emits:
                s += '\n\t\t' + self.emits[x].name()
        if(len(self.calls)):
            s += '\n\t%s Calls' % str(len(self.calls))
            for x in self.calls:
                s += '\n\t\t' + self.calls[x].name()
        if(len(self.emitters)):
            s += '\n\t%s Emitters' % str(len(self.emitters))
            for x in self.emitters:
                s += '\n\t\t' + self.emitters[x].name()
        if(len(self.callers)):
            s += '\n\t%s Callers' % str(len(self.callers))
            for x in self.callers:
                s += '\n\t\t' + self.callers[x].name()
        return s

    def htmlName(self):
        return self.key + '.html'

    def hasHeader(self):
        if self.header is None:
            return False
        return True

    def hasSource(self):
        if self.source is None:
            return False
        return True
