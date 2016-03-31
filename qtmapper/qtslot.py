#!/usr/local/bin/python3
from qtmapper import qtmethod

'''
Class representing a SLOT

triggers: these are QtMethods that trigger the slot (ie. SIGNALS) through @connect
callers: these are QtMethods that directly call the slot, through @caller
connectors: these are QtMethods that connect this slot to a signal @connect
disconnectors: these are QtMethods that disconnect this slot @disconnect

N.B: this class also has calls and emits
calls: other QtMethods (slots) called by this slot @caller
emits: other QtMethods (signals) emitted by this slot @emit
'''
class QtSlot(qtmethod.QtMethod):
    def __init__(self, method):
        qtmethod.QtMethod.__init__(self, method)

        self.triggers = {} # other QtMethods that TRIGGER this slot (emitted signals)
        self.callers = {} # other QtMethods that CALL this slot (not signals)
        self.connectors = {} # other QtMethods that CONNECT this slot to emitters
        self.disconnectors = {} # other QtMethods that DISCONNECT this slot from emitters

        self.type = 'slot'
        #self.calls = {} # QtSlots that get CALLED in this method
        #self.emits = {} # QtSignals that are EMITTED in this method
        #self.connections = {} # QtConnections made in this method
        #self.disconnections = {} # QtConnections made in this method

    def __str__(self):
        s = self._method.__str__()
        if len(self.triggers):
            s += '\n\t%s triggers' % len(self.triggers)
        if len(self.callers):
            s += '\n\t%s callers' % len(self.callers)
        if len(self.connectors):
            s += '\n\t%s connectors' % len(self.connectors)
        if len(self.disconnectors):
            s += '\n\t%s disconnectors' % len(self.disconnectors)
        if len(self.calls):
            s += '\n\t%s calls' % len(self.calls)
        if len(self.emits):
            s += '\n\t%s emits' % len(self.emits)
        if len(self.connections):
            s += '\n\t%s connects' % len(self.connections)
        if len(self.disconnections):
            s += '\n\t%s disconnects' % len(self.disconnections)
        return s

    #def addSymbol(self, symbol):
    #    self.symbol = symbol

    def addTrigger(self, trigger):
        self._addNode(trigger, self.triggers)

    def addCaller(self, caller):
        self._addNode(caller, self.callers)
        if(self.symbol is not None) and self.symbolPropagationEnabled:
            self.symbol.addCall(caller)

    def addConnector(self, connector):
        self._addNode(connector, self.connectors)

    def addDisconnector(self, disconnector):
        self._addNode(disconnector, self.disconnectors)

    def numTriggers(self):
        return len(self.triggers)

    def numCallers(self):
        return len(self.callers)

    def numConnectors(self):
        return len(self.connectors)

    def numDisconnectors(self):
        return len(self.disconnectors)


if __name__ == '__main__':
    import method
    m = method.Method('foo(int *)', 'Bar')
    e = method.Method('signalEmitterFn()', 'EmitterClass')
    r = method.Method('signalReceiverFn()', 'ReceiverClass')
    c = method.Method('signalConnectorFn()', 'ConnectorClass')
    d = method.Method('signalDisconnectorFn()', 'DisconnectorClass')
    e2 = method.Method('signalEmitterFn2(bool *)', 'EmitterClass')
    signal = QtSignal(m)
    signal.addEmitter(e)
    signal.addEmitter(e2)
    signal.addReceiver(r)
    signal.addReceiver(r)
    signal.addConnector(c)
    signal.addDisconnector(d)

    print('Num Emitters: %s' % signal.numEmitters())
    for key in signal.emitters:
        print(key + ': ' + str(signal.emitters[key]))
    print('Num Receivers: %s' % signal.numReceivers())
    print('Num Connectors: %s' % signal.numConnectors())
    print('Num Disconnectors: %s' % signal.numDisconnectors())
