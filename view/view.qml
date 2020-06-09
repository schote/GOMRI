import QtQuick 2.10
import QtQuick.Controls 2.1
import QtQuick.Window 2.2

ApplicationWindow {

    title: qsTr("GOMRI")
    width: 1600//Globals.windowWidth
    height: 900//Globals.windowHeight
    visible: true

    menuBar: ToolBar {
        id: toolbar
        width: parent.width
        height: 30

        Row {
            ToolButton {
                id: saveDataButton
                height: toolbar.height
                text: qsTr("Save Data")
            }
            ToolButton {
                id: saveFigureButton
                height: toolbar.height
                text: qsTr("Save Figure")
            }
        }
    }

    Column {

        anchors {
            top: toolbar.bottom
            bottom: parent.bottom
            left: parent.left
            right: parent.right
        }

        Row {
            id: plotSection
            anchors {
                left: parent.left
                right: parent.right
            }
            height: 0.5 * parent.height

            ImagePlotView {
                id: imagePlot
                anchors.left: parent.left
                implicitWidth: 0.5 * parent.width
                height: parent.height
            }

            SignalPlotView {
                id: spectrumPlot
                anchors.right: parent.right
                implicitWidth: 0.5 * parent.width
                height: parent.height
            }
        }

        SettingsView {
            id: settings
            anchors {
                top: plotSection.bottom
                bottom: parent.bottom
                left: parent.left
                right: parent.right
            }
        }
    }

}

/*##^##
Designer {
    D{i:8;invisible:true}D{i:9;invisible:true}
}
##^##*/
