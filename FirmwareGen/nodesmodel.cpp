#include "nodesmodel.h"
#include <QDebug>
#include <QStringList>

#include <datanode.h>

NodesModel::NodesModel(QObject *parent): QStringListModel(parent)
{
}

void NodesModel::setDiagram(DataflowDiagram *diagramObject)
{
    this->m_diagram = diagramObject;
    QStringList nodeNames;
    auto nodes = diagramObject->nodes();
    for (const auto &node: nodes) {
        auto dataNode = qSharedPointerDynamicCast<DataNode>(node);
        if (dataNode != nullptr) {
            nodeNames << dataNode->name();
        }
    }
    setStringList(nodeNames);
}

DataflowDiagram *NodesModel::diagram()
{
    return m_diagram;
}

QHash<int, QByteArray> NodesModel::roleNames() const
{
    auto hash = QHash<int, QByteArray>();
    hash[NameRole] = "name";
    return hash;
}
