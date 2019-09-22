unix|win32: LIBS += -L$$PWD/scivi.desktop/scivi2core/lib/ -lscivi2core

INCLUDEPATH += $$PWD/scivi.desktop/scivi2core/src
DEPENDPATH += $$PWD/scivi.desktop/scivi2core

win32:!win32-g++: PRE_TARGETDEPS += $$PWD/scivi.desktop/scivi2core/lib/scivi2core.lib
else:unix|win32-g++: PRE_TARGETDEPS += $$PWD/scivi.desktop/scivi2core/lib/libscivi2core.a
