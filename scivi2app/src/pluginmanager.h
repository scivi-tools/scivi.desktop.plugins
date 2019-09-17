#ifndef PLUGINMANAGER_H
#define PLUGINMANAGER_H

#include <QDir>
#include <QList>
#include <QObject>
#include <QPointer>
#include <QString>

#include "editor/editor.h"
#include "plugin/pluginmodel.h"

namespace scivi {

class Plugin;

class PluginManager : public QObject {
    Q_OBJECT
    Q_PROPERTY(QObject *pluginModel READ pluginModel NOTIFY pluginModelChanged)
    Q_PROPERTY(QQuickItem *pluginContainer WRITE setPluginContainer)
public:
    PluginManager(Editor *editor, QQmlEngine *engine,
                  QObject *parent = nullptr);
    void initialize(QDir baseDir);

    void registerPlugin(Plugin *plugin, QString dir);
    QList<Plugin *> plugins() const;
    QObject *pluginModel();
    Q_INVOKABLE QQuickItem *runPluginWithName(QString name);
    void setPluginContainer(QQuickItem *container);

    static Plugin *load(QString pathToPlugin);
    static QList<Plugin *> findPluginsInDir(QDir dir);

signals:
    void pluginModelChanged();

private:
    PluginModel m_pluginModel;
    Editor *m_editor;
    QQmlEngine *m_engine;
    QQuickItem *m_pluginContainer;
};

}  // namespace scivi

#endif  // PLUGINMANAGER_H
