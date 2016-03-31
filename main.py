#!/usr/local/bin/python3
import os

import qtmapper.mapper as mapper
#import qtmapper.html as html
import qtmapper.html.htmlwriter as htmlwriter

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    print(os.getcwd())
    try:
        import CppHeaderParser
        mapper = mapper.QtSignalSlotMapper('../readalo/src/ReadaloX/')
        mapper.run()
        print(mapper.parser)

        #print(sorted(mapper.symbols.keys()))

        writer = htmlwriter.HtmlWriter(mapper, 'html/')
        writer.write()

    except ImportError:
        print('Module CppHeaderParser not found. Please install:')
        print('$ pip install cppheaderparser')
