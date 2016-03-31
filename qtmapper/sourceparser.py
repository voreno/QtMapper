#!/usr/local/bin/python3
import sys
import os
import CppHeaderParser

from qtmapper import method
from qtmapper import utils

class SourceFile:
    def __init__(self, path, fileName, isHeader):
        self.path = path
        self.fileName = fileName
        self.isHeader = isHeader

        self.headerClasses = [] # maps className::className
        self.classes = [] # stores all classNames
        #self.symbols = {} # maps symbolName : symbolName (same as self.classes)

        self._calls = {} # maps {CallerMethod.key : {CalledMethod.key: CallerParser}}
        self._emits = {} # maps {CallerMethod.key : {CalledMethod.key: CallerParser}}
        self._connects = {} # maps Method.key : ConnectorParser
        self._disconnects = {} # maps Method.key : ConnectorParser

    def populateSymbols(self):
        # *** CONNECTS ***
        for key in self._connects:
            for parser in self._connects[key]:
                if parser.emitter.methodClass not in self.classes:
                    self.classes.append(parser.emitter.methodClass)
                if parser.receiver.methodClass not in self.classes:
                    self.classes.append(parser.receiver.methodClass)
                if parser.connector.methodClass not in self.classes:
                    self.classes.append(parser.connector.methodClass)
                '''
                if parser.emitter.key not in self.signals:
                    self.signals.append(parser.emitter.key)
                if parser.receiverIsSignal:
                    if parser.receiver.key not in self.signals:
                        self.signals.append(parser.receiver.key)
                else:
                    if parser.receiver.key not in self.slots:
                        self.slots.append(parser.receiver.key)
                '''
        # *** DISCONNECTS ***
        for key in self._disconnects:
            for parser in self._disconnects[key]:
                if parser.emitter.methodClass not in self.classes:
                    self.classes.append(parser.emitter.methodClass)
                if parser.receiver.methodClass not in self.classes:
                    self.classes.append(parser.receiver.methodClass)
                if parser.connector.methodClass not in self.classes:
                    self.classes.append(parser.connector.methodClass)
        # *** CALLERS ***
        for callerKey in self._calls:
            for calledKey in self._calls[callerKey]:
                parser = self._calls[callerKey][calledKey]
                if parser.caller.methodClass not in self.classes:
                    self.classes.append(parser.caller.methodClass)
                if parser.calledMethod.methodClass not in self.classes:
                    self.classes.append(parser.calledMethod.methodClass)
        # *** EMITTERS ***
        for callerKey in self._emits:
            for calledKey in self._emits[callerKey]:
                parser = self._emits[callerKey][calledKey]
                if parser.caller.methodClass not in self.classes:
                    self.classes.append(parser.caller.methodClass)
                if parser.calledMethod.methodClass not in self.classes:
                    self.classes.append(parser.calledMethod.methodClass)

    def numConnects(self):
        n = 0
        for key in self._connects:
            n += len(self._connects[key])
        return n

    def numDisconnects(self):
        n = 0
        for key in self._disconnects:
            n += len(self._disconnects[key])
        return n

    def numCalls(self):
        n = 0
        for key in self._calls:
            n += len(self._calls[key])
        return n

    def numEmits(self):
        n = 0
        for key in self._emits:
            n += len(self._emits[key])
        return n

class CallerParser:
    def __init__(self, descriptor):
        self.descriptor = descriptor

        self.caller = None # the QtMethod that calls this method
        self.calledMethod = None # the QtMethod that gets called or emitted

        self.parserError = 0
        self.parserErrorMessage = ''

        # 1: @caller/@emit missing
        # 2: *** number error
        # 3: called :: error
    def parse(self):
        if ('@caller' not in self.descriptor) and ('@emit' not in self.descriptor):
            self.parserError = 1
            self.parserErrorMessage = 'Error @caller/@emit missing'
            return False

        # syntax: //@caller***SlotClass::Slot***CallerClass::CallerMethod
        # syntax: //@emit***ClassOfSingal::signal(…)***ClassEmitting::FunctionEmitting
        parts = self.descriptor.split('***')
        if(len(parts) == 3):
            calledMethod = parts[1]
            caller = parts[2]

            calledBits = calledMethod.split('::')
            if(len(calledBits) == 2):
                self.calledMethod = method.Method(calledBits[1], calledBits[0])
            else:
                self.parserError = 3
                self.parserErrorMessage = 'Error not enough :: found'
                return False
            callerBits = caller.split('::')
            if(len(callerBits) == 2):
                self.caller = method.Method(callerBits[1], callerBits[0])
            else:
                self.parserError = 3
                self.parserErrorMessage = 'Error not enough :: found'
                return False
        else:
            self.parserError = 2
            self.parserErrorMessage = 'Error not enough *** found'
            return False
        return True

