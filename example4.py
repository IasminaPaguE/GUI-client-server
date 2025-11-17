import sys

from PyQt6.QtWidgets import(
    QApplication,
    QWidget,
    QGridLayout,
    QPushButton
)

app = QApplication([])


window = QWidget()
window.setWindowTitle("App using QGridLayout")

layout = QGridLayout()
layout.addWidget(QPushButton("B00"),0,0)
layout.addWidget(QPushButton("B01"), 0,1)
layout.addWidget(QPushButton("B02"),0,2)
layout.addWidget(QPushButton("B10"), 1,0)
layout.addWidget(QPushButton("B111"),1,1)
layout.addWidget(QPushButton("B12"), 1,2)
layout.addWidget(QPushButton("B20"),2,0)
layout.addWidget(QPushButton("B21"), 2,1)
layout.addWidget(QPushButton("B22"),2,2)

window.setLayout(layout)
window.show()

sys.exit(app.exec())




