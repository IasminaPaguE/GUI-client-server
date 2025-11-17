import sys

from PyQt6.QtWidgets import (
    QApplication, 
    QWidget,
    QHBoxLayout,
    QPushButton
)
app = QApplication([])
window = QWidget()
window.setWindowTitle("PyQt App")

layout = QHBoxLayout()
layout.addWidget(QPushButton("Left"))
layout.addWidget(QPushButton("center"))
layout.addWidget(QPushButton("left"))

window.setLayout(layout)
window.show()


sys.exit(app.exec())