class ConnectorParser:
    def __init__(self, line, descriptor):
        self.line = line
        self.descriptor = descriptor

        self.emitter = None
        self.receiver = None
        self.connector = None

        self.receiverIsSignal = False

        self.parserError = 0
        self.parserErrorMessage = ''
        # 0: no error;
        # 1: descriptor wrong len();
        # 2: class::method error in connector (wrong length)
        # 3: class::method error no :: separator
        # 4: no emitter
        # 5: no receiver
        #self.parse()

    def __str__(self):
        if self.parserError:
            return self.parserErrorMessage
        else:
            s = self.emitter.__str__() + '\n'
            s += self.receiver.__str__() + '\n'
            s += self.connector.__str__()
            return s

    def parse(self):
        descriptionParts = self.descriptor.split('***')
        emitterClass = ''
        receiverClass = ''
        # *** PARSE DESCRIPTOR LINE ***
        if(len(descriptionParts) == 4):
            # we are expecting the descriptor to contain the following structure:
            # @descriptor***SignalClass***SlotClass***ConnectingClass::ConnectingMethod(... args ...)
            # @descriptor can be @connect or @disconnect, doesn't matter
            emitterClass = descriptionParts[1]
            receiverClass = descriptionParts[2]
            connector = descriptionParts[3]

            connParts = connector.split('::')
            if len(connParts) == 2:
                self.connector = method.Method(connParts[1], connParts[0])
            else:
                if '::' not in connector:
                    self.parserError = 3
                    self.parserErrorMessage = 'No :: in ConnectingClass::ConnectingMethod(..args...)'
                    return False
                else:
                    self.parserError = 2
                    self.parserErrorMessage = 'Too many :: in ConnectingClass::ConnectingMethod(..args...)'
                    return False
        else:
            self.parserError = 1
            self.parserErrorMessage = 'Wrong number of *** in connector description'
            return False

        # *** PARSE CONNECTION LINE ***
        emitter = utils.substrBetween(self.line, 'SIGNAL(', '),')
        if(len(emitter) == 0):
            self.parserError = 4
            self.parserErrorMessage = 'No emitter SIGNAL found'
            return False

        receiver = utils.rSubstrBetween(self.line, 'SLOT(', '));')
        if(len(receiver) == 0):
            receiver = utils.rSubstrBetween(self.line, 'SIGNAL(', '));')
            if(len(receiver) == 0):
                self.parserError = 5
                self.parserErrorMessage = 'No receiver SIGNAL or SLOT found'
                return False
            else:
                self.receiverIsSignal = True
        # ASSERT: if we got here, we parsed everything successfully
        self.emitter = method.Method(emitter, emitterClass)
        self.receiver = method.Method(receiver, receiverClass)
        return True

