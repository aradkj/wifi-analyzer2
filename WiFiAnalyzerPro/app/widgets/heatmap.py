"""
WiFi Analyzer Pro - Channel Heatmap & Spectral Visualizer
Renders channel frequency distributions, spectral bell curves for 2.4 GHz and 5 GHz,
and calculates channel congestion ratings to help users optimize channel selection.
"""

from typing import List, Optional, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QToolTip, QButtonGroup
)
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QLinearGradient, QPainterPath
)

from app.models import WiFiNetwork


# Common 5 GHz channel list
CHANNELS_5GHZ = [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 149, 153, 157, 161, 165]


class ChannelSpectrumCanvas(QWidget):
    """Paints spectral bell curves representing WiFi channel occupancy."""

    network_selected = Signal(object)

    PALETTE = [
        QColor("#00D2FF"), QColor("#38EF7D"), QColor("#FFA726"),
        QColor("#C084FC"), QColor("#F43F5E"), QColor("#38BDF8"),
        QColor("#34D399"), QColor("#FBBF24"), QColor("#818CF8"),
        QColor("#FB7185"), QColor("#2DD4BF"), QColor("#E879F9")
    ]

    MARGIN_LEFT = 105.0
    MARGIN_RIGHT = 35.0
    MARGIN_BOTTOM = 65.0
    MARGIN_TOP = 40.0

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._networks: List[WiFiNetwork] = []
        self._selected_bssid: Optional[str] = None
        self._hovered_network: Optional[WiFiNetwork] = None
        self._active_band = "2.4 GHz"  # '2.4 GHz' or '5 GHz'

        self.setMouseTracking(True)
        self.setStyleSheet("background-color: transparent;")

    def set_networks(self, networks: List[WiFiNetwork]):
        self._networks = networks
        self.update()

    def set_active_band(self, band: str):
        self._active_band = band
        self.update()

    def set_selected_bssid(self, bssid: Optional[str]):
        self._selected_bssid = bssid.lower() if bssid else None
        self.update()

    def mouseMoveEvent(self, event):
        pos = event.position()
        w = self.width()
        h = self.height()

        graph_w = w - self.MARGIN_LEFT - self.MARGIN_RIGHT
        graph_h = h - self.MARGIN_TOP - self.MARGIN_BOTTOM

        matching_nets = [n for n in self._networks if n.band == self._active_band and n.channel > 0]
        hovered = None

        for net in matching_nets:
            px, py = self._get_peak_coords(net, self.MARGIN_LEFT, graph_w, self.MARGIN_TOP, graph_h)
            dist_x = abs(pos.x() - px)
            if dist_x <= 35 and pos.y() >= py - 20 and pos.y() <= h - self.MARGIN_BOTTOM:
                hovered = net
                break

        if hovered != self._hovered_network:
            self._hovered_network = hovered
            self.update()
            if hovered:
                tip = (
                    f"<b>{hovered.ssid}</b><br/>"
                    f"Channel: {hovered.channel} ({hovered.frequency_mhz} MHz)<br/>"
                    f"Signal: {hovered.signal}% ({hovered.rssi_dbm} dBm)<br/>"
                    f"Band: {hovered.band} | Radio: {hovered.radio_type}<br/>"
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

    def _get_channel_x(self, channel: int, margin_left: float, graph_w: float) -> float:
        if self._active_band == "2.4 GHz":
            min_ch, max_ch = 0, 15
            frac = (channel - min_ch) / (max_ch - min_ch)
            return margin_left + frac * graph_w
        else:
            if channel in CHANNELS_5GHZ:
                idx = CHANNELS_5GHZ.index(channel)
                return margin_left + ((idx + 0.5) / len(CHANNELS_5GHZ)) * graph_w
            else:
                min_ch, max_ch = 32, 168
                frac = (channel - min_ch) / (max_ch - min_ch)
                return margin_left + frac * graph_w

    def _get_peak_coords(self, net: WiFiNetwork, margin_left: float, graph_w: float, margin_top: float, graph_h: float):
        px = self._get_channel_x(net.channel, margin_left, graph_w)
        sig_frac = max(0.05, min(1.0, net.signal / 100.0))
        py = (margin_top + graph_h) - (sig_frac * graph_h * 0.88)
        return px, py

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        margin_left = self.MARGIN_LEFT
        margin_right = self.MARGIN_RIGHT
        margin_bottom = self.MARGIN_BOTTOM
        margin_top = self.MARGIN_TOP

        graph_w = max(100.0, w - margin_left - margin_right)
        graph_h = max(100.0, h - margin_top - margin_bottom)
        base_y = margin_top + graph_h

        # 1. Background
        painter.fillRect(0, 0, w, h, QColor("#0F141C"))

        # 2. Draw Y-Axis Signal Grid Lines (-30 dBm to -100 dBm / 100% to 0%)
        painter.setFont(QFont("Segoe UI", 8))
        levels = [
            (1.00, "-30 dBm (100%)", "#38EF7D"),
            (0.75, "-55 dBm (75%)", "#00D2FF"),
            (0.50, "-70 dBm (50%)", "#FFA726"),
            (0.25, "-85 dBm (25%)", "#EF4444"),
        ]

        for frac, label, col_str in levels:
            ly = base_y - (frac * graph_h * 0.88)
            painter.setPen(QPen(QColor("#1A2536"), 1, Qt.DashLine))
            painter.drawLine(int(margin_left), int(ly), int(w - margin_right), int(ly))

            painter.setPen(QColor("#8E9FB5"))
            painter.drawText(QRectF(2, ly - 8, margin_left - 10, 16), Qt.AlignRight | Qt.AlignVCenter, label)

        # Baseline
        painter.setPen(QPen(QColor("#24334A"), 2))
        painter.drawLine(int(margin_left), int(base_y), int(w - margin_right), int(base_y))

        # 3. Draw X-Axis Channel Ticks and Markers
        font_axis = QFont("Segoe UI", 9, QFont.Bold)
        painter.setFont(font_axis)

        if self._active_band == "2.4 GHz":
            ch_list = list(range(1, 15))
            for ch in ch_list:
                cx = self._get_channel_x(ch, margin_left, graph_w)
                painter.setPen(QPen(QColor("#24334A"), 1))
                painter.drawLine(int(cx), int(base_y), int(cx), int(base_y + 6))

                is_primary = ch in (1, 6, 11)
                if is_primary:
                    painter.setPen(QColor("#00D2FF"))
                else:
                    painter.setPen(QColor("#8E9FB5"))

                painter.drawText(QRectF(cx - 15, base_y + 8, 30, 20), Qt.AlignCenter, str(ch))

                if is_primary:
                    painter.setPen(QPen(QColor("#00D2FF"), 1, Qt.DotLine))
                    painter.drawLine(int(cx), int(margin_top), int(cx), int(base_y))
        else:
            for ch in CHANNELS_5GHZ:
                cx = self._get_channel_x(ch, margin_left, graph_w)
                painter.setPen(QPen(QColor("#24334A"), 1))
                painter.drawLine(int(cx), int(base_y), int(cx), int(base_y + 6))

                painter.setPen(QColor("#8E9FB5"))
                painter.drawText(QRectF(cx - 16, base_y + 8, 32, 20), Qt.AlignCenter, str(ch))

        # X-axis label
        painter.setPen(QColor("#64748B"))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(QRectF(margin_left, base_y + 32, graph_w, 20), Qt.AlignCenter, f"{self._active_band} WiFi Channels")

        # 4. Draw Networks Spectral Bell Curves
        matching_nets = [n for n in self._networks if n.band == self._active_band and n.channel > 0]
        sorted_nets = sorted(matching_nets, key=lambda n: (1 if (self._selected_bssid == n.bssid.lower()) else 0, n.signal))

        font_label = QFont("Segoe UI", 8, QFont.Bold)
        painter.setFont(font_label)

        for i, net in enumerate(sorted_nets):
            is_selected = (self._selected_bssid == net.bssid.lower())
            is_hovered = (self._hovered_network == net)

            color_base = self.PALETTE[i % len(self.PALETTE)]

            px, py = self._get_peak_coords(net, margin_left, graph_w, margin_top, graph_h)

            if self._active_band == "2.4 GHz":
                ch_span_px = (graph_w / 15.0) * 2.0
            else:
                ch_span_px = max(24.0, (graph_w / len(CHANNELS_5GHZ)) * 0.9)

            left_x = px - ch_span_px
            right_x = px + ch_span_px

            path = QPainterPath()
            path.moveTo(left_x, base_y)
            path.cubicTo(
                left_x + ch_span_px * 0.45, base_y,
                px - ch_span_px * 0.35, py,
                px, py
            )
            path.cubicTo(
                px + ch_span_px * 0.35, py,
                right_x - ch_span_px * 0.45, base_y,
                right_x, base_y
            )
            path.closeSubpath()

            fill_grad = QLinearGradient(px, py, px, base_y)
            alpha_peak = 120 if (is_selected or is_hovered) else 45
            fill_grad.setColorAt(0.0, QColor(color_base.red(), color_base.green(), color_base.blue(), alpha_peak))
            fill_grad.setColorAt(1.0, QColor(color_base.red(), color_base.green(), color_base.blue(), 5))

            painter.setBrush(QBrush(fill_grad))

            pen_width = 2.5 if (is_selected or is_hovered) else 1.5
            stroke_col = QColor("#FFFFFF") if is_selected else color_base
            painter.setPen(QPen(stroke_col, pen_width))
            painter.drawPath(path)

            painter.setBrush(stroke_col)
            painter.drawEllipse(QPointF(px, py), 3.5, 3.5)

            clean_name = net.ssid if len(net.ssid) <= 12 else net.ssid[:10] + ".."
            lbl_str = f"{clean_name} ({net.signal}%)"

            lbl_w = 88.0
            lbl_rect = QRectF(px - lbl_w / 2.0, py - 20, lbl_w, 16)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(15, 20, 28, 200))
            painter.drawRoundedRect(lbl_rect, 3, 3)

            painter.setPen(QColor("#FFFFFF") if (is_selected or is_hovered) else color_base)
            painter.drawText(lbl_rect, Qt.AlignCenter, lbl_str)

        if not matching_nets:
            painter.setPen(QColor("#64748B"))
            painter.setFont(QFont("Segoe UI", 11))
            painter.drawText(
                QRectF(margin_left, margin_top, graph_w, graph_h),
                Qt.AlignCenter,
                f"No {self._active_band} networks detected in current scan."
            )


