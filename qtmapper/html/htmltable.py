class HtmlTable:
    def __init__(self, cols, header = [], colAlignment=[]):
        self.cols = cols
        self.rows = []

        if(len(header) != 0):
            if(len(header) == cols):
                self.header = header
            else:
                print('HtmlTable.__init__ ERROR wrong col count in header')
                print(header)
                self.header = []
        else:
            self.header = []
        if(len(colAlignment) != 0):
            if(len(colAlignment) == cols):
                self.colAlignment = colAlignment
            else:
                print('HtmlTable.__init__ ERROR wrong col count in cellAlignment')
                self.colAlignment = []
        else:
            self.colAlignment = []

    def append(self, rowCells):
        if(self._checkColCount(rowCells) == False):
            print("HtmlTable.addRow ERROR rowCells col count doesn't match col count in row data")
        else:
            self.rows.append(rowCells)

    def setHeader(self, header):
        if(self._checkColCount(header)):
            self.header = header
        else:
            print("HtmlTable.setHeader ERROR header col count doesn't match col count in row data")

    def setColAlignment(self, alignment):
        if(self._checkColCount(alignment)):
            self.colAlignment = alignment
        else:
            print("HtmlTable.setCellAlignment ERROR alignment col count doesn't match col count in row data")

    def html(self):
        table = '<table>\n'
        if(len(self.header)):
            table += '\t' + self.tr(self.header)
        for row in self.rows:
            table += '\t' + self.tr(row)
        table += '</table>'
        return table

    def tr(self, row):
        if(self._checkColCount(row) == False):
            return ''
        tr = '<tr>\n'
        useAlignment = False
        if(len(self.colAlignment)):
            useAlignment = True
        cellID = 0
        for td in row:
            cellTag = 'td'
            success = False
            if useAlignment:
                if cellID in self.colAlignment:
                    if self.colAlignment[cellID]:
                        tr += '\t<%s><center>%s</center></%s>\n' % (cellTag, str(td), cellTag)
                        success = True
            if success == False:
                tr += '\t<%s>%s</%s>\n' % (cellTag, str(td), cellTag)
            cellID += 1
        tr += '</tr>'
        return tr

    def _checkColCount(self, cells):
        return (len(cells) == self.cols)
