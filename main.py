#!/usr/local/bin/python3
import os

import qtmapper.mapper as mapper
#import qtmapper.html as html
import qtmapper.html.htmlwriter as htmlwriter

if __name__ == '__main__':
    # for debug purposes (relpaths)
    os.chdir(os.path.dirname(__file__))
    #print(os.getcwd())

    failedImports = False
    try:
        import CppHeaderParser
    except ImportError:
        print('Module CppHeaderParser not found. Please install:')
        print('$ pip install cppheaderparser')
        failedImports = True

    try:
        import graphviz
    except ImportError:
        print('or Module graphviz not found. Please install:')
        print('$ pip install graphviz')
        failedImports = True

    if failedImports is not True:
        mapper = mapper.QtSignalSlotMapper('../readalo/src/ReadaloX/')
        #mapper = mapper.QtSignalSlotMapper('test_data/data_small/')
        mapper.run()
        print(mapper.parser)

        #print(sorted(mapper.symbols.keys()))

        writer = htmlwriter.HtmlWriter(mapper, 'html/')
        writer.write()
