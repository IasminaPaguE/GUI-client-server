import sys

from PyQt6.QtWidgets import(
    QApplication,
    QLayout,
    QVBoxLayout,
    QWidget,
    QPushButton
)

app = QApplication([])
window = QWidget()
window.setWindowTitle("Application using QVBoxLayout")

layout = QVBoxLayout()
layout.addWidget(QPushButton("top"))
layout.addWidget(QPushButton("center"))
layout.addWidget(QPushButton("bottom"))

window.setLayout(layout)

window.show()
sys.exit(app.exec())




