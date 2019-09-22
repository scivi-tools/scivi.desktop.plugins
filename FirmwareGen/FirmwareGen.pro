QT -= gui
QT += qml quick

TEMPLATE = lib
TARGET = FirmwareGenPlugin
CONFIG += c++11 plugin
CONFIG
TARGET = $$qtLibraryTarget($$TARGET)
uri = FirmwareGen
QMAKE_MOC_OPTIONS += -Muri=$$uri

include($$PWD/../3p/PythonQt.pri)
include($$PWD/../scivi2plugin.pri)

DESTDIR = ../FirmwareGen
DEFINES += FIRMWAREGEN_LIBRARY

SOURCES += \
    firmwaregen_plugin.cpp \
    generator.cpp \
    nodesmodel.cpp

HEADERS += \
    firmwaregen_global.h \
    firmwaregen_plugin.h \
    generator.h \
    nodesmodel.h

DISTFILES += qmldir \
    qml/FirmwareGenDialog.qml \
    codegen.py \
    onto.py

RESOURCES += \
    qmlfirmwaregen.qrc

!equals(_PRO_FILE_PWD_, $$OUT_PWD) {
    copy_qmldir.target = $$OUT_PWD/qmldir
    copy_qmldir.depends = $$_PRO_FILE_PWD_/qmldir
    copy_qmldir.commands = $(COPY_FILE) \"$$replace(copy_qmldir.depends, /, $$QMAKE_DIR_SEP)\" \"$$replace(copy_qmldir.target, /, $$QMAKE_DIR_SEP)\"
    QMAKE_EXTRA_TARGETS += copy_qmldir
    PRE_TARGETDEPS += $$copy_qmldir.target
}

qmldir.files = qmldir
unix {
    installPath = $$[QT_INSTALL_QML]/$$replace(uri, \\., /)
    qmldir.path = $$installPath
    target.path = $$installPath
    INSTALLS += target qmldir
}
