class QtConnection:
    def __init__(self, emitter, receiver, receiverIsSignal):
        self.emitter = emitter # QtSignal
        self.receiver = receiver # QtSlot or QtSignal

        self.receiverIsSignal = receiverIsSignal

        self.key = emitter.key() + '_' + receiver.key()


class QtConnector:
    # DEPRECATED...
    def __init__(self, connector, connection):
        self.connector = connector # QtMethod
        self.connection =  connection # QtConnection

        self.key = connector.key
