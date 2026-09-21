"""
WiFi Analyzer Pro - Radar Visualization Widget
Renders an animated 360-degree radar scanner visualizing nearby WiFi networks
as spatial blips positioned radially by signal strength and distributed cleanly around 360°.
Low CPU usage (~30 FPS).
"""

import math
from typing import List, Optional, Tuple
from PySide6.QtWidgets import QWidget, QToolTip
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, Signal
from PySide6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QConicalGradient, QPainterPath
)

from app.models import WiFiNetwork


class RadarWidget(QWidget):
    """Animated circular radar screen plotting wireless networks."""

    network_selected = Signal(object)  # Emits selected WiFiNetwork

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._networks: List[WiFiNetwork] = []
        self._selected_bssid: Optional[str] = None
        self._hovered_network: Optional[WiFiNetwork] = None

        # Sweep animation angle (0 to 360 degrees)
        self._sweep_angle = 0.0
        self._animating = True

        # Timer for smooth 30 FPS sweep animation
        self._timer = QTimer(self)
        self._timer.setInterval(33)  # ~30 FPS
        self._timer.timeout.connect(self._on_animation_tick)
        self._timer.start()

        self.setMouseTracking(True)
        self.setStyleSheet("background-color: transparent;")

    def set_networks(self, networks: List[WiFiNetwork]):
        """Update networks plotted on radar."""
        self._networks = networks
        self.update()

    def set_selected_bssid(self, bssid: Optional[str]):
        self._selected_bssid = bssid.lower() if bssid else None
        self.update()

    def toggle_animation(self) -> bool:
        """Toggle animation on/off for zero-CPU mode."""
        self._animating = not self._animating
        if self._animating:
            self._timer.start()
        else:
            self._timer.stop()
            self.update()
        return self._animating

    def is_animating(self) -> bool:
        return self._animating

    def _on_animation_tick(self):
        self._sweep_angle = (self._sweep_angle + 2.0) % 360.0
        self.update()

    def _get_network_coords(self, net: WiFiNetwork, index: int, total: int, center_x: float, center_y: float, max_radius: float) -> Tuple[float, float, float]:
        """
        Compute (x, y, angle_deg) for a network blip.
        Evenly distributes angles across 360 degrees by stable BSSID sorting.
        Signal 100% -> radius near center (0.18 * max_radius)
        Signal 0%   -> radius near edge (0.90 * max_radius)
        """
        if total > 0:
            # Deterministic angular slot based on sorted BSSID order
            # This ensures smooth 360-degree spread without clustering
            angle_deg = (index * (360.0 / total) + 20.0) % 360.0
        else:
            angle_deg = 0.0

        clamped_sig = max(5, min(100, net.signal))
        norm_dist = 1.0 - (clamped_sig / 100.0)

        min_r = max_radius * 0.18
        r = min_r + norm_dist * (max_radius * 0.74)

        rad = math.radians(angle_deg - 90.0)  # 0 deg = North
        x = center_x + r * math.cos(rad)
        y = center_y + r * math.sin(rad)
        return x, y, angle_deg

    def mouseMoveEvent(self, event):
        pos = event.position()
        w = self.width()
        h = self.height()
        center_x = w / 2.0
        center_y = h / 2.0
        max_radius = min(center_x, center_y) - 25

        hovered = None
        total = len(self._networks)
        for i, net in enumerate(self._networks):
            nx, ny, _ = self._get_network_coords(net, i, total, center_x, center_y, max_radius)
            dist = math.hypot(pos.x() - nx, pos.y() - ny)
            if dist <= 14:
                hovered = net
                break

        if hovered != self._hovered_network:
            self._hovered_network = hovered
            self.update()
            if hovered:
                tip = (
                    f"<b>{hovered.ssid}</b><br/>"
                    f"Signal: {hovered.signal}% ({hovered.rssi_dbm} dBm)<br/>"
                    f"Band: {hovered.band} | Channel: {hovered.channel}<br/>"
                    f"BSSID: {hovered.bssid.upper()}<br/>"
                    f"Security: {hovered.auth}<br/>"
                    f"Vendor: {hovered.vendor}"
                )
                QToolTip.showText(event.globalPosition().toPoint(), tip, self)

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._hovered_network:
                self._selected_bssid = self._hovered_network.bssid.lower()
                self.network_selected.emit(self._hovered_network)
                self.update()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        center_x = w / 2.0
        center_y = h / 2.0
        max_radius = max(60.0, min(center_x, center_y) - 28.0)

        # 1. Background fill
        painter.fillRect(0, 0, w, h, QColor("#0B1017"))

        # Radar boundary disc
        painter.setPen(QPen(QColor("#152438"), 2))
        painter.setBrush(QColor("#0D1622"))
        painter.drawEllipse(QPointF(center_x, center_y), max_radius, max_radius)

        # 2. Concentric Radar Rings
        ring_fractions = [0.25, 0.50, 0.75, 1.0]
        ring_labels = ["-50 dBm (100%)", "-65 dBm (75%)", "-75 dBm (50%)", "-90 dBm (25%)"]

        painter.setFont(QFont("Segoe UI", 8))
        for i, frac in enumerate(ring_fractions):
            r = max_radius * frac
            painter.setPen(QPen(QColor("#1C3149"), 1, Qt.DashLine if frac < 1.0 else Qt.SolidLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(center_x, center_y), r, r)

            # Ring distance indicator label on North axis
            painter.setPen(QColor("#486581"))
            painter.drawText(int(center_x + 6), int(center_y - r + 13), ring_labels[3 - i])

        # 3. Crosshairs
        painter.setPen(QPen(QColor("#1A2D42"), 1))
        painter.drawLine(int(center_x - max_radius), int(center_y), int(center_x + max_radius), int(center_y))
        painter.drawLine(int(center_x), int(center_y - max_radius), int(center_x), int(center_y + max_radius))

        # Diagonals
        diag_len = max_radius * 0.7071
        painter.setPen(QPen(QColor("#142233"), 1, Qt.DotLine))
        painter.drawLine(int(center_x - diag_len), int(center_y - diag_len), int(center_x + diag_len), int(center_y + diag_len))
        painter.drawLine(int(center_x - diag_len), int(center_y + diag_len), int(center_x + diag_len), int(center_y - diag_len))

        # Cardinal Direction Markers
        font_cardinal = QFont("Segoe UI", 9, QFont.Bold)
        painter.setFont(font_cardinal)
        painter.setPen(QColor("#627D98"))
        painter.drawText(QRectF(center_x - 15, center_y - max_radius - 22, 30, 20), Qt.AlignCenter, "N")
        painter.drawText(QRectF(center_x + max_radius + 6, center_y - 10, 20, 20), Qt.AlignCenter, "E")
        painter.drawText(QRectF(center_x - 15, center_y + max_radius + 4, 30, 20), Qt.AlignCenter, "S")
        painter.drawText(QRectF(center_x - max_radius - 26, center_y - 10, 20, 20), Qt.AlignCenter, "W")

        # 4. Animated Rotating Radar Sweep Beam
        if self._animating:
            sweep_path = QPainterPath()
            sweep_path.moveTo(center_x, center_y)
            sweep_rect = QRectF(center_x - max_radius, center_y - max_radius, max_radius * 2, max_radius * 2)
            start_angle = 90.0 - self._sweep_angle
            sweep_path.arcTo(sweep_rect, start_angle, 40.0)
            sweep_path.closeSubpath()

            conical = QConicalGradient(center_x, center_y, self._sweep_angle - 90)
            conical.setColorAt(0.0, QColor(0, 210, 255, 110))
            conical.setColorAt(0.12, QColor(0, 210, 255, 30))
            conical.setColorAt(0.2, QColor(0, 210, 255, 0))
            conical.setColorAt(1.0, QColor(0, 210, 255, 0))

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(conical))
            painter.drawPath(sweep_path)

            # Leading beam line
            rad_lead = math.radians(self._sweep_angle - 90)
            lead_x = center_x + max_radius * math.cos(rad_lead)
            lead_y = center_y + max_radius * math.sin(rad_lead)
            painter.setPen(QPen(QColor("#00FFFF"), 1.8))
            painter.drawLine(QPointF(center_x, center_y), QPointF(lead_x, lead_y))

        # 5. Network Blips & Labels
        font_blip = QFont("Segoe UI", 8)
        painter.setFont(font_blip)
        total = len(self._networks)

        for i, net in enumerate(self._networks):
            nx, ny, angle_deg = self._get_network_coords(net, i, total, center_x, center_y, max_radius)
            is_selected = (self._selected_bssid == net.bssid.lower())
            is_hovered = (self._hovered_network == net)

            # Color by band
            if net.band == "5 GHz":
                base_color = QColor("#00E5FF")  # Cyan
            elif net.band == "6 GHz":
                base_color = QColor("#D500F9")  # Purple
            elif net.band == "2.4 GHz":
                base_color = QColor("#FFA726")  # Amber
            else:
                base_color = QColor("#94A3B8")  # Gray

            diff = (self._sweep_angle - angle_deg) % 360
            is_lit_by_sweep = self._animating and (diff < 35.0)

            # Outer glow / halo
            if is_selected:
                painter.setPen(QPen(QColor("#FFFFFF"), 2))
                painter.setBrush(QColor(base_color.red(), base_color.green(), base_color.blue(), 70))
                painter.drawEllipse(QPointF(nx, ny), 12, 12)
            elif is_hovered or is_lit_by_sweep:
                alpha = int(80 * (1.0 - diff / 35.0)) if is_lit_by_sweep else 70
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(base_color.red(), base_color.green(), base_color.blue(), alpha))
                painter.drawEllipse(QPointF(nx, ny), 10, 10)

            # Dot
            dot_radius = 5.0 if not is_selected else 6.5
            painter.setPen(QPen(QColor("#FFFFFF"), 1.2))
            painter.setBrush(base_color)
            painter.drawEllipse(QPointF(nx, ny), dot_radius, dot_radius)

            # Label tag (SSID + %)
            clean_name = net.ssid if len(net.ssid) <= 12 else net.ssid[:10] + ".."
            label_text = f"{clean_name} ({net.signal}%)"

            # Determine label position to avoid clipping
            offset_x = 8 if nx <= center_x else -86
            offset_y = -6 if ny <= center_y else 14
            label_x = nx + offset_x
            label_y = ny + offset_y

            # Text background badge for readability
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(11, 16, 23, 210))
            painter.drawRoundedRect(QRectF(label_x - 3, label_y - 11, 88, 15), 3, 3)

            painter.setPen(QColor("#FFFFFF") if (is_selected or is_hovered) else QColor("#CBD5E1"))
            painter.drawText(int(label_x), int(label_y), label_text)

        # 6. Center Hub Icon / Dot
        painter.setPen(QPen(QColor("#00D2FF"), 2))
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawEllipse(QPointF(center_x, center_y), 4, 4)
