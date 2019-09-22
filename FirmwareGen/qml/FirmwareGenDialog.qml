import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2
import QtQuick.Controls 2.5
import Qt.labs.platform 1.0 as Platforms
import FirmwareGen 0.1

Item {
    anchors.fill: parent
    anchors.margins: 8

    NodesModel {
        id: nodesModel
    }

    Generator {
        id: firmwareGenerator
    }

    Page {
        anchors.left: parent.left
        anchors.right: parent.right

        header: Label {
            text: qsTr("Firmware generation from dataflow diagram")
        }

        contentItem: GridLayout {
           anchors.margins: 8
           columns: 3

           Label {
               text: "Host"
           }
           ComboBox {
               id: dataNodesComboBox
               Layout.fillWidth: true
               Layout.columnSpan: 2
               textRole: 'name'
               model: nodesModel
           }
           Label {
               text: "Path to save"
           }
           TextField {
               id: outputField
               selectByMouse: true
               Layout.preferredWidth: 300
           }
           Button {
               Layout.preferredWidth: 30
               text: "..."
               onClicked: outputFileDialog.open()
               Platforms.FileDialog {
                   id: outputFileDialog
                   fileMode: Platforms.FileDialog.SaveFile
                   folder: 'file://' + outputField.text
                   onAccepted: {
                       var path = outputFileDialog.file.toString();
                       path = path.replace(/^(file:\/{2})/,"");
                       outputField.text = decodeURIComponent(path);
                   }
               }
           }
       }

        Button {
            text: qsTr("Generate")
            onClicked: {
                if (dataNodesComboBox.currentIndex != -1 && outputField.text !== "")
                    firmwareGenerator.generate(dataNodesComboBox.currentText, nodesModel.diagram, outputField.text)
            }
        }

        Component.onCompleted: {
            outputField.text = appPath + '/firmware.ino';
            nodesModel.diagram = diagram // Global diagram property passed with creation context
        }
    }
}
