"""
WiFi Analyzer Pro - Signal Strength Visualization
Presents a graphical horizontal bar chart of discovered WiFi networks and signal strengths,
with quality gradients, dBm indicators, interactive hovering, and selection highlighting.
"""

from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QToolTip
)
from PySide6.QtCore import Qt, QRectF, QSize, Signal, QPoint
from PySide6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QLinearGradient, QFontMetrics
)

from app.models import WiFiNetwork


class SignalChartCanvas(QWidget):
    """Custom painted canvas rendering horizontal signal strength bars."""

    network_selected = Signal(object)  # Emits selected WiFiNetwork

    BAR_HEIGHT = 28
    ROW_SPACING = 14
    TOP_PADDING = 20
    BOTTOM_PADDING = 20
    LEFT_LABEL_WIDTH = 220
    RIGHT_LABEL_WIDTH = 130

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._networks: List[WiFiNetwork] = []
        self._selected_bssid: Optional[str] = None
        self._hovered_index: Optional[int] = None

        self.setMouseTracking(True)
        self.setStyleSheet("background-color: transparent;")

    def set_networks(self, networks: List[WiFiNetwork]):
        """Update networks and resize canvas to fit all rows."""
        # Sort descending by signal
        self._networks = sorted(networks, key=lambda n: n.signal, reverse=True)
        total_rows = len(self._networks)
        required_height = self.TOP_PADDING + total_rows * (self.BAR_HEIGHT + self.ROW_SPACING) + self.BOTTOM_PADDING
        self.setMinimumHeight(max(300, required_height))
        self.update()

    def set_selected_bssid(self, bssid: Optional[str]):
        self._selected_bssid = bssid.lower() if bssid else None
        self.update()

    def sizeHint(self) -> QSize:
        total_rows = len(self._networks)
        h = self.TOP_PADDING + total_rows * (self.BAR_HEIGHT + self.ROW_SPACING) + self.BOTTOM_PADDING
        return QSize(600, max(350, h))

    def mouseMoveEvent(self, event):
        y = event.position().y()
        index = self._get_row_at_y(y)
        if index != self._hovered_index:
            self._hovered_index = index
            self.update()
            if index is not None and 0 <= index < len(self._networks):
                net = self._networks[index]
                tip_text = (
                    f"<b>{net.ssid}</b><br/>"
                    f"BSSID: {net.bssid.upper()}<br/>"
                    f"Signal: {net.signal}% ({net.rssi_dbm} dBm)<br/>"
                    f"Band: {net.band} (Channel {net.channel})<br/>"
                    f"Security: {net.auth} ({net.encryption})<br/>"
                    f"Vendor: {net.vendor}"
                )
                QToolTip.showText(event.globalPosition().toPoint(), tip_text, self)
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self._hovered_index = None
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            index = self._get_row_at_y(event.position().y())
            if index is not None and 0 <= index < len(self._networks):
                net = self._networks[index]
                self._selected_bssid = net.bssid.lower()
                self.network_selected.emit(net)
                self.update()
        super().mousePressEvent(event)

    def _get_row_at_y(self, y: float) -> Optional[int]:
        if not self._networks:
            return None
        rel_y = y - self.TOP_PADDING
        if rel_y < 0:
            return None
        row = int(rel_y // (self.BAR_HEIGHT + self.ROW_SPACING))
        if 0 <= row < len(self._networks):
            # Check if within bar height
            in_row_y = rel_y % (self.BAR_HEIGHT + self.ROW_SPACING)
            if in_row_y <= self.BAR_HEIGHT:
                return row
        return None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Background
        painter.fillRect(0, 0, w, h, QColor("#0F141C"))

        if not self._networks:
            # Draw placeholder message
            painter.setPen(QColor("#64748B"))
            font = QFont("Segoe UI", 12)
            painter.setFont(font)
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "No WiFi networks discovered yet.\nClick SCAN to analyze nearby signals.")
            return

        # Bar chart area
        bar_left = self.LEFT_LABEL_WIDTH
        bar_right = w - self.RIGHT_LABEL_WIDTH
        max_bar_width = max(100.0, bar_right - bar_left)

        # Draw vertical grid lines (25%, 50%, 75%, 100%)
        painter.setPen(QPen(QColor("#1A2332"), 1, Qt.DashLine))
        grid_font = QFont("Segoe UI", 9)
        painter.setFont(grid_font)

        for pct in (25, 50, 75, 100):
            gx = bar_left + (pct / 100.0) * max_bar_width
            painter.drawLine(int(gx), self.TOP_PADDING - 5, int(gx), h - self.BOTTOM_PADDING)

        # Fonts
        font_ssid = QFont("Segoe UI", 10, QFont.Bold)
        font_sub = QFont("Segoe UI", 8)
        font_meter = QFont("Segoe UI", 9, QFont.Bold)
        fm_ssid = QFontMetrics(font_ssid)

        for i, net in enumerate(self._networks):
            y = self.TOP_PADDING + i * (self.BAR_HEIGHT + self.ROW_SPACING)
            is_selected = (self._selected_bssid == net.bssid.lower())
            is_hovered = (self._hovered_index == i)

            # Highlight row background if selected
            if is_selected:
                row_highlight = QRectF(8, y - 4, w - 16, self.BAR_HEIGHT + 8)
                painter.setPen(QPen(QColor("#00D2FF"), 1.5))
                painter.setBrush(QColor("#162335"))
                painter.drawRoundedRect(row_highlight, 6, 6)
            elif is_hovered:
                row_highlight = QRectF(8, y - 4, w - 16, self.BAR_HEIGHT + 8)
                painter.setPen(QPen(QColor("#25364E"), 1))
                painter.setBrush(QColor("#141C28"))
                painter.drawRoundedRect(row_highlight, 6, 6)

            # 1. Left Label: SSID & Band badge
            # Band badge pill
            band_text = "5G" if "5" in net.band else ("2.4G" if "2.4" in net.band else "?")
            badge_color = QColor("#38BDF8") if "5" in net.band else (QColor("#FFA726") if "2.4" in net.band else QColor("#94A3B8"))
            badge_rect = QRectF(16, y + 4, 34, 18)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(badge_color.red(), badge_color.green(), badge_color.blue(), 30))
            painter.drawRoundedRect(badge_rect, 4, 4)

            painter.setPen(badge_color)
            painter.setFont(font_sub)
            painter.drawText(badge_rect, Qt.AlignCenter, band_text)

            # SSID Text
            ssid_rect = QRectF(56, y + 2, self.LEFT_LABEL_WIDTH - 64, self.BAR_HEIGHT - 4)
            painter.setFont(font_ssid)
            painter.setPen(QColor("#FFFFFF") if not net.is_hidden else QColor("#94A3B8"))
            elided_ssid = fm_ssid.elidedText(net.ssid, Qt.ElideRight, int(ssid_rect.width()))
            painter.drawText(ssid_rect, Qt.AlignVCenter | Qt.AlignLeft, elided_ssid)

            # 2. Horizontal Bar Track (Background)
            track_rect = QRectF(bar_left, y + 4, max_bar_width, self.BAR_HEIGHT - 8)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#161F2E"))
            painter.drawRoundedRect(track_rect, 5, 5)

            # 3. Horizontal Filled Gradient Bar
            sig_pct = max(2, min(100, net.signal))
            fill_width = (sig_pct / 100.0) * max_bar_width
            fill_rect = QRectF(bar_left, y + 4, fill_width, self.BAR_HEIGHT - 8)

            # Choose linear gradient based on signal tier
            gradient = QLinearGradient(bar_left, 0, bar_left + fill_width, 0)
            if net.signal >= 75:
                gradient.setColorAt(0.0, QColor("#00F2FE"))
                gradient.setColorAt(1.0, QColor("#4FACFE"))
            elif net.signal >= 50:
                gradient.setColorAt(0.0, QColor("#38EF7D"))
                gradient.setColorAt(1.0, QColor("#11998E"))
            elif net.signal >= 30:
                gradient.setColorAt(0.0, QColor("#F6D365"))
                gradient.setColorAt(1.0, QColor("#FDA085"))
            else:
                gradient.setColorAt(0.0, QColor("#FF416C"))
                gradient.setColorAt(1.0, QColor("#FF4B2B"))

            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(fill_rect, 5, 5)

            # 4. Right Label (Signal % and RSSI dBm)
            right_rect = QRectF(bar_right + 12, y + 2, self.RIGHT_LABEL_WIDTH - 16, self.BAR_HEIGHT - 4)
            painter.setFont(font_meter)

            # Text color matches tier
            if net.signal >= 75:
                painter.setPen(QColor("#38EF7D"))
            elif net.signal >= 50:
                painter.setPen(QColor("#00D2FF"))
            elif net.signal >= 30:
                painter.setPen(QColor("#FFA726"))
            else:
                painter.setPen(QColor("#EF4444"))

            metric_str = f"{net.signal}%  ({net.rssi_dbm} dBm)"
            painter.drawText(right_rect, Qt.AlignVCenter | Qt.AlignLeft, metric_str)


class SignalChartWidget(QWidget):
    """Scrollable container wrapper around SignalChartCanvas."""

    network_selected = Signal(object)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #0F141C;
                border: 1px solid #232E40;
                border-radius: 8px;
            }
        """)

        self.canvas = SignalChartCanvas()
        self.canvas.network_selected.connect(self.network_selected.emit)
        self.scroll_area.setWidget(self.canvas)

        layout.addWidget(self.scroll_area)

    def set_networks(self, networks: List[WiFiNetwork]):
        self.canvas.set_networks(networks)

    def select_network(self, bssid: str):
        self.canvas.set_selected_bssid(bssid)
