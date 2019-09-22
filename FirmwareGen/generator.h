#ifndef GENERATOR_H
#define GENERATOR_H

#include <QString>
#include <QObject>
#include <QProcess>
#include <dataflowdiagram.h>

namespace scivi {

using namespace diagram;

class Generator: public QObject
{
    Q_OBJECT
public:
    explicit Generator(QObject *parent = nullptr);
    Q_INVOKABLE void generate(QString nodeName, DataflowDiagram *diagram, QString outputPath);
public slots:
    void firmwareProcessFinished(int exitCode, QProcess::ExitStatus exitStatus);
private:
    QProcess m_genProcess;
};

}

#endif // GENERATOR_H
