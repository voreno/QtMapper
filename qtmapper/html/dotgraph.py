#!/usr/local/bin/python3

# http://matthiaseisen.com/articles/graphviz/
import os
import graphviz as gv

def digraph():
    #graph = gv.Digraph(format='svg', engine='circo')
    graph = gv.Digraph(format='svg', engine='dot')

    graph.graph_attr['bgcolor'] = 'transparent'
    #graph.graph_attr['orientation'] = 'landscape'
    graph.graph_attr['rankdir'] = 'LR'

    graph.node_attr['fontname'] = 'menlo'
    graph.node_attr['shape'] ='rectangle'
    graph.node_attr['fontsize'] = '8px'

    graph.edge_attr['arrowhead'] = 'open'
    graph.edge_attr['fontname'] = 'open sans'
    graph.node_attr['fontsize'] = '8px'

    return graph

def getTriggers(method):
    triggers = {}
    if method.type == 'signal':
        triggers.update(updateMethodDict(triggers, method.triggers))
        triggers.update(updateMethodDict(triggers, method.emitters))
    if method.type == 'slot':
        triggers.update(updateMethodDict(triggers, method.triggers))
        triggers.update(updateMethodDict(triggers, method.callers))
    return triggers

def getReceivers(method):
    receivers = {}
    if method.type == 'method' or method.type == 'slot':
        receivers.update(updateMethodDict(receivers, method.calls))
        receivers.update(updateMethodDict(receivers, method.emits))
    if method.type == 'signal':
        receivers.update(updateMethodDict(receivers, method.receivers))
    return receivers

def updateMethodDict(outDict, inDict):
    for key in inDict:
        method = inDict[key]
        if method._key not in outDict:
            outDict[method._key] = method
    return outDict
'''
def getSignalReceivers(signal):
    receivers = {}
    for key in signal.receivers:
        method = signal.receivers[key]
        if method._key not in receivers:
            receivers[method._key] = method.name()
    return receivers

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
'''
def generateSignalMap(signal, relpath, imgpath):
    triggers = getTriggers(signal)
    receivers = getReceivers(signal)

    g = digraph()
    g.node(signal._key, signal.name(), {'color':'red'})
    #g[signal._key]['color'] = 'red'

    for nodeKey in triggers:
        method = triggers[nodeKey]
        nodeHref = relpath + nodeKey + '.html'
        g.node(nodeKey, method.name(), href=nodeHref)
        g.edge(nodeKey, signal._key)
        mTriggers = getTriggers(method)
        for nKey in mTriggers:
            method2 = mTriggers[nKey]
            hRef = relpath + nKey + '.html'
            g.node(nKey, method2.name(), href=hRef)
            g.edge(nKey, nodeKey, style='dashed')
            m2Triggers = getTriggers(method2)
            if(len(m2Triggers)):
                g.node(nKey+'_a', ' ', shape='plaintext')
                g.edge(nKey+'_a',nKey, label='more triggers', style='dashed')


    for nodeKey in receivers:
        method = receivers[nodeKey]
        nodeHref = relpath + nodeKey + '.html'
        g.node(nodeKey, method.name(), href=nodeHref)
        g.edge(signal._key, nodeKey)
        mReceivers = getReceivers(method)
        for nKey in mReceivers:
            method2 = mReceivers[nKey]
            hRef = relpath + nKey + '.html'
            g.node(nKey, method2.name(), href=hRef)
            g.edge(nodeKey, nKey, style='dashed')
            m2Receivers = getReceivers(method2)
            if(len(m2Receivers)):
                g.node(nKey+'_a', ' ', shape='plaintext')
                g.edge(nKey, nKey+'_a', label='more receivers', style='dashed')

    g.render(imgpath, view = False)

if __name__ == '__main__':
    #g = gv.Digraph(format='png')
    os.chdir(os.path.dirname(__file__))
    g = digraph()
    g.node('A', 'ClassA::signalClick(bool)', href = 'http://www.a.com')
    g.node('B', 'ClassB::slotClickReceived(bool)')
    g.edge('A', 'B', label = 'alabel')
    g.render('../../html/images/tmp.gv', view=False)
