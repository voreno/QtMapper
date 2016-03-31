import os
from shutil import copyfile

from qtmapper.html import htmlpage
from qtmapper.html import htmltable

from qtmapper.html import dotgraph

class HtmlWriter:
    def __init__(self, mapper, writePath):
        self.mapper = mapper # QtSignalMapper

        self.cssPath = os.path.join(os.path.dirname(__file__), 'css/main.css')

        self.rootFolder = writePath
        self.pathValid = False
        self._checkPath()

    def write(self):
        if(self.pathValid == False):
            print('Wrong output path: ' + self.rootFolder)
            return False
        self.createCSS()
        self.createIndexPage()
        self.createClassPages()
        self.createSignalPages()
        self.createSlotPages()
        self.createOtherPages()

    def createIndexPage(self):
        page = htmlpage.HtmlPage(self.rootFolder, 'index.html', 'Index', cssRelPath='')
        self._setPageNavigation(page, relpath = '')

        numHdr = len(self.mapper.parser.headers)
        numSrc = len(self.mapper.parser.sources)
        numFiles = numHdr + numSrc
        numSymbols = str(len(self.mapper.symbols))

        htmlNumbers = page.p(page.b(str(numHdr)) + ' Header Files') + '\n'
        htmlNumbers += page.p(page.b(str(numSrc)) + ' Source Files') + '\n'
        htmlNumbers += page.p(page.b(str(numFiles)) + ' Total Files') + '\n'
        htmlNumbers += page.p(page.b(numSymbols) + ' Symbols') + '\n'

        page.addContent(htmlNumbers)
        page.write()

    def createClassPages(self):
        page = htmlpage.HtmlPage(self.rootFolder, 'classes.html', 'Classes', cssRelPath='')
        self._setPageNavigation(page, relpath = '')

        numClasses = len(self.mapper.symbols)
        numSignals = len(self.mapper.signals)
        numSlots = len(self.mapper.slots)

        hdr = ['Symbol', 'Symbol Signals', 'Symbol Slots']
        align = [False, True, True]
        table = htmltable.HtmlTable(3, hdr, align)

        tr = []
        tr.append('<b>%s</b> Symbol%s' % (numClasses, ('' if numClasses == 1 else 's')))
        tr.append('<b>%s</b> Signal%s' % (numSignals, ('' if numSignals == 1 else 's')))
        tr.append('<b>%s</b> Slot%s' % (numSlots, ('' if numSlots == 1 else 's')))
        #tr.append('<b>%s</b> Connection%s' % (numConn, ('' if numConn == 1 else 's')))
        #tr.append('<b>%s</b> Disconnection%s' % (numDisConn, ('' if numDisConn == 1 else 's')))
        table.append(tr)

        sortedSymbols = sorted(self.mapper.symbols.keys())
        for key in sortedSymbols:
            symbol = self.mapper.symbols[key]

            tr = []
            tr.append(page.classLink(symbol.symbolName,'', 'classes/'))
            tr.append(str(len(symbol.signals)) + ' sig')
            tr.append(str(len(symbol.slots)) + ' slt')
            #tr.append(str(symbol.totalConnection()) + ' conn')
            #tr.append(str(symbol.totalDisconnection()) + ' disconn')
            table.append(tr)

            self._createClassPage(symbol)

        page.addContent(table.html())
        page.write()

    def createSignalPages(self):
        page = htmlpage.HtmlPage(self.rootFolder, 'signals.html', 'Signals', cssRelPath='')
        self._setPageNavigation(page, relpath = '')

        hdr = ['Signal', 'Triggers', 'Receivers', 'Connectors', 'Disconnectors', 'Emitters']
        align = [False, True, True, True, True, True]

        table = htmltable.HtmlTable(6, hdr, align)

        sort = sorted(self.mapper.signals.keys())
        for key in sort:
            signal = self.mapper.signals[key]

            tr = []
            m = page.link(signal.htmlName(), signal.method(), relpath='methods/')
            c = page.classLink(signal.symbol.symbolName, '', relpath='classes/')
            tr.append(c + '::' + m)
            tr.append(str(len(signal.triggers)) + ' trg')
            tr.append(str(len(signal.receivers)) + ' rcv')
            tr.append(str(len(signal.connectors)) + ' conn')
            tr.append(str(len(signal.disconnectors)) + ' dconn')
            tr.append(str(len(signal.emitters)) + ' emit')
            table.append(tr)

            self._createSignalPage(signal)

        page.addContent(table.html())
        page.write()

    def createSlotPages(self):
        page = htmlpage.HtmlPage(self.rootFolder, 'slots.html', 'Slots', cssRelPath='')
        self._setPageNavigation(page, relpath = '')

        hdr = ['Slot', 'Triggers', 'Connectors', 'Disconnectors', 'Callers', 'Calls', 'Emits', 'Connects', 'Disconnects']
        align = [False, True, True, True, True, True, True, True, True]

        table = htmltable.HtmlTable(len(hdr), hdr, align)

        sort = sorted(self.mapper.slots.keys())
        for key in sort:
            slot = self.mapper.slots[key]

            tr = []
            m = page.link(slot.htmlName(), slot.method(), relpath='methods/')
            c = page.classLink(slot.symbol.symbolName, '', relpath='classes/')
            tr.append(c + '::' + m)
            tr.append(str(len(slot.triggers)) + ' trg')
            tr.append(str(len(slot.connectors)) + ' conn')
            tr.append(str(len(slot.disconnectors)) + ' dconn')
            tr.append(str(len(slot.callers)) + ' called')
            tr.append(str(len(slot.calls)) + ' calls')
            tr.append(str(len(slot.emits)) + ' emits')
            tr.append(str(len(slot.connections)) + ' conn')
            tr.append(str(len(slot.disconnections)) + ' dconn')

            table.append(tr)

            self._createSlotPage(slot)

        page.addContent(table.html())
        page.write()

    def createOtherPages(self):
        page = htmlpage.HtmlPage(self.rootFolder, 'other.html', 'Other Methods', cssRelPath='')
        self._setPageNavigation(page, relpath = '')

        hdr = ['Method', 'Calls', 'Emits', 'Connections', 'Disconnections']
        align = [False, True, True, True, True]

        table = htmltable.HtmlTable(5, hdr, align)

        sort = sorted(self.mapper.otherMethods.keys())
        for key in sort:
            method = self.mapper.otherMethods[key]

            tr = []
            m = page.link(method.htmlName(), method.method(), relpath='methods/')
            c = page.classLink(method.symbol.symbolName, '', relpath='classes/')
            tr.append(c + '::' + m)
            tr.append(str(len(method.calls)) + ' call')
            tr.append(str(len(method.emits)) + ' emit')
            tr.append(str(len(method.connections)) + ' conn')
            tr.append(str(len(method.disconnections)) + ' dconn')
            table.append(tr)

            self._createOtherPage(method)

        page.addContent(table.html())
        page.write()

    def _createOtherPage(self, otherMethod):
        page = htmlpage.HtmlPage(self.rootFolder + 'methods/', otherMethod.htmlName(), otherMethod.method(), cssRelPath='../')
        self._setPageNavigation(page, relpath = '../')

        page.addContent(page.h(1, otherMethod.method()))
        page.addContent(page.p('Slot Class: ' + page.classLink(otherMethod.symbol.symbolName, '', '../classes/')))

        # *** Calls ***
        if(len(otherMethod.calls)):
            page.addContent(page.h(2, '%s Calls%s' % (len(otherMethod.calls), '' if len(otherMethod.calls) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Called Class', 'Called Method'], [False, False])
            for key in otherMethod.calls:
                method = otherMethod.calls[key]
                tr = [page.classLink(method.symbol.symbolName, otherMethod.symbol.symbolName, '../classes/')]
                tr.append(page.link(method.htmlName(), method.method(), relpath=''))
                table.append(tr)
            page.addContent(table.html())
        # *** Emits ***
        if(len(otherMethod.emits)):
            page.addContent(page.h(2, '%s Emits%s' % (len(otherMethod.emits), '' if len(otherMethod.emits) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Emitted Class', 'Emitted Method'], [False, False])
            for key in otherMethod.emits:
                method = otherMethod.emits[key]
                tr = [page.classLink(method.symbol.symbolName, otherMethod.symbol.symbolName, '../classes/')]
                tr.append(page.link(method.htmlName(), method.method(), relpath=''))
                table.append(tr)
            page.addContent(table.html())
        # *** Connections ***
        if(len(otherMethod.connections)):
            page.addContent(page.h(2, '%s Connections Made%s' % (len(otherMethod.connections), '' if len(otherMethod.connections) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Emitter', 'Receiver'], [False, False])
            for key in otherMethod.connections:
                qtConn = otherMethod.connections[key]
                cEmitter = page.classLink(qtConn.emitter.symbol.symbolName, otherMethod.symbol.symbolName, relpath='../classes/')
                cReceiver = page.classLink(qtConn.receiver.symbol.symbolName, otherMethod.symbol.symbolName, relpath='../classes/')
                mEmitter = page.link(qtConn.emitter.key(), qtConn.emitter.method(), relpath='')
                mReceiver = page.link(qtConn.receiver.key(), qtConn.receiver.method(), relpath='')
                tr = [cEmitter + '::' + mEmitter]
                tr.append(cReceiver + '::' + mReceiver)
                table.append(tr)
            page.addContent(table.html())
        # *** Disconnector ***
        if(len(otherMethod.disconnections)):
            page.addContent(page.h(2, '%s Disconnections Made%s' % (len(otherMethod.disconnections), '' if len(otherMethod.disconnections) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Disconnected Class', 'Disconnected Method'], [False, False])
            for key in otherMethod.disconnections:
                qtConn = otherMethod.disconnections[key]
                cEmitter = page.classLink(qtConn.emitter.symbol.symbolName, otherMethod.symbol.symbolName, relpath='../classes/')
                cReceiver = page.classLink(qtConn.receiver.symbol.symbolName, otherMethod.symbol.symbolName, relpath='../classes/')
                mEmitter = page.link(qtConn.emitter.key(), qtConn.emitter.method(), relpath='')
                mReceiver = page.link(qtConn.receiver.key(), qtConn.receiver.method(), relpath='')
                tr = [cEmitter + '::' + mEmitter]
                tr.append(cReceiver + '::' + mReceiver)
                table.append(tr)
            page.addContent(table.html())
        page.write()

    def _createSlotPage(self, slot):
        page = htmlpage.HtmlPage(self.rootFolder + 'methods/', slot.htmlName(), slot.method(), cssRelPath='../')
        self._setPageNavigation(page, relpath = '../')

        page.addContent(page.h(1, slot.method()))
        page.addContent(page.p('Slot Class: ' + page.classLink(slot.symbol.symbolName, '', '../classes/')))

        tbl = htmltable.HtmlTable(3, ['Triggers', 'Slot', 'Receivers'])
        trigs = ''
        rcvs = ''

        # *** Trigger ***
        if(len(slot.triggers)):
            page.addContent(page.h(2, '%s Trigger%s' % (len(slot.triggers), '' if len(slot.triggers) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Trigger Class', 'Trigger Method'], [False, False])
            for key in slot.triggers:
                method = slot.triggers[key]
                tr = [page.classLink(method.symbol.symbolName, slot.symbol.symbolName, '../classes/')]
                tr.append(page.link(method.htmlName(), method.method(), relpath=''))
                table.append(tr)
                trigs += tr[0] + '::' + tr[1] + '<br>'
            page.addContent(table.html())
        # *** Connector ***
        if(len(slot.connectors)):
            page.addContent(page.h(2, '%s Connector%s' % (len(slot.connectors), '' if len(slot.connectors) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Connecting Class', 'Connecting Method'], [False, False])
            for key in slot.connectors:
                method = slot.connectors[key]
                tr = [page.classLink(method.symbol.symbolName, slot.symbol.symbolName, '../classes/')]
                tr.append(page.link(method.htmlName(), method.method(), relpath=''))
                table.append(tr)
            page.addContent(table.html())
        # *** Disconnector ***
        if(len(slot.disconnectors)):
            page.addContent(page.h(2, '%s Disconnector%s' % (len(slot.disconnectors), '' if len(slot.disconnectors) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Disconnecting Class', 'Disconnecting Method'], [False, False])
            for key in slot.disconnectors:
                method = slot.disconnectors[key]
                tr = [page.classLink(method.symbol.symbolName, slot.symbol.symbolName, '../classes/')]
                tr.append(page.link(method.htmlName(), method.method(), relpath=''))
                table.append(tr)
            page.addContent(table.html())
        # *** Caller ***
        if(len(slot.callers)):
            page.addContent(page.h(2, '%s Caller%s' % (len(slot.callers), '' if len(slot.callers) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Caller Class', 'Caller Method'], [False, False])
            for key in slot.callers:
                method = slot.callers[key]
                tr = [page.classLink(method.symbol.symbolName, slot.symbol.symbolName, '../classes/')]
                tr.append(page.link(method.htmlName(), method.method(), relpath=''))
                table.append(tr)
                trigs += tr[0] + '::' + tr[1] + '<br>'
            page.addContent(table.html())
        # *** Calls ***
        if(len(slot.calls)):
            page.addContent(page.h(2, '%s Calls%s' % (len(slot.calls), '' if len(slot.calls) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Called Class', 'Called Method'], [False, False])
            for key in slot.calls:
                method = slot.calls[key]
                tr = [page.classLink(method.symbol.symbolName, slot.symbol.symbolName, '../classes/')]
                tr.append(page.link(method.htmlName(), method.method(), relpath=''))
                table.append(tr)
                rcvs += tr[0] + '::' + tr[1] + '<br>'
            page.addContent(table.html())
        # *** Emits ***
        if(len(slot.emits)):
            page.addContent(page.h(2, '%s Emits%s' % (len(slot.emits), '' if len(slot.emits) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Emitted Class', 'Emitted Method'], [False, False])
            for key in slot.emits:
                method = slot.emits[key]
                tr = [page.classLink(method.symbol.symbolName, slot.symbol.symbolName, '../classes/')]
                tr.append(page.link(method.htmlName(), method.method(), relpath=''))
                table.append(tr)
                rcvs += tr[0] + '::' + tr[1] + '<br>'
            page.addContent(table.html())
        # *** Connections ***
        if(len(slot.connections)):
            page.addContent(page.h(2, '%s Connections Made%s' % (len(slot.connections), '' if len(slot.connections) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Emitter', 'Receiver'], [False, False])
            for key in slot.connections:
                qtConn = slot.connections[key]
                cEmitter = page.classLink(qtConn.emitter.symbol.symbolName, slot.symbol.symbolName, relpath='../classes/')
                cReceiver = page.classLink(qtConn.receiver.symbol.symbolName, slot.symbol.symbolName, relpath='../classes/')
                mEmitter = page.link(qtConn.emitter.key(), qtConn.emitter.method(), relpath='')
                mReceiver = page.link(qtConn.receiver.key(), qtConn.receiver.method(), relpath='')
                tr = [cEmitter + '::' + mEmitter]
                tr.append(cReceiver + '::' + mReceiver)
                table.append(tr)
            page.addContent(table.html())
        # *** Disconnector ***
        if(len(slot.disconnections)):
            page.addContent(page.h(2, '%s Disconnections Made%s' % (len(slot.disconnections), '' if len(slot.disconnections) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Disconnected Class', 'Disconnected Method'], [False, False])
            for key in slot.disconnections:
                qtConn = slot.disconnections[key]
                cEmitter = page.classLink(qtConn.emitter.symbol.symbolName, slot.symbol.symbolName, relpath='../classes/')
                cReceiver = page.classLink(qtConn.receiver.symbol.symbolName, slot.symbol.symbolName, relpath='../classes/')
                mEmitter = page.link(qtConn.emitter.key(), qtConn.emitter.method(), relpath='')
                mReceiver = page.link(qtConn.receiver.key(), qtConn.receiver.method(), relpath='')
                tr = [cEmitter + '::' + mEmitter]
                tr.append(cReceiver + '::' + mReceiver)
                table.append(tr)
            page.addContent(table.html())

        tbl.append([trigs, slot.name(), rcvs])
        page.pageBody.insert(2, tbl.html())

        page.write()

    def _createSignalPage(self, signal):
        page = htmlpage.HtmlPage(self.rootFolder + 'methods/', signal.htmlName(), signal.method(), cssRelPath='../')
        self._setPageNavigation(page, relpath = '../')

        page.addContent(page.h(1, signal.method()))
        page.addContent(page.p('Signal Class: ' + page.classLink(signal.symbol.symbolName, '', '../classes/')))

        imgpath = self.rootFolder + '/images/' + signal._key
        dotgraph.generateSignalMap(signal, '../methods/', imgpath)
        imgpath += '.svg'
        with open(imgpath, 'r') as f:
            html = ''
            for line in f:
                html += line + '\n'
            page.addContent(html)
        #page.addContent("<object type='image/svg+xml' data='%s'>Your browser does not support SVG</object>" % ('../images/' + signal._key + '.svg'))
        #page.addContent("<object type='image/svg+xml' data='%s'>Your browser does not support SVG</object>" % ('../images/' + signal._key + '.svg'))

        tbl = htmltable.HtmlTable(3, ['Triggers', 'Signal', 'Receivers'])
        trigs = ''
        rcvs = ''

        # *** RECEIVERS ***
        if(len(signal.receivers)):
            page.addContent(page.h(2, '%s Receiver%s' % (len(signal.receivers), '' if len(signal.receivers) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Receiver Class', 'Receiver Method'], [False, False])
            for key in signal.receivers:
                method = signal.receivers[key]
                tr = [page.classLink(method.symbol.symbolName, signal.symbol.symbolName, '../classes/')]
                tr.append(page.link(method.htmlName(), method.method(), relpath=''))
                table.append(tr)
                rcvs += tr[0] + '::' + tr[1] + '<br>'
            page.addContent(table.html())
        # *** Connector ***
        if(len(signal.connectors)):
            page.addContent(page.h(2, '%s Connector%s' % (len(signal.connectors), '' if len(signal.connectors) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Connecting Class', 'Connecting Method'], [False, False])
            for key in signal.connectors:
                method = signal.connectors[key]
                tr = [page.classLink(method.symbol.symbolName, signal.symbol.symbolName, '../classes/')]
                tr.append(page.link(method.htmlName(), method.method(), relpath=''))
                table.append(tr)
            page.addContent(table.html())
        # *** Disconnector ***
        if(len(signal.disconnectors)):
            page.addContent(page.h(2, '%s Disconnector%s' % (len(signal.disconnectors), '' if len(signal.disconnectors) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Disconnecting Class', 'Disconnecting Method'], [False, False])
            for key in signal.disconnectors:
                method = signal.disconnectors[key]
                tr = [page.classLink(method.symbol.symbolName, signal.symbol.symbolName, '../classes/')]
                tr.append(page.link(method.htmlName(), method.method(), relpath=''))
                table.append(tr)
            page.addContent(table.html())
        # *** Trigger ***
        if(len(signal.triggers)):
            page.addContent(page.h(2, '%s Trigger%s' % (len(signal.triggers), '' if len(signal.triggers) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Trigger Class', 'Trigger Method'], [False, False])
            for key in signal.triggers:
                method = signal.triggers[key]
                tr = [page.classLink(method.symbol.symbolName, signal.symbol.symbolName, '../classes/')]
                tr.append(page.link(method.htmlName(), method.method(), relpath=''))
                table.append(tr)
                trigs += tr[0] + '::' + tr[1] + '<br>'
            page.addContent(table.html())
        # *** Emitters ***
        if(len(signal.emitters)):
            page.addContent(page.h(2, '%s Emitter%s' % (len(signal.emitters), '' if len(signal.emitters) == 1 else 's')))
            table = htmltable.HtmlTable(2, ['Emitter Class', 'Emitter Method'], [False, False])
            for key in signal.emitters:
                method = signal.emitters[key]
                tr = [page.classLink(method.symbol.symbolName, signal.symbol.symbolName, '../classes/')]
                tr.append(page.link(method.htmlName(), method.method(), relpath=''))
                table.append(tr)
                trigs += tr[0] + '::' + tr[1] + '<br>'
            page.addContent(table.html())

        tbl.append([trigs, signal.name(), rcvs])
        page.pageBody.insert(2, tbl.html())

        page.write()

    def _createClassPage(self, symbol):
        page = htmlpage.HtmlPage(os.path.join(self.rootFolder, 'classes/'), symbol.key, symbol.symbolName, cssRelPath='../')
        self._setPageNavigation(page, relpath='../')

        page.addContent(page.h(1, symbol.symbolName))
        if(symbol.hasHeader()):
            page.addContent(page.p('Header: ' + self.mapper.srcRootPath(symbol.header.path)))
        if(symbol.hasSource()):
            page.addContent(page.p('Source: ' + self.mapper.srcRootPath(symbol.source.path)))


        # *** SIGNALS ***
        if(len(symbol.signals)):
            page.addContent(page.h(2, '%s Signal%s' % (len(symbol.signals), ('' if len(symbol.signals) == 1 else 's'))))

        sortedSymbols = sorted(symbol.signals.keys())
        for key in sortedSymbols:
            signal = symbol.signals[key]
            page.addContent(page.h(3, page.link(signal.key(), signal.method(), '../methods/')))

            table = htmltable.HtmlTable(3, ['Action', 'Class', 'Method'], [False, True, True])

            if(len(signal.emitters)):
                for key in signal.emitters:
                    method = signal.emitters[key]
                    tr = ['emitted by fn']
                    tr.append(page.classLink(method.symbol.symbolName, symbol.symbolName, relpath = ''))
                    tr.append(page.link(method.key(), method.method(), relpath='../methods/'))
                    table.append(tr)
            if(len(signal.triggers)):
                for key in signal.triggers:
                    method = signal.triggers[key]
                    tr = ['emitted by signal']
                    tr.append(page.classLink(method.symbol.symbolName, symbol.symbolName, relpath = ''))
                    tr.append(page.link(method.key(), method.method(), relpath='../methods/'))
                    table.append(tr)
            if(len(signal.receivers)):
                for key in signal.receivers:
                    method = signal.receivers[key]
                    tr = ['signal received by']
                    tr.append(page.classLink(method.symbol.symbolName, symbol.symbolName, relpath = ''))
                    tr.append(page.link(method.key(), method.method(), relpath='../methods/'))
                    table.append(tr)
            if(len(signal.connectors)):
                for key in signal.connectors:
                    method = signal.connectors[key]
                    tr = ['connected by']
                    tr.append(page.classLink(method.symbol.symbolName, symbol.symbolName, relpath = ''))
                    tr.append(page.link(method.key(), method.method(), relpath='../methods/'))
                    table.append(tr)
            if(len(signal.disconnectors)):
                for key in signal.disconnectors:
                    method = signal.disconnectors[key]
                    tr = ['disconnected by']
                    tr.append(page.classLink(method.symbol.symbolName, symbol.symbolName, relpath = ''))
                    tr.append(page.link(method.key(), method.method(), relpath='../methods/'))
                    table.append(tr)
            page.addContent(table.html())
        # *** SLOTS ***
        if(len(symbol.slots)):
            page.addContent(page.h(2, '%s Slot%s' % (len(symbol.slots), ('' if len(symbol.slots) == 1 else 's'))))
        sortedSymbols = sorted(symbol.slots.keys())
        for key in sortedSymbols:
            slot = symbol.slots[key]
            page.addContent(page.h(3, page.link(slot.key(), slot.method(), '../methods/')))

            table = htmltable.HtmlTable(3, ['Action', 'Class', 'Method'], [False, True, True])

            if(len(slot.triggers)):
                for key in slot.triggers:
                    method = slot.triggers[key]
                    tr = ['triggered by signal']
                    tr.append(page.classLink(method.symbol.symbolName, symbol.symbolName, relpath = ''))
                    tr.append(page.link(method.key(), method.method(), relpath='../methods/'))
                    table.append(tr)
            if(len(slot.callers)):
                for key in slot.callers:
                    method = slot.callers[key]
                    tr = ['slot called by']
                    tr.append(page.classLink(method.symbol.symbolName, symbol.symbolName, relpath = ''))
                    tr.append(page.link(method.key(), method.method(), relpath='../methods/'))
                    table.append(tr)
            if(len(slot.connectors)):
                for key in slot.connectors:
                    method = slot.connectors[key]
                    tr = ['connected by']
                    tr.append(page.classLink(method.symbol.symbolName, symbol.symbolName, relpath = ''))
                    tr.append(page.link(method.key(), method.method(), relpath='../methods/'))
                    table.append(tr)
            if(len(slot.disconnectors)):
                for key in slot.disconnectors:
                    method = slot.disconnectors[key]
                    tr = ['disconnected by']
                    tr.append(page.classLink(method.symbol.symbolName, symbol.symbolName, relpath = ''))
                    tr.append(page.link(method.key(), method.method(), relpath='../methods/'))
                    table.append(tr)
            page.addContent(table.html())

        # *** CONNECTIONS ***
        table = None
        if(symbol.totalConnections()):
            page.addContent(page.h(2, '%s Connection%s' % (symbol.totalConnections(), ('' if symbol.totalConnections() == 1 else 's'))))
            table = htmltable.HtmlTable(3, ['Action', 'Class', 'Method'], [False, True, True])
        #sort = sorted(symbol.connections.keys())
        for key in symbol.connections:
            connector = symbol.connections[key]
            conns = connector.getSymbolConnections(symbol)
            for qtConn in conns:
                # create links
                cEmitter = page.classLink(qtConn.emitter.symbol.symbolName, symbol.symbolName, relpath='')
                cReceiver = page.classLink(qtConn.receiver.symbol.symbolName, symbol.symbolName, relpath='')
                mEmitter = page.link(qtConn.emitter.key(), qtConn.emitter.method(), relpath='../methods/')
                mReceiver = page.link(qtConn.receiver.key(), qtConn.receiver.method(), relpath='../methods/')
                # populate table row
                tr = ['<code>this</code> connected']
                tr.append(cEmitter + '::' + mEmitter)
                tr.append(cReceiver + '::' + mReceiver)
                table.append(tr)
        for key in symbol.otherConnections:
            connector = symbol.otherConnections[key]
            conns = connector.getSymbolConnections(symbol)
            for qtConn in conns:
                # create links
                cEmitter = page.classLink(qtConn.emitter.symbol.symbolName, symbol.symbolName, relpath='')
                cReceiver = page.classLink(qtConn.receiver.symbol.symbolName, symbol.symbolName, relpath='')
                mEmitter = page.link(qtConn.emitter.key(), qtConn.emitter.method(), relpath='../methods/')
                mReceiver = page.link(qtConn.receiver.key(), qtConn.receiver.method(), relpath='../methods/')
                # populate table row
                tr = ['<code>%s</code> connected' % connector.symbol.symbolName]
                tr.append(cEmitter + '::' + mEmitter)
                tr.append(cReceiver + '::' + mReceiver)
                table.append(tr)
        for key in symbol.disconnections:
            connector = symbol.disconnections[key]
            conns = connector.getSymbolDisconnections(symbol)
            for qtConn in conns:
                # create links
                cEmitter = page.classLink(qtConn.emitter.symbol.symbolName, symbol.symbolName, relpath='')
                cReceiver = page.classLink(qtConn.receiver.symbol.symbolName, symbol.symbolName, relpath='')
                mEmitter = page.link(qtConn.emitter.key(), qtConn.emitter.method(), relpath='../methods/')
                mReceiver = page.link(qtConn.receiver.key(), qtConn.receiver.method(), relpath='../methods/')
                # populate table row
                tr = ['<code>this</code> disconnected']
                tr.append(cEmitter + '::' + mEmitter)
                tr.append(cReceiver + '::' + mReceiver)
                table.append(tr)
        for key in symbol.otherDisconnections:
            connector = symbol.otherDisconnections[key]
            conns = connector.getSymbolDisconnections(symbol)
            for qtConn in conns:
                # create links
                cEmitter = page.classLink(qtConn.emitter.symbol.symbolName, symbol.symbolName, relpath='')
                cReceiver = page.classLink(qtConn.receiver.symbol.symbolName, symbol.symbolName, relpath='')
                mEmitter = page.link(qtConn.emitter.key(), qtConn.emitter.method(), relpath='../methods/')
                mReceiver = page.link(qtConn.receiver.key(), qtConn.receiver.method(), relpath='../methods/')
                # populate table row
                tr = ['<code>%s</code> disconnected' % connector.symbol.symbolName]
                tr.append(cEmitter + '::' + mEmitter)
                tr.append(cReceiver + '::' + mReceiver)
                table.append(tr)
        if table is not None:
            page.addContent(table.html())

        # *** Callers ***
        if(len(symbol.callers)):
            page.addContent(page.h(2, '%s Caller Method%s' % (len(symbol.callers), ('' if len(symbol.callers) == 1 else 's'))))
        for key in symbol.callers:
            caller = symbol.callers[key]
            page.addContent(page.h(3, page.link(caller.key(), caller.method(), '../methods/')))

            table = htmltable.HtmlTable(3, ['Action', 'Class', 'Method'], [False, True, True])

            if(len(caller.calls)):
                for key in caller.calls:
                    method = caller.calls[key]
                    tr = ['calls']
                    tr.append(page.classLink(method.symbol.symbolName, symbol.symbolName, relpath = ''))
                    tr.append(page.link(method.key(), method.method(), relpath='../methods/'))
                    table.append(tr)
            page.addContent(table.html())

        # *** Emitters ***
        if(len(symbol.emitters)):
            page.addContent(page.h(2, '%s Emitter Method%s' % (len(symbol.emitters), ('' if len(symbol.emitters) == 1 else 's'))))
        for key in symbol.emitters:
            emitter = symbol.emitters[key]
            page.addContent(page.h(3, page.link(emitter.key(), emitter.method(), '../methods/')))

            table = htmltable.HtmlTable(3, ['Action', 'Class', 'Method'], [False, True, True])

            if(len(emitter.emits)):
                for key in emitter.emits:
                    method = emitter.emits[key]
                    tr = ['emits']
                    tr.append(page.classLink(method.symbol.symbolName, symbol.symbolName, relpath = ''))
                    tr.append(page.link(method.key(), method.method(), relpath='../methods/'))
                    table.append(tr)
            page.addContent(table.html())

        # *** Called @todo methods that are called by other classes ***
        page.write()
    def createCSS(self):
        if not os.path.exists(os.path.join(self.rootFolder + 'css/')):
            os.makedirs(os.path.join(self.rootFolder + 'css/'))
        copyfile(self.cssPath, self.rootFolder + 'css/main.css')

    def _setPageNavigation(self, page, relpath):
        page.addNavLink(os.path.join(relpath, 'index.html'), 'Index')
        page.addNavLink(os.path.join(relpath, 'classes.html'), 'Classes')
        page.addNavLink(os.path.join(relpath, 'signals.html'), 'Signals')
        page.addNavLink(os.path.join(relpath, 'slots.html'), 'Slots')
        page.addNavLink(os.path.join(relpath, 'other.html'), 'Other')

    def _checkPath(self):
        if(os.path.isdir(self.rootFolder)):
            self.pathValid = True
        else:
            self.pathValid = False
