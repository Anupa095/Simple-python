import sys
import psutil
from PyQt5 import QtWidgets, QtCore, QtGui

class PetWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Setup window
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint |
                            QtCore.Qt.Tool)  # tool so no taskbar
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Load images for different moods
        self.pix_idle = QtGui.QPixmap("pet_idle.png")  # idle image
        self.pix_busy = QtGui.QPixmap("pet_busy.png")  # busy/high CPU image
        
        self.current_pix = self.pix_idle
        
        # Timer to update
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)  # every 1 second
        
        # Set initial size and position
        self.resize(self.current_pix.size())
        self.move(100, 100)  # you can add dragging to reposition

    def update_status(self):
        cpu = psutil.cpu_percent(interval=None)
        if cpu > 50:
            self.current_pix = self.pix_busy
        else:
            self.current_pix = self.pix_idle
        self.repaint()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.current_pix)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # For example, open menu or do something
            print("Clicked pet!")

def main():
    app = QtWidgets.QApplication(sys.argv)
    pet = PetWidget()
    pet.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
