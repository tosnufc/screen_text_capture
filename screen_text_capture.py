import sys
import pytesseract
from PyQt5 import QtWidgets, QtGui, QtCore
import mss
from PIL import Image
import tempfile
import os

class SelectionWidget(QtWidgets.QLabel):
    def __init__(self, pixmap):
        super().__init__()
        self.setPixmap(pixmap)
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.selection_done = False
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowState(QtCore.Qt.WindowFullScreen)
        self.setCursor(QtCore.Qt.CrossCursor)
        self.rect = None

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.selection_done = True
        self.rect = QtCore.QRect(self.begin, self.end).normalized()
        self.close()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.begin and self.end:
            qp = QtGui.QPainter(self)
            qp.setPen(QtGui.QPen(QtGui.QColor('red'), 2))
            qp.setBrush(QtGui.QColor(255, 0, 0, 40))
            rect = QtCore.QRect(self.begin, self.end)
            qp.drawRect(rect)

    def get_rect(self):
        if self.rect:
            return self.rect.x(), self.rect.y(), self.rect.width(), self.rect.height()
        return None

def main():
    # 1. Capture the entire screen and save as a temp file
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Full screen
        sct_img = sct.grab(monitor)
        img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(tmpfile.name)
        tmpfile.close()

    # 2. Show the screenshot and let user select a region
    app = QtWidgets.QApplication(sys.argv)
    pixmap = QtGui.QPixmap(tmpfile.name)
    selector = SelectionWidget(pixmap)
    selector.show()
    app.exec_()
    if not selector.selection_done or not selector.get_rect():
        print("No region selected.")
        os.unlink(tmpfile.name)
        sys.exit(1)
    x, y, w, h = selector.get_rect()
    if w == 0 or h == 0:
        print("Invalid region selected.")
        os.unlink(tmpfile.name)
        sys.exit(1)

    # 3. Crop the selected region and run OCR
    img = Image.open(tmpfile.name)
    region = img.crop((x, y, x + w, y + h))
    text = pytesseract.image_to_string(region, lang='eng')
    print("Extracted Text:\n", text)

    # 4. Clean up the screenshot file
    os.unlink(tmpfile.name)

if __name__ == "__main__":
    main()
