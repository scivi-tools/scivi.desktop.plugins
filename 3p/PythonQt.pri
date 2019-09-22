CONFIG(debug, debug|release) {
  DEBUG_EXT = _d
} else {
  DEBUG_EXT =
}

include($$PWD/PythonQt/build/python.prf)

win32::LIBS += $$OUT_PWD/../3p/PythonQt/lib/PythonQt-Qt5-Python$${PYTHON_VERSION}$${DEBUG_EXT}.lib
unix::LIBS += -L$$OUT_PWD/../3p/PythonQt/lib -lPythonQt-Qt5-Python$${PYTHON_VERSION}$${DEBUG_EXT}

unix:{
    QMAKE_LFLAGS += "-Wl,-rpath,$$OUT_PWD/../3p/PythonQt/lib"
}

INCLUDEPATH += $$PWD/PythonQt/src