class ChannelHeatmapWidget(QWidget):
    """Complete Channel Heatmap with Band Switcher and Channel Congestion Analysis."""

    network_selected = Signal(object)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Top Control Bar
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

        self.btn_24 = QPushButton("2.4 GHz Band")
        self.btn_24.setCheckable(True)
        self.btn_24.setChecked(True)

        self.btn_50 = QPushButton("5 GHz Band")
        self.btn_50.setCheckable(True)

        btn_style = """
            QPushButton {
                background-color: #161D27;
                color: #8E9FB5;
                border: 1px solid #232E40;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:checked {
                background-color: #00D2FF;
                color: #000000;
                border: 1px solid #00D2FF;
            }
            QPushButton:hover:!checked {
                background-color: #1E2738;
                color: #FFFFFF;
            }
        """
        self.btn_24.setStyleSheet(btn_style)
        self.btn_50.setStyleSheet(btn_style)

        self.button_group = QButtonGroup(self)
        self.button_group.addButton(self.btn_24)
        self.button_group.addButton(self.btn_50)

        self.btn_24.clicked.connect(lambda: self._on_band_changed("2.4 GHz"))
        self.btn_50.clicked.connect(lambda: self._on_band_changed("5 GHz"))

        top_bar.addWidget(self.btn_24)
        top_bar.addWidget(self.btn_50)
        top_bar.addStretch()

        self.lbl_congestion_summary = QLabel("Channel Analysis: Scan to view congestion")
        self.lbl_congestion_summary.setStyleSheet("color: #8E9FB5; font-size: 12px;")
        top_bar.addWidget(self.lbl_congestion_summary)

        layout.addLayout(top_bar)

        # Spectral Graph Canvas
        self.canvas = ChannelSpectrumCanvas()
        self.canvas.network_selected.connect(self.network_selected.emit)
        layout.addWidget(self.canvas, stretch=1)

    def set_networks(self, networks: List[WiFiNetwork]):
        self.canvas.set_networks(networks)
        self._update_congestion_summary(networks)

    def select_network(self, bssid: str):
        self.canvas.set_selected_bssid(bssid)

    def _on_band_changed(self, band: str):
        self.canvas.set_active_band(band)

    def _update_congestion_summary(self, networks: List[WiFiNetwork]):
        nets_24 = [n for n in networks if n.band == "2.4 GHz"]
        ch_counts: Dict[int, int] = {}
        for n in nets_24:
            ch_counts[n.channel] = ch_counts.get(n.channel, 0) + 1

        c1 = ch_counts.get(1, 0)
        c6 = ch_counts.get(6, 0)
        c11 = ch_counts.get(11, 0)

        best_ch = min([(1, c1), (6, c6), (11, c11)], key=lambda x: x[1])[0]
        self.lbl_congestion_summary.setText(
            f"2.4 GHz APs: [Ch 1: {c1}]  [Ch 6: {c6}]  [Ch 11: {c11}]  ➜  Recommended: Channel {best_ch}"
        )
