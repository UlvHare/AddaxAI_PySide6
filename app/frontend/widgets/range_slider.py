# frontend/widgets/range_slider.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QRect, QSize, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient

class RangeSlider(QWidget):
    """Custom Range Slider widget for selecting value ranges."""

    # Signals for value changes
    valueChanged = Signal(float, float)  # min, max
    sliderReleased = Signal()

    def __init__(self, parent=None, min_value=0.0, max_value=1.0, start_min=0.2, start_max=0.8):
        """Initialize the range slider.

        Args:
            parent: Parent widget
            min_value: Minimum possible value
            max_value: Maximum possible value
            start_min: Initial minimum selected value
            start_max: Initial maximum selected value
        """
        super().__init__(parent)

        # Set fixed height for the slider
        self.setMinimumHeight(40)
        self.setMaximumHeight(40)

        # Initialize variables
        self.min_value = min_value
        self.max_value = max_value
        self.min_pos = start_min
        self.max_pos = start_max

        # UI styling parameters
        self.handle_radius = 10
        self.bar_height = 6
        self.margin = 5

        # Handle being dragged
        self.min_handle_dragged = False
        self.max_handle_dragged = False

        # Set focus policy for keyboard navigation
        self.setFocusPolicy(Qt.ClickFocus)

        # Enable mouse tracking
        self.setMouseTracking(True)

    def sizeHint(self):
        """Return the recommended size for this widget."""
        return QSize(300, 40)

    def paintEvent(self, event):
        """Paint the range slider widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Widget dimensions
        width = self.width()
        height = self.height()

        # Calculate drawing positions
        bar_y = height // 2 - self.bar_height // 2
        slider_width = width - 2 * self.margin - 2 * self.handle_radius
        slider_start_x = self.margin + self.handle_radius

        # Calculate handle positions in pixel coordinates
        min_handle_x = slider_start_x + (self.min_pos - self.min_value) / (self.max_value - self.min_value) * slider_width
        max_handle_x = slider_start_x + (self.max_pos - self.min_value) / (self.max_value - self.min_value) * slider_width

        # Draw inactive part of the slider (background)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(200, 200, 200)))
        painter.drawRoundedRect(slider_start_x, bar_y, slider_width, self.bar_height, 3, 3)

        # Draw active part of the slider
        active_start = min_handle_x
        active_width = max_handle_x - min_handle_x

        # Create gradient for active part
        gradient = QLinearGradient(active_start, bar_y, active_start + active_width, bar_y)
        gradient.setColorAt(0, QColor(0, 122, 204))
        gradient.setColorAt(1, QColor(0, 188, 212))

        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(active_start, bar_y, active_width, self.bar_height, 3, 3)

        # Draw minimum handle
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(QColor(0, 122, 204), 2))
        painter.drawEllipse(QPoint(int(min_handle_x), height // 2), self.handle_radius, self.handle_radius)

        # Draw maximum handle
        painter.drawEllipse(QPoint(int(max_handle_x), height // 2), self.handle_radius, self.handle_radius)

    def mousePressEvent(self, event):
        """Handle mouse press event to start dragging handles."""
        if event.button() == Qt.LeftButton:
            width = self.width()
            height = self.height()
            slider_width = width - 2 * self.margin - 2 * self.handle_radius
            slider_start_x = self.margin + self.handle_radius

            # Calculate handle positions in pixel coordinates
            min_handle_x = slider_start_x + (self.min_pos - self.min_value) / (self.max_value - self.min_value) * slider_width
            max_handle_x = slider_start_x + (self.max_pos - self.min_value) / (self.max_value - self.min_value) * slider_width

            # Check if clicking on handles
            min_handle_rect = QRect(int(min_handle_x) - self.handle_radius, height // 2 - self.handle_radius,
                                    2 * self.handle_radius, 2 * self.handle_radius)
            max_handle_rect = QRect(int(max_handle_x) - self.handle_radius, height // 2 - self.handle_radius,
                                    2 * self.handle_radius, 2 * self.handle_radius)

            if min_handle_rect.contains(event.pos()):
                self.min_handle_dragged = True
            elif max_handle_rect.contains(event.pos()):
                self.max_handle_dragged = True
            else:
                # Check if clicking on bar
                bar_rect = QRect(slider_start_x, height // 2 - self.bar_height // 2,
                                slider_width, self.bar_height)

                if bar_rect.contains(event.pos()):
                    # Determine which handle to move based on proximity
                    click_pos = (event.pos().x() - slider_start_x) / slider_width
                    click_val = self.min_value + click_pos * (self.max_value - self.min_value)

                    if abs(click_val - self.min_pos) < abs(click_val - self.max_pos):
                        self.min_handle_dragged = True
                        # Move the handle to the click position
                        self.min_pos = max(self.min_value, min(click_val, self.max_pos - 0.01))
                    else:
                        self.max_handle_dragged = True
                        # Move the handle to the click position
                        self.max_pos = min(self.max_value, max(click_val, self.min_pos + 0.01))

                    self.update()
                    self.valueChanged.emit(self.min_pos, self.max_pos)

    def mouseMoveEvent(self, event):
        """Handle mouse move event to update handle positions during drag."""
        if self.min_handle_dragged or self.max_handle_dragged:
            width = self.width()
            slider_width = width - 2 * self.margin - 2 * self.handle_radius
            slider_start_x = self.margin + self.handle_radius

            # Calculate value from pixel position
            click_pos = (event.pos().x() - slider_start_x) / slider_width
            click_val = self.min_value + click_pos * (self.max_value - self.min_value)

            if self.min_handle_dragged:
                # Ensure min_pos doesn't exceed max_pos
                self.min_pos = max(self.min_value, min(click_val, self.max_pos - 0.01))
            elif self.max_handle_dragged:
                # Ensure max_pos doesn't go below min_pos
                self.max_pos = min(self.max_value, max(click_val, self.min_pos + 0.01))

            self.update()
            self.valueChanged.emit(self.min_pos, self.max_pos)

    def mouseReleaseEvent(self, event):
        """Handle mouse release event to stop handle dragging."""
        if event.button() == Qt.LeftButton:
            if self.min_handle_dragged or self.max_handle_dragged:
                self.min_handle_dragged = False
                self.max_handle_dragged = False
                self.sliderReleased.emit()

    def get_values(self):
        """Get the current minimum and maximum values.

        Returns:
            Tuple of (min_value, max_value)
        """
        return (self.min_pos, self.max_pos)

    def set_values(self, min_val, max_val):
        """Set the current minimum and maximum values.

        Args:
            min_val: Minimum value
            max_val: Maximum value
        """
        # Ensure values are within range and min < max
        min_val = max(self.min_value, min(min_val, self.max_value))
        max_val = max(self.min_value, min(max_val, self.max_value))

        if min_val >= max_val:
            max_val = min_val + 0.01

        self.min_pos = min_val
        self.max_pos = max_val
        self.update()
        self.valueChanged.emit(self.min_pos, self.max_pos)
