#ifndef NODESMODEL_H
#define NODESMODEL_H

#include <QStringListModel>
#include <QPointer>
#include <dataflowdiagram.h>
#include <datanode.h>

using namespace scivi::diagram;

class NodesModel: public QStringListModel
{
    Q_OBJECT
    Q_DISABLE_COPY(NodesModel)
    Q_PROPERTY(DataflowDiagram *diagram WRITE setDiagram READ diagram)
public:
    explicit NodesModel(QObject *parent = nullptr);
    virtual ~NodesModel() = default;
    enum Roles {
        NameRole = Qt::DisplayRole,
    };

    void setDiagram(DataflowDiagram* diagramObject);
    DataflowDiagram *diagram();

    // QAbstractItemModel interface
public:
    QHash<int, QByteArray> roleNames() const override;

protected:
    DataflowDiagram* m_diagram;
};

#endif // NODESMODEL_H
