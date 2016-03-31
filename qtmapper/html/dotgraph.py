#!/usr/local/bin/python3

# http://matthiaseisen.com/articles/graphviz/
import os
import graphviz as gv

def digraph():
    graph = gv.Digraph(format='svg')

    graph.node_attr['fontname'] = 'menlo'
    graph.node_attr['shape'] ='rectangle'
    graph.node_attr['fontsize'] = '10px'

    graph.edge_attr['arrowhead'] = 'open'
    graph.edge_attr['fontname'] = 'open sans'

    return graph

def getSignalTriggers(signal):
    triggers = {}
    for key in signal.triggers:
        method = signal.triggers[key]
        if method._key not in triggers:
            triggers[method._key] = method.name()
    for key in signal.emitters:
        method = signal.emitters[key]
        if method._key not in triggers:
            triggers[method._key] = method.name()
    return triggers

def getSignalReceivers(signal):
    receivers = {}
    for key in signal.receivers:
        method = signal.receivers[key]
        if method._key not in receivers:
            receivers[method._key] = method.name()
    return receivers

def generateSignalMap(signal, relpath, imgpath):
    triggers = getSignalTriggers(signal)
    receivers = getSignalReceivers(signal)

    g = digraph()
    g.node(signal._key, signal.name(), {'color':'red'})
    #g[signal._key]['color'] = 'red'

    for nodeKey in triggers:
        nodeName = triggers[nodeKey]
        nodeHref = relpath + nodeKey + '.html'
        g.node(nodeKey, nodeName, href=nodeHref)
        g.edge(nodeKey, signal._key)

    for nodeKey in receivers:
        nodeName = receivers[nodeKey]
        nodeHref = relpath + nodeKey + '.html'
        g.node(nodeKey, nodeName, href=nodeHref)
        g.edge(signal._key, nodeKey)

    g.render(imgpath, view = False)

if __name__ == '__main__':
    #g = gv.Digraph(format='png')
    os.chdir(os.path.dirname(__file__))
    g = digraph()
    g.node('A', 'ClassA::signalClick(bool)', href = 'http://www.a.com')
    g.node('B', 'ClassB::slotClickReceived(bool)')
    g.edge('A', 'B', label = 'alabel')
    g.render('../../html/images/tmp.gv', view=False)
