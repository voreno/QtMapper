import os

class HtmlPage:
    def __init__(self, folder, fileName, title, cssRelPath):
        self.folder = folder
        self.fileName = fileName
        if(self.fileName.endswith('.html') == False):
            self.fileName += '.html'

        self.path = os.path.join(self.folder, self.fileName)

        self.title = title
        self.cssRelPath = cssRelPath

        self.pageBody = []
        self.navLinks = {}

    def write(self):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        print('Writing ' + self.path)
        outFile = open(self.path, 'w+')
        outFile.write(self.html())
        outFile.close()

    def html(self):
        html = '<html>\n'
        html += self.indent(self.head())
        html += self.indent(self.body())
        html += '</html>'
        return html

    def head(self):
        head = '<head>\n'
        head += "\t<meta charset='utf-8'>\n"
        head += "\t<title>" + self.title + "</title>\n"
        head += "\t<link rel='stylesheet' type='text/css' href='" + self.cssRelPath + "css/main.css'>"
        head += "</head>"
        return head

    def body(self):
        body = '<body>\n'
        body += self.indent(self.nav())
        for content in self.pageBody:
            body += self.indent(content)
        body += '</body>'
        return body

    def nav(self):
        nav = "<nav>\n"
        #nav += '\t' + self.createLink(self.relPath + "index.html", 'Index') + ' | \n';
        for linkID in range(0,len(self.navLinks)):
            navLink = self.navLinks[linkID]
            for link in navLink:
                text = navLink[link]
                nav += '\t' + self.link(link, text, '') + '  \n'
        nav += '</nav>'
        return nav

    def addContent(self, html):
        self.pageBody.append(html)

    def addNavLink(self, href, text):
        if(len(href) and len(text)):
            navLink = {}
            navLink[href] = text
            self.navLinks[len(self.navLinks)] = navLink

    def link(self, href, text, relpath):
        href = href.replace('::', '__')
        if '.html' not in href:
            href += '.html'
        return "<a href='%s%s'>%s</a>" % (relpath, href, text)

    def classLink(self, className, thisClassName, relpath):
        text = className
        if(className == thisClassName):
            text = self._wrap('code', 'this')
        href = self._prepareClass(className)
        if '.html' not in href:
            href += '.html'
        return "<a href='%s%s'>%s</a>" % (relpath, href, text)

    def indent(self, text):
        out = ''
        lines = text.split('\n')
        for line in lines:
            out += '\t%s\n' % line
        return out

    def p(self, text):
        return self._wrap('p', text)

    def h(self, size, text):
        return self._wrap('h%s' % size, text)

    def b(self, text):
        return self._wrap('b', text)

    def _wrap(self, tag, text):
        return '<%s>%s</%s>' % (tag, text, tag)

    def _prepareClass(self, className):
        return className.replace('::', '__')
