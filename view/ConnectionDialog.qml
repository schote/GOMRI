import QtQuick 2.0
import QtQuick.Controls 2.15

Item {

    Popup {
        id: colorThemePopup

        x: Math.round((parent.width)/2 - this.width/2)
        y: Math.round((parent.height)/2 - this.height/2)

        enter: Transition { NumberAnimation { property: "opacity"; from: 0.0; to: 1.0 } }
        exit: Transition { NumberAnimation { property: "opacity"; from: 1.0; to: 0.0 } }

        height: 100
        width: 150
    }

}
