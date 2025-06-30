import sys
import pytesseract
from PyQt5 import QtWidgets, QtGui, QtCore
import mss
from PIL import Image
import tempfile
import os
import subprocess

class SelectionWidget(QtWidgets.QWidget):
    def __init__(self, image_path, monitor_info):
        super().__init__()
        self.image_path = image_path
        self.monitor_info = monitor_info
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.selection_done = False
        self.rect = None
        
        # Load and display the image
        self.pixmap = QtGui.QPixmap(image_path)
        
        # Set up the window to cover the specific monitor
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setGeometry(monitor_info['left'], monitor_info['top'], 
                        monitor_info['width'], monitor_info['height'])
        self.setCursor(QtCore.Qt.CrossCursor)
        
        # Set background to show the screenshot
        self.setAutoFillBackground(True)

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
        painter = QtGui.QPainter(self)
        
        # Draw the screenshot as background
        painter.drawPixmap(0, 0, self.width(), self.height(), self.pixmap)
        
        # Draw selection rectangle if dragging
        if self.begin and self.end:
            painter.setPen(QtGui.QPen(QtGui.QColor('red'), 2))
            painter.setBrush(QtGui.QColor(255, 0, 0, 40))
            rect = QtCore.QRect(self.begin, self.end)
            painter.drawRect(rect)

    def get_rect(self):
        if self.rect:
            # Scale coordinates based on the actual image size vs display size
            scale_x = self.pixmap.width() / self.width()
            scale_y = self.pixmap.height() / self.height()
            
            x = int(self.rect.x() * scale_x)
            y = int(self.rect.y() * scale_y)
            w = int(self.rect.width() * scale_x)
            h = int(self.rect.height() * scale_y)
            
            return x, y, w, h
        return None

    def keyPressEvent(self, event):
        # Allow ESC to cancel
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

def get_mouse_position():
    """Get the current mouse cursor position using xdotool."""
    try:
        result = subprocess.run(['xdotool', 'getmouselocation'], 
                              capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        # Parse output like "x:1920 y:1080 screen:0 window:12345"
        parts = output.split()
        x = int(parts[0].split(':')[1])
        y = int(parts[1].split(':')[1])
        return x, y
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError, ValueError):
        # Fallback: use PyQt5 to get cursor position
        cursor_pos = QtGui.QCursor.pos()
        return cursor_pos.x(), cursor_pos.y()

def find_monitor_with_cursor(monitors):
    """Find which monitor contains the mouse cursor."""
    mouse_x, mouse_y = get_mouse_position()
    
    for monitor in monitors:
        if monitor['width'] == 0 or monitor['height'] == 0:
            continue
            
        left = monitor['left']
        top = monitor['top']
        right = left + monitor['width']
        bottom = top + monitor['height']
        
        if left <= mouse_x < right and top <= mouse_y < bottom:
            return monitor
    
    # Fallback: return the first valid monitor
    for monitor in monitors:
        if monitor['width'] > 0 and monitor['height'] > 0:
            return monitor
    
    return None

def main():
    # 1. Capture the screen of the monitor containing the mouse cursor
    with mss.mss() as sct:
        # Find the monitor that contains the mouse cursor
        monitor = find_monitor_with_cursor(sct.monitors)
        
        if not monitor:
            print("Error: No valid monitor found!")
            sys.exit(1)
        
        print(f"Capturing monitor: {monitor['width']}x{monitor['height']} at ({monitor['left']}, {monitor['top']})")
            
        sct_img = sct.grab(monitor)
        img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(tmpfile.name)
        tmpfile.close()

    # 2. Show the screenshot and let user select a region
    app = QtWidgets.QApplication(sys.argv)
    
    # Create selection widget
    selector = SelectionWidget(tmpfile.name, monitor)
    selector.show()
    
    # Run the application
    app.exec_()
    
    # Check if selection was made
    if not selector.selection_done or not selector.get_rect():
        print("No region selected.")
        os.unlink(tmpfile.name)
        sys.exit(1)
        
    x, y, w, h = selector.get_rect()
    if w == 0 or h == 0:
        print("Invalid region selected.")
        os.unlink(tmpfile.name)
        sys.exit(1)

    print(f"Selected region: {x}, {y}, {w}, {h}")

    # 3. Crop the selected region and run OCR
    img = Image.open(tmpfile.name)
    region = img.crop((x, y, x + w, y + h))
    text = pytesseract.image_to_string(region, lang='eng')
    print("Extracted Text:\n", text)

    # 4. Clean up the screenshot file
    os.unlink(tmpfile.name)

    # 5. Copy text to clipboard
    try:
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(text)
        print("Text copied to clipboard.")
    except:
        print("Could not copy to clipboard, but text extraction completed.")

if __name__ == "__main__":
    main()
 