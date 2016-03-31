#!/usr/local/bin/python3

from qtmapper import qtmethod


'''
Class representing a SIGNAL

emitters: these are QtMethods that emit the signal through @emit
receivers: these are QtMethods that directly receive the signal, through @connect
connectors: these are QtMethods that connect this slot to a signal @connect
disconnectors: these are QtMethods that disconnect this slot @disconnect

N.B. this sub-class shouldn't use calls or emits

'''
class QtSignal(qtmethod.QtMethod):
    def __init__(self, method):
        qtmethod.QtMethod.__init__(self, method)

        self.triggers = {} # other QtMethods that EMIT this signal through a connection
        self.emitters = {} # other QtMethods that EMIT this signal
        self.receivers = {} # other QtMethods that RECEIVE this signal
        self.connectors = {} # other QtMethods that CONNECT this signal to receivers
        self.disconnectors = {} # other QtMethods that DISCONNECT this signal from receivers

        self.type = 'signal'

    def addTrigger(self, trigger):
        self._addNode(trigger, self.triggers)

    def addEmitter(self, emitter):
        self._addNode(emitter, self.emitters)
        if(self.symbol is not None) and self.symbolPropagationEnabled:
            self.symbol.addEmit(emitter)

    def addReceiver(self, receiver):
        self._addNode(receiver, self.receivers)

    def addConnector(self, connector):
        self._addNode(connector, self.connectors)
        '''
        if self.symbol is not None:
            if self.symbol.symbolName == connector.methodClass():
                # connector is of same class as this symbol
                self.symbol.addConnection(connector)
        '''

    def addDisconnector(self, disconnector):
        self._addNode(disconnector, self.disconnectors)

    def numEmitters(self):
        return len(self.emitters)

    def numReceivers(self):
        return len(self.receivers)

    def numConnectors(self):
        return len(self.connectors)

    def numDisconnectors(self):
        return len(self.disconnectors)



if __name__ == '__main__':
    import method
    m = method.Method('signalFoo(int *)', 'Bar')
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

    print(signal)

    print('Num Emitters: %s' % signal.numEmitters())
    for key in signal.emitters:
        print(key + ': ' + str(signal.emitters[key]))
    print('Num Receivers: %s' % signal.numReceivers())
    print('Num Connectors: %s' % signal.numConnectors())
    print('Num Disconnectors: %s' % signal.numDisconnectors())
