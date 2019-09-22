#ifndef FIRMWAREGEN_H
#define FIRMWAREGEN_H

#include "firmwaregen_global.h"
#include <QObject>
#include <QProcess>
#include <datanode.h>
#include <dataflowdiagram.h>
#include <plugin.h>
#include <QQmlExtensionPlugin>
#include "generator.h"

using namespace scivi::diagram;
using namespace scivi;

class FIRMWAREGEN_EXPORT FirmwareGen: public QQmlExtensionPlugin, public Plugin
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID Plugin_iid)
    Q_PLUGIN_METADATA(IID QQmlExtensionInterface_iid)
    Q_INTERFACES(scivi::Plugin)
public:
    explicit FirmwareGen(QObject *parent = nullptr);
    virtual ~FirmwareGen() override;

    // Plugin interface
public:
    QString name() const override;
    void initialize(Plugin::IntializeParams) override;
    void startup(Plugin::StartupParams) override;
    void shutdown() override;
    QPointer<QQmlComponent> createView(QQmlEngine *engine, QObject *parent = nullptr) override;

    // QQmlTypesExtensionInterface interface
public:
    void registerTypes(const char *uri) override;
};

#endif // FIRMWAREGEN_H