class SourceParser:
    def __init__(self, rootSourcePath):
        self.rootSourcePath = rootSourcePath

        self.headers = {}
        self.sources = {}

        self.allHeaderClasses = []
        self.allClasses = []

        self.allSignals = []
        self.allSlots = []
        self.allOtherMethods = []

        self._debugMode = False
        self._headerMethods = {} # dictionary of all methods that were found in the headers

        self._connectFinds = ['connect(', '->connect(']
        self._disconnectFinds = ['disconnect(', '->disconnect(']

    def __str__(self):
        s = 'Parser for: ' + self.rootSourcePath + '\n'
        s += '%s Total Files: %s headers, %s sources' % (self.numFiles(), self.numHeaders(), self.numSources()) + '\n'
        s += '%s Total @connect statements found' % self.numConnects() + '\n'
        s += '%s Total @disconnect statements found' % self.numDisconnects() + '\n'
        s += '%s Total @caller statements found' % self.numCalls() + '\n'
        s += '%s Total @emit statements found' % self.numEmits() + '\n'
        s += '%s Classes: %s defined in headers, %s used in sources' % (len(self.allClasses), len(self.allHeaderClasses), (len(self.allClasses) - len(self.allHeaderClasses)))
        return s

    def getHeaderSourcePath(self, hdrPath):
        srcPath = ''
        if('.hpp' in hdrPath):
            srcPath = hdrPath.replace('.hpp', '.cpp')
        elif('.h' in hdrPath):
            srcPath = hdrPath.replace('.h', '.cpp')
        else:
            return ''
        if(len(srcPath) > 0):
            if(os.path.isfile(srcPath) == False):
                srcPath = srcPath.replace('.hpp', '.cc')
                if(os.path.isfile(srcPath)):
                    if srcPath in self.sources:
                        return srcPath
            else:
                if srcPath in self.sources:
                    return srcPath
        return ''

    def getSourceHeaderPath(self, srcPath):
        hdrPath = ''
        if('.cpp' in srcPath):
            hdrPath = srcPath.replace('.cpp', '.h')
        elif('.cc' in srcPath):
            hdrPath = srcPath.replace('.cc', '.h')
        else:
            return ''
        if(len(hdrPath) > 0):
            if(os.path.isfile(hdrPath) == False):
                hdrPath = hdrPath.replace('.h', '.hpp')
                if(os.path.isfile(hdrPath)):
                    if hdrPath in self.headers:
                        return hdrPath
            else:
                if hdrPath in self.headers:
                    return hdrPath
        return ''

    def parse(self):
        self._parseFolders()
        self._prepareParsedResults()

    def numHeaders(self):
        return len(self.headers)

    def numSources(self):
        return len(self.sources)

    def numFiles(self):
        return self.numHeaders() + self.numSources()

    def numConnects(self):
        n = 0
        for s in self.sources:
            n += self.sources[s].numConnects()
        return n

    def numDisconnects(self):
        n = 0
        for s in self.sources:
            n += self.sources[s].numDisconnects()
        return n

    def numCalls(self):
        n = 0
        for s in self.sources:
            n += self.sources[s].numCalls()
        return n

    def numEmits(self):
        n = 0
        for s in self.sources:
            n += self.sources[s].numEmits()
        return n

    def _parseFolders(self):
        if(self._debugMode):
            print('Parsing: ' + self.rootSourcePath)
        for folder, subs, files in os.walk(self.rootSourcePath):
            for fileName in files:
                extension = os.path.splitext(fileName)[1]
                filePath = os.path.join(folder, fileName)
                if(extension == '.h' or extension == '.hpp'):
                    header = SourceFile(filePath, fileName, True)
                    self._parseHeaderFile(header)
                    self.headers[filePath] = header
                if(extension == '.cc' or extension == '.cpp'):
                    source = SourceFile(filePath, fileName, False)
                    self._parseSourceFile(source)
                    self.sources[filePath] = source

    def _parseHeaderFile(self, header):
        hDebugMode = False
        if(self._debugMode):
            print('Parsing HEADER: ' + header.path)
            hDebugMode = False

        try:
            cppHeader = CppHeaderParser.CppHeader(header.path)
            for className in cppHeader.classes:
                header.classes.append(className)
                header.headerClasses.append(className)
                # get the class from the header
                # if we want to parse the methods of the class
                headerClass = cppHeader.classes[className]
                for method in headerClass['methods']['public']:
                    if(self._parseCppHeaderClassMethod(method) >= 0):
                        # method is slot or signal
                        self._addCppHeaderMethod(method['name'])
                        if(hDebugMode):
                            print(method['name'])
                for method in headerClass['methods']['protected']:
                    if(self._parseCppHeaderClassMethod(method) >= 0):
                        # method is slot or signal
                        self._addCppHeaderMethod(method['name'])
                        if(hDebugMode):
                            print(method['name'])
                for method in headerClass['methods']['private']:
                    if(self._parseCppHeaderClassMethod(method) >= 0):
                        # method is slot or signal
                        self._addCppHeaderMethod(method['name'])
                        if(hDebugMode):
                            print(method['name'])
        except CppHeaderParser.CppParseError as e:
            print(e)

    def _parseSourceFile(self, source):
        # source is a .cc or .cpp SourceFile
        if(self._debugMode):
            print('Parsing SOURCE: ' + source.path)
        if(os.path.isfile(source.path) and source.isHeader == False):
            # source file was detected
            opened = False
            with (open(source.path)) as sourceFile:
                # source file opened
                opened = True
                lineNum = 0
                previousLine = ''
                for line in sourceFile:
                    lineNum += 1 # sets the lineNum to line's number
                    line = line.lstrip(' ') # remove all white space at the start of line
                    line = line.replace('\r', '').replace('\n', '')
                    if(line.startswith('//')):
                        # we have a comment, or a line that contains a @action
                        previousLine = line
                        continue
                    # Assert: this line is not a comment (NB We don't capture /* ... */ situations)
                    # *** DISCONNECT *** parsing
                    matchFound = False
                    for disconnectStr in self._disconnectFinds:
                        if disconnectStr in line:
                            if '@disconnect' in previousLine:
                                parser = ConnectorParser(line, previousLine)
                                parser.parse()
                                if parser.parserError == 0:
                                    # no error
                                    if parser.connector.key in source._disconnects:
                                        source._disconnects[parser.connector.key].append(parser)
                                    else:
                                        source._disconnects[parser.connector.key] = [parser]
                                else:
                                    print('SourceParser error parsing disconnect: ' + parser.parserErrorMessage)
                                    print('\t at line %s in file %s' % (lineNum, source.path))
                            else:
                                if '@connect' in previousLine:
                                    print('SourceParser error: found @connect instead of @disconnect at line %s in file %s' % (lineNum - 1, source.path))
                                else:
                                    print('SourceParser error: missing @disconnect at line %s in file %s' % (lineNum, source.path))
                            matchFound = True
                            break
                    if matchFound:
                        previousLine = line
                        continue
                    # *** CONNECT *** parsing
                    matchFound = False
                    for connectStr in self._connectFinds:
                        if connectStr in line:
                            if '@connect' in previousLine:
                                parser = ConnectorParser(line, previousLine)
                                parser.parse()
                                if parser.parserError == 0:
                                    # no error
                                    if parser.connector.key in source._connects:
                                        source._connects[parser.connector.key].append(parser)
                                    else:
                                        source._connects[parser.connector.key] = [parser]
                                else:
                                    print('SourceParser error parsing connect: ' + parser.parserErrorMessage)
                                    print('\t at line %s in file %s' % (lineNum, source.path))
                            else:
                                if '@disconnect' in previousLine:
                                    print('SourceParser error: found @disconnect instead of @connect at line %s in file %s' % (lineNum - 1, source.path))
                                else:
                                    print('SourceParser error: missing @connect at line %s in file %s' % (lineNum, source.path))
                            matchFound = True
                            break
                    # *** CALLER *** parsing
                    matchFound = False
                    if '@caller' in previousLine:
                        parser = CallerParser(previousLine)
                        parser.parse()
                        if(parser.parserError == 0):
                            # no error
                            callerKey = parser.caller.key
                            calledKey = parser.calledMethod.key
                            if callerKey in source._calls:
                                if calledKey not in source._calls[callerKey]:
                                    source._calls[callerKey][calledKey] = parser
                                else:
                                    # callerMethod already called calledMethod once
                                    pass
                            else:
                                d = {}
                                d[calledKey] = parser
                                source._calls[callerKey] = d
                        else:
                            print('SourceParser error parsing @caller: ' + parser.parserErrorMessage)
                            print('\t at line %s in file %s' % (lineNum, source.path))
                    # *** EMIT *** parsing
                    if '@emit' in previousLine:
                        if 'emit' in line:
                            parser = CallerParser(previousLine)
                            parser.parse()
                            if(parser.parserError == 0):
                                # no error
                                callerKey = parser.caller.key
                                calledKey = parser.calledMethod.key
                                if callerKey in source._emits:
                                    if calledKey not in source._emits[callerKey]:
                                        source._emits[callerKey][calledKey] = parser
                                    else:
                                        # callerMethod already called calledMethod once
                                        pass
                                else:
                                    d = {}
                                    d[calledKey] = parser
                                    source._emits[callerKey] = d
                            else:
                                print('SourceParser error parsing @emit: ' + parser.parserErrorMessage)
                                print('\t at line %s in file %s' % (lineNum, source.path))
                        else:
                            print('SourceParser error: found @emit but no emit at line %s in file %s' % (lineNum - 1, source.path))
                    previousLine = line
            if(opened == False):
                print("SourceParser error: could not open file @ " + source.path)
        else:
            if(source.isHeader):
                print("SourceParser error: trying to parse a header file as source file")
            if(os.path.isfile(source.path) == False):
                print("SourceParser error: file not found @ " + source.path)

    def _parseCppHeaderClassMethod(self, cppHeaderMethod):
        if 'name' in cppHeaderMethod:
            name = cppHeaderMethod['name']
            if 'signal' in name:
                return 0
            if 'slot' in name:
                return 1
        return -1

    def _addCppHeaderMethod(self, cppHeaderMethodName):
        # adds the methodname to the list, it must be a slot or signal
        if cppHeaderMethodName not in self._headerMethods:
            self._headerMethods[cppHeaderMethodName] = True

    def _prepareParsedResults(self):
        for h in self.headers:
            hdr = self.headers[h]
            for hc in hdr.classes:
                if hc not in self.allHeaderClasses:
                    self.allHeaderClasses.append(hc)
        for c in self.sources:
            src = self.sources[c]
            src.populateSymbols()
            for sc in src.classes:
                if sc not in self.allClasses:
                    self.allClasses.append(sc)

            # get unique signals, slots first
            for key in src._connects:
                for parser in src._connects[key]:
                    # signal
                    if parser.emitter.key not in self.allSignals:
                        self.allSignals.append(parser.emitter.key)
                    # slot
                    if parser.receiverIsSignal:
                        if parser.receiver.key not in self.allSignals:
                            self.allSignals.append(parser.receiver.key)
                    else:
                        if parser.receiver.key not in self.allSlots:
                            self.allSlots.append(parser.receiver.key)
            for key in src._disconnects:
                for parser in src._disconnects[key]:
                    # signal
                    if parser.emitter.key not in self.allSignals:
                        self.allSignals.append(parser.emitter.key)
                    # slot
                    if parser.receiverIsSignal:
                        if parser.receiver.key not in self.allSignals:
                            self.allSignals.append(parser.receiver.key)
                    else:
                        if parser.receiver.key not in self.allSlots:
                            self.allSlots.append(parser.receiver.key)
            # called slot
            for caller in src._calls:
                for called in src._calls[caller]:
                    parser = src._calls[caller][called]
                    if parser.calledMethod.key not in self.allSlots:
                        self.allSlots.append(parser.calledMethod.key)
            # emitted signal
            for caller in src._emits:
                for called in src._emits[caller]:
                    parser = src._emits[caller][called]
                    if parser.calledMethod.key not in self.allSignals:
                        self.allSignals.append(parser.calledMethod.key)

            # now that we have mapped all the signals and slots, map the methods that perform actions
            for key in src._connects:
                for parser in src._connects[key]:
                    # connector
                    if parser.connector.key not in self.allSignals and parser.connector.key not in self.allSlots:
                        if parser.connector.key not in self.allOtherMethods:
                            self.allOtherMethods.append(parser.connector.key)
            for key in src._disconnects:
                for parser in src._disconnects[key]:
                    # connector
                    if parser.connector.key not in self.allSignals and parser.connector.key not in self.allSlots:
                        if parser.connector.key not in self.allOtherMethods:
                            self.allOtherMethods.append(parser.connector.key)
            # called slot
            for caller in src._calls:
                for called in src._calls[caller]:
                    parser = src._calls[caller][called]
                    if parser.caller.key not in self.allSlots and parser.caller.key not in self.allSignals:
                        if parser.caller.key not in self.allOtherMethods:
                            self.allOtherMethods.append(parser.caller.key)
                    continue
            # emitted signal
            for caller in src._emits:
                for called in src._emits[caller]:
                    parser = src._emits[caller][called]
                    if parser.caller.key not in self.allSlots and parser.caller.key not in self.allSignals:
                        if parser.caller.key not in self.allOtherMethods:
                            self.allOtherMethods.append(parser.caller.key)
                    continue
if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    rootFolder = 'test_data/'
    parser = SourceParser(rootFolder)
    parser.parse()
    print(parser)
