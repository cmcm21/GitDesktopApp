from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
import time


class CircularProgressBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(17, 17)
        self.setMaximumSize(17, 17)
        self.sign = 1
        self.value = 0

    def set_value(self, value):
        self.value = value
        self.update()

    def change_sign(self):
        self.sign *= -1

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        background_gradient = QLinearGradient(0, 0, self.width(), self.height())
        background_gradient.setColorAt(0, QColor("#999999"))
        background_gradient.setColorAt(1, QColor("#666666"))
        progress_gradient = QLinearGradient(0, 0, self.width(), self.height())
        progress_gradient.setColorAt(0, QColor("#008000"))
        progress_gradient.setColorAt(1, QColor("#00FF00"))

        # Outer circle
        outer_radius = min(self.width(), self.height()) / 2 - 10
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(background_gradient)
        painter.drawEllipse(self.rect().center(), outer_radius, outer_radius)

        # Progress arc
        painter.setBrush(progress_gradient)
        start_angle = 90 * 16  # 0 degrees is at 3 o'clock, so we start at 90 degrees
        span_angle = self.sign * self.value * 360 / 100 * 16  # Convert value to angle
        painter.drawPie(self.rect(), start_angle, span_angle)

        # Inner circle
        inner_radius = outer_radius
        painter.setBrush(QColor("#DDDDDD"))
        painter.drawEllipse(self.rect().center(), inner_radius, inner_radius)


class LoadingWidget(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__()
        self.showing = False

        layout = QVBoxLayout(self)
        label = QLabel("Loading...")
        label.setStyleSheet("background: transparent;")
        self.custom_parent = parent

        # Create the circular progress bar
        self.progress_bar = CircularProgressBar()
        layout.addWidget(label, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_bar, 0, Qt.AlignmentFlag.AlignCenter)

        self.progress_thread = None
        self.setStyleSheet(
            "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #000000, stop: 1 #333333);"
        )
        self.progress_thread = ProgressThread()
        self.progress_thread.progress_update.connect(self.progress_bar.set_value)
        self.progress_thread.change_sign.connect(self.progress_bar.change_sign)

    def show_anim_screen(self):
        if self.showing:
            return
        # Start the progress bar animation
        self.custom_parent.setDisabled(True)

        # To avoid circular import
        from View.LauncherWindow import LauncherWindow
        if isinstance(self.custom_parent, LauncherWindow):
            self.custom_parent.disable_window(True)
        else:
            self.custom_parent.setDisabled(True)
        self.progress_thread.start()
        self.progress_thread.set_run()
        self.showing = True
        self.show()

    def stop_anim_screen(self):
        if self.progress_thread is not None and self.progress_thread.isRunning():
            self.progress_thread.stop()

        self.showing = False

        # To avoid circular import
        from View.LauncherWindow import LauncherWindow
        if isinstance(self.custom_parent, LauncherWindow):
            self.custom_parent.disable_window(False)
        else:
            self.setDisabled(False)

        self.close()


class ProgressThread(QThread):
    progress_update = Signal(int)
    change_sign = Signal()
    running = True

    def set_run(self):
        self.running = True

    def run(self):
        progress_value = 0
        direction = 1

        # Start the progress bar animation
        while self.running:
            time.sleep(0.0075)
            progress_value += 1 * direction
            if progress_value > 100 or progress_value <= 0:
                direction *= -1
                self.change_sign.emit()
            self.progress_update.emit(progress_value)

    def stop(self):
        self.running = False
        self.wait()
        self.quit()
