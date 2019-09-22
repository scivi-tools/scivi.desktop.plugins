#include "generator.h"
#include <QDebug>
#include <datanode.h>
#include <QDir>
#include <QJsonDocument>


#ifdef _DEBUG
#undef _DEBUG
#include <PythonQt.h>
#else
#include <PythonQt.h>
#endif

namespace scivi {

Generator::Generator(QObject *parent): QObject(parent)
{
    PythonQt::init();
    connect(PythonQt::self(), &PythonQt::pythonStdOut, this, [](const QString &msg) {
        qDebug() << msg;
    });
    connect(PythonQt::self(), &PythonQt::pythonStdErr, this, [](const QString &msg) {
        qWarning() << msg;
    });
    QObject::connect(&m_genProcess, static_cast<void(QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished), this, &Generator::firmwareProcessFinished);
}

void Generator::generate(QString nodeName, DataflowDiagram *diagram, QString outputPath)
{
    Q_UNUSED(outputPath);
    if (nodeName == "") {
        qWarning() << "Empty host node name";
        return;
    }
    QSharedPointer<DataNode> hostNode;
    auto nodes = diagram->nodes();
    for (const auto &node: nodes) {
        auto dataNode = qSharedPointerDynamicCast<DataNode>(node);
        if (!dataNode.isNull() && dataNode.data()->name() == nodeName) {
            hostNode = dataNode;
            break;
        }
    }
    if (hostNode == nullptr) {
        qWarning() << "Cannot read host datanode";
        return;
    }
    auto doc = QJsonDocument(diagram->toJsonObject());
    QJsonObject rootObj = doc.object();
    QJsonObject hostObject = hostNode->toJsonObject();
    rootObj["host"] = hostObject;
    QString pathToDiagram = QDir::tempPath() +  "/dataflow.json";
    doc.setObject(rootObj);

    PythonQtObjectPtr module = PythonQt::self()->createUniqueModule();
    // HACK: Copy binary script from resources to filesystem
    QString tempDir = QDir::tempPath();
    qDebug() << tempDir;
    QFile::copy(":/FirmwareGen/py/onto.py", QDir::toNativeSeparators(tempDir + "/onto.py"));
    PythonQt::self()->addSysPath(QDir::tempPath());

    module.evalFile(":/FirmwareGen/py/codegen.py");
    QVariant result = module.call("generate", QVariantList() << doc.toVariant());
    if (result.isValid()) {
        QFile file(outputPath);
        if (!file.open(QIODevice::WriteOnly)) {
            qWarning() << "Couldn't open output file" << file.errorString();
        }
        QString code = result.toString();
        file.write(code.toUtf8());
    } else {
        qWarning() << "ERROR retrieving result from python!";
    }
}

void Generator::firmwareProcessFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    Q_UNUSED(exitCode);
    Q_UNUSED(exitStatus);
    qDebug() << QString::fromUtf8(m_genProcess.readAll());
}

}
