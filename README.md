# QtMapper

This is a tool that parses a Qt project and extracts information about signals and slots.

## Installation Requirements

Requires Python 3

Requires CppHeaderParser

```python
pip install cppheaderparser
```

## Preparing the Qt Project

The current version of `QtMapper` requires signals and slots to be marked in the source code, a bit like Doxygen requires additional markup for descriptions.

Further versions may make use of `clang` python bindings to automatically detect all signals, slots and relevant references automatically.

```cpp
//@connect***ClassOfSignal***ClassOfReceiver***ClassMakingConnection::methodMakingConnection(.. args ..)
this->connect(this->classA, SIGNAL(signalA()), this->classB, SLOT(slotB(int*,bool)));

//@disconnect***ClassOfSignal***ClassOfReceiver***ClassMakingDisconnection::methodMakingDisconnection(.. args ..)
this->disconnect(this->classA, SIGNAL(signalA()), this->classB, SLOT(slotB(int*,bool)));

//@emit***ClassOfSignal::signal(...args...)***ClassEmitting::methodEmitting(...args...)
emit this->signal(...args...)

//@caller***ClassOfSlot::slot(...args...)***ClassCallingSlot::methodCallingSlot(...args...)
this->slotBeingCalled(...)
```

## Running QtMapper

```python
#!/usr/local/bin/python3
import qtmapper.mapper as mapper
import qtmapper.html.htmlwriter as htmlwriter

if __name__ == '__main__':
	pathToRootOfQtProject = '/Users/xxx/qt/project_x/src/'
	mapper = mapper.QtSignalSlotMapper(pathToRootOfQtProject)
	mapper.run()

	pathToOutputHTML = '/Users/xxx/qt/project_x/docs/qtmapped/html/'
	writer = htmlwriter.HtmlWriter(mapper, pathToOutputHTML)
	writer.write()

```
