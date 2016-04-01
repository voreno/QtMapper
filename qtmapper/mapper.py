#!/usr/local/bin/python3
import os

from qtmapper import sourceparser

from qtmapper import qtmethod
from qtmapper import qtsignal
from qtmapper import qtslot
from qtmapper import qtconnection

#from html import htmlwriter

from qtmapper import symbol as _sym_

class QtSignalSlotMapper:
    def __init__(self, sourcePath):
        self.rootPath = sourcePath
        self.parser = None
        self.pathValid = False

        self._checkPath()

        self.symbols = {}
        self.signals = {}
        self.slots = {}
        self.otherMethods = {}

        self.diagramPaths = []
    def run(self):
        if(self.pathValid == False):
            print('QtSignalSlotMapper error, path does not exist: ' + self.rootPath)
            return False

        self.parser = sourceparser.SourceParser(self.rootPath)
        self.parser.parse()
        self._processResults()

    def srcRootPath(self, srcPath):
        if self.rootPath in srcPath:
            return srcPath.split(self.rootPath)[1]
        return srcPath

    def _processResults(self):
        if self.parser is None:
            return False

        # *** create symbols ***
        for h in self.parser.headers:
            hdr = self.parser.headers[h]
            for hdrClass in hdr.headerClasses:
                #hdrClass is the className of a defined class in the header
                symbolKey = hdrClass.replace('::', '__')
                symbol = self._getSymbol(symbolKey)
                if symbol is None:
                    # create new symbol
                    symbol = _sym_.Symbol(hdrClass)
                    self.symbols[symbol.key] = symbol
                    symbol.header = hdr
                    srcPath = self.parser.getHeaderSourcePath(hdr.path)
                    if srcPath in self.parser.sources:
                        symbol.source = self.parser.sources[srcPath]
        for srcClass in self.parser.allClasses:
            if srcClass not in self.symbols:
                symbol = _sym_.Symbol(srcClass)
                self.symbols[symbol.key] = symbol

        # *** extract results from source files ***
        for s in self.parser.sources:
            src = self.parser.sources[s]
            # ***************************
            # *** process connections ***
            # ***************************
            for c in src._connects:
                for conn in src._connects[c]:
                    #conn = src._connects[c] # represented by a ConnectorParser object
                    #CP has emitter, receiver, connector

                    # get the symbol of the connector
                    symbol = self._createSymbol(conn.connector.methodClass)

                    # get the QtSignal of emitter
                    signal = self._getSignal(conn.emitter.key)
                    if signal is None:
                        # create signal
                        signal = qtsignal.QtSignal(conn.emitter)
                        self.signals[signal._key] = signal
                        #print(self.signals.keys())
                        # set the signal's symbol
                        signal.setSymbol(self._createSymbol(signal.methodClass()))
                        signal.symbol.addSignal(signal)

                    # get the QtSlot (or QtSignal) of receiver
                    receiver = None
                    if conn.receiverIsSignal:
                        receiver = self._getSignal(conn.receiver.key)
                    else:
                        receiver = self._getSlot(conn.receiver.key)
                    if receiver is None:
                        if(conn.receiverIsSignal):
                            receiver = qtsignal.QtSignal(conn.receiver)
                            self.signals[receiver._key] = receiver
                        else:
                            receiver = qtslot.QtSlot(conn.receiver)
                            self.slots[receiver._key] = receiver
                        # set the receiver's symbol
                        receiver.setSymbol(self._createSymbol(receiver.methodClass()))
                        if(conn.receiverIsSignal):
                            receiver.symbol.addSignal(receiver)
                        else:
                            receiver.symbol.addSlot(receiver)

                    connector = None
                    connectorIsSlot = False
                    if(conn.connector.key in self.parser.allSlots):
                        # determine if the connector is also a slot
                        connectorIsSlot = True
                        connector = self._getSlot(conn.connector.key)
                        if connector is None:
                            connector = qtslot.QtSlot(conn.connector)
                            self.slots[connector._key] = connector
                            # set the connector's symbol
                            connector.setSymbol(self._createSymbol(connector.methodClass()))
                            connector.symbol.addSlot(connector)
                    else:
                        # connector is just a QtMethod (not signal or slot)
                        connector = self._getOtherMethod(conn.connector.key)
                        if connector is None:
                            connector = qtmethod.QtMethod(conn.connector)
                            self.otherMethods[connector._key] = connector
                            # set the connector's symbol
                            connector.setSymbol(self._createSymbol(connector.methodClass()))
                            # don't add connector to symbol yet, this happens in connector.addconnection

                    # create the connection
                    qtConn = qtconnection.QtConnection(signal, receiver, conn.receiverIsSignal)

                    # link up data
                    connector.addConnection(qtConn) # try adding connection if not exists

                    signal.addConnector(connector) # @todo correct notification for symbol
                    signal.addReceiver(receiver)

                    receiver.addConnector(connector) # @todo correct notification for symbol
                    receiver.addTrigger(signal)

                    connector.symbol.addConnection(connector, isOther = False)

                    if signal.symbol.symbolName is not symbol.symbolName:
                        signal.symbol.addConnection(connector, isOther = True)

                    if receiver.symbol.symbolName is not symbol.symbolName:
                        receiver.symbol.addConnection(connector, isOther = True)
            # ******************************
            # *** process disconnections ***
            # ******************************
            for c in src._disconnects:
                for conn in src._disconnects[c]:
                    #conn = src._disconnects[c] # represented by a ConnectorParser object
                    #CP has emitter, receiver, connector

                    # get the symbol of the disconnector
                    symbol = self._createSymbol(conn.connector.methodClass)

                    # get the QtSignal of emitter
                    signal = self._getSignal(conn.emitter.key)
                    if signal is None:
                        # create signal
                        signal = qtsignal.QtSignal(conn.emitter)
                        self.signals[signal._key] = signal
                        # set the signal's symbol
                        signal.setSymbol(self._createSymbol(signal.methodClass()))
                        signal.symbol.addSignal(signal)

                    # get the QtSlot (or QtSignal) of receiver
                    receiver = None
                    if conn.receiverIsSignal:
                        receiver = self._getSignal(conn.receiver.key)
                    else:
                        receiver = self._getSlot(conn.receiver.key)
                    if receiver is None:
                        if(conn.receiverIsSignal):
                            receiver = qtsignal.QtSignal(conn.receiver)
                            self.signals[receiver._key] = receiver
                        else:
                            receiver = qtslot.QtSlot(conn.receiver)
                            self.slots[receiver._key] = receiver
                        # set the receiver's symbol
                        receiver.setSymbol(self._createSymbol(receiver.methodClass()))
                        if(conn.receiverIsSignal):
                            receiver.symbol.addSignal(receiver)
                        else:
                            receiver.symbol.addSlot(receiver)

                    connector = None
                    connectorIsSlot = False
                    if(conn.connector.key in self.parser.allSlots):
                        # determine if the connector is also a slot
                        connectorIsSlot = True
                        connector = self._getSlot(conn.connector.key)
                        if connector is None:
                            connector = qtslot.QtSlot(conn.connector)
                            self.slots[connector._key] = connector
                            # set the connector's symbol
                            connector.setSymbol(self._createSymbol(connector.methodClass()))
                            connector.symbol.addSlot(connector)
                    else:
                        # connector is just a QtMethod (not signal or slot)
                        connector = self._getOtherMethod(conn.connector.key)
                        if connector is None:
                            connector = qtmethod.QtMethod(conn.connector)
                            self.otherMethods[connector._key] = connector
                            # set the connector's symbol
                            connector.setSymbol(self._createSymbol(connector.methodClass()))

                    # create the connection
                    qtConn = qtconnection.QtConnection(signal, receiver, conn.receiverIsSignal)

                    # link up data
                    connector.addDisconnection(qtConn) # try adding connection if not exists
                    connector.symbol.addDisconnection(connector, isOther = False)

                    signal.addDisconnector(connector) # @todo correct notification for symbol
                    #signal.addReceiver(receiver)

                    receiver.addDisconnector(connector) # @todo correct notification for symbol
                    #receiver.addTrigger(signal)

                    if signal.symbol.symbolName is not symbol.symbolName:
                        signal.symbol.addDisconnection(connector, isOther = True)

                    if receiver.symbol.symbolName is not symbol.symbolName:
                        receiver.symbol.addDisconnection(connector, isOther = True)

            # *******************
            # *** parse emits ***
            # *******************
            for emitterKey in src._emits:
                for emitted in src._emits[emitterKey]:
                    # emitData: caller (QtMethod) calledMethod (QtMethod)
                    emitData = src._emits[emitterKey][emitted]

                    symbol = self._createSymbol(emitData.caller.methodClass)

                    signal = self._getSignal(emitData.calledMethod.key)
                    if signal is None:
                        # create signal
                        signal = qtsignal.QtSignal(emitData.calledMethod)
                        self.signals[signal._key] = signal
                        # set signal's symbol
                        signal.setSymbol(self._createSymbol(signal.methodClass()))
                        signal.symbol.addSignal(signal)

                    emitter = None
                    emitterIsSlot = False
                    if(emitData.caller.key in self.parser.allSlots):
                        emitterIsSlot = True
                        emitter = self._getSlot(emitData.caller.key)
                        if emitter is None:
                            # create slot
                            emitter = qtslot.QtSlot(emitData.caller)
                            self.slots[emitter._key] = emitter
                            # set the emitter's symbol
                            emitter.setSymbol(self._createSymbol(emitter.methodClass()))
                            emitter.symbol.addSlot(emitter)
                    else:
                        emitter = self._getOtherMethod(emitData.caller.key)
                        if emitter is None:
                            # create method
                            emitter = qtmethod.QtMethod(emitData.caller)
                            self.otherMethods[emitter._key] = emitter
                            # set the emitter's symbol
                            emitter.setSymbol(self._createSymbol(emitter.methodClass()))
                            #emitter.symbol.addEmitter(emitter)

                    emitter.addEmit(signal)
                    signal.addEmitter(emitter)

                    emitter.symbol.addEmitter(emitter)
                    signal.symbol.addEmit(emitter)

                    #if(signal.symbol.symbolName == emitter.symbol.symbolName):
                    #    emitter.symbol.addEmitter()

            # *******************
            # *** parse calls ***
            # *******************
            for callerKey in src._calls:
                for called in src._calls[callerKey]:
                    # emitData: caller (QtMethod) calledMethod (QtMethod)
                    callData = src._calls[callerKey][called]

                    symbol = self._createSymbol(callData.caller.methodClass)

                    slot = self._getSlot(callData.calledMethod.key)
                    if slot is None:
                        # create slot
                        slot = qtslot.QtSlot(callData.calledMethod)
                        self.slots[slot._key] = slot
                        # set slot's symbol
                        slot.setSymbol(self._createSymbol(slot.methodClass()))
                        slot.symbol.addSlot(slot)

                    caller = None
                    callerIsSlot = False
                    if(callData.caller.key in self.parser.allSlots):
                        callerIsSlot = True
                        caller = self._getSlot(callData.caller.key)
                        if caller is None:
                            # create slot
                            caller = qtslot.QtSlot(callData.caller)
                            self.slots[caller._key] = caller
                            # set the caller's symbol
                            caller.setSymbol(self._createSymbol(caller.methodClass()))
                            caller.symbol.addSlot(caller)
                    else:
                        caller = self._getOtherMethod(callData.caller.key)
                        if caller is None:
                            # create method
                            caller = qtmethod.QtMethod(callData.caller)
                            self.otherMethods[caller._key] = caller
                            # set the caller's symbol
                            caller.setSymbol(self._createSymbol(caller.methodClass()))
                            #caller.symbol.addCaller(caller)

                    caller.addCall(slot)
                    slot.addCaller(caller)

                    caller.symbol.addCaller(caller)
                    slot.symbol.addCall(caller)

    def _createSymbol(self, symbolName):
        if symbolName in self.symbols:
            return self.symbols[symbolName]
        else:
            s = _sym_.Symbol(symbolName)
            self.symbols[symbolName] = s
            return s

    def _getSymbol(self, key):
        if key in self.symbols:
            return self.symbols[key]
        return None

    def _getSignal(self, key):
        if key in self.signals:
            return self.signals[key]
        return None

    def _getSlot(self, key):
        if key in self.slots:
            return self.slots[key]
        return None

    def _getOtherMethod(self, key):
        if key in self.otherMethods:
            return self.otherMethods[key]
        return None


    def _checkPath(self):
        if(os.path.isdir(self.rootPath)):
            self.pathValid = True
        else:
            self.pathValid = False


if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    mapper = QtSignalSlotMapper('test_data/data_small')
    mapper.run()
    print(mapper.parser)

    for s in mapper.symbols:
        print(mapper.symbols[s])
        sym = mapper.symbols[s]
        for e in sym.emits:
            print(sym.emits[e].name())
