#!/usr/local/bin/python3
def cppSymbolEncoder(symbolStr):
    symbolStr = symbolStr.replace('*', '')
    symbolStr = symbolStr.replace(',', '_')
    symbolStr = symbolStr.replace('::', '__')
    symbolStr = symbolStr.replace('()', '')
    symbolStr = symbolStr.replace('(', '__')
    symbolStr = symbolStr.replace(')', '')
    symbolStr = symbolStr.replace('<', '_')
    symbolStr = symbolStr.replace('>', '_')
    symbolStr = symbolStr.replace(' ', '')
    return symbolStr

def substrBetween(text, firstMatch, lastMatch):
    try:
        start = text.index(firstMatch) + len(firstMatch)
        end = text.index(lastMatch, start)
        return text[start:end]
    except ValueError:
        return ''

def rSubstrBetween(text, firstMatch, lastMatch):
    try:
        start = text.rindex(firstMatch) + len(firstMatch)
        end = text.rindex(lastMatch, start)
        return text[start:end]
    except ValueError:
        return ''
