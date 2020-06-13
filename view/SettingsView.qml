import QtQuick 2.0
import QtQuick.Controls 2.15

Item {

    property string exampleText: "test"

    Rectangle {
        anchors.fill: parent
        color:  "darkslategray"

        Label {
            anchors.centerIn: parent
            text: qsTr(exampleText)
        }
    }
}


/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
