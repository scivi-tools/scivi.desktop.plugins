#include "firmwaregen_plugin.h"
#include <QDebug>
#include <QJsonDocument>
#include <QJsonObject>
#include <QDir>

#include <qqml.h>
#include <QQmlComponent>
#include "nodesmodel.h"

FirmwareGen::FirmwareGen(QObject *parent): QQmlExtensionPlugin(parent)
{
}

FirmwareGen::~FirmwareGen()
{

}

QString FirmwareGen::name() const
{
    return tr("Firmware generation plugin");
}

void FirmwareGen::initialize(IntializeParams params)
{
    Q_UNUSED(params);
    qDebug() << "Initialize firmware plugin";
}

void FirmwareGen::startup(StartupParams params)
{
    Q_UNUSED(params);
    qDebug() << "Startup firmware plugin";
}

void FirmwareGen::shutdown()
{
}

QPointer<QQmlComponent> FirmwareGen::createView(QQmlEngine *engine, QObject *parent)
{
    QQmlComponent *qmlComponent = new QQmlComponent(engine, QUrl(QStringLiteral("qrc:/FirmwareGen/qml/FirmwareGenDialog.qml")), QQmlComponent::PreferSynchronous, parent);
    if (qmlComponent->isNull()) {
        qWarning() << "Qml component is null";
    }
    if (qmlComponent->isLoading()) {
        qWarning() << "Qml component still loading";
    }
    if (qmlComponent->isError()) {
        qWarning() << "Error while instantiating firmware gen dialog " << qmlComponent->errors();
    }
    if (!qmlComponent->isReady()) {
        qWarning() << "Qml component is not ready";
    }
    return qmlComponent;
}

void FirmwareGen::registerTypes(const char *uri)
{
    Q_ASSERT(uri == QStringLiteral("FirmwareGen"));
    // @uri FirmwareGen
    qmlRegisterType<NodesModel>(uri, 0, 1, "NodesModel");
    qmlRegisterType<Generator>(uri, 0, 1, "Generator");
}
