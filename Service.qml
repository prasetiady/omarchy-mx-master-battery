import QtQuick
import Quickshell.Io

Item {
  id: root
  property var shell: null

  Process {
    id: indicator
    command: ["/usr/bin/python", decodeURIComponent(String(Qt.resolvedUrl("mx-master-battery-tray")).replace(/^file:\/\//, ""))]
    running: true
    onExited: restartTimer.restart()
  }

  Timer {
    id: restartTimer
    interval: 5000
    onTriggered: indicator.running = true
  }
}
