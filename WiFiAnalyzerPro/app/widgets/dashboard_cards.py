"""
WiFi Analyzer Pro - Dashboard Summary Cards
Displays key wireless metrics in modern, dark-themed cards with colored accent headers.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt
from app.models import ScanResult


class StatCard(QFrame):
    """An individual metric card with accent border, title, large value, and subtitle."""

    def __init__(self, title: str, accent_color: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("StatCard")
        self.accent_color = accent_color

        self.setStyleSheet(f"""
            QFrame#StatCard {{
                background-color: #161D27;
                border: 1px solid #232E40;
                border-top: 3px solid {accent_color};
                border-radius: 8px;
                padding: 10px 14px;
            }}
            QFrame#StatCard:hover {{
                border-color: {accent_color};
                background-color: #1A2330;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Title / Label
        self.lbl_title = QLabel(title.upper())
        self.lbl_title.setStyleSheet("""
            font-size: 11px;
            font-weight: 700;
            color: #8E9FB5;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(self.lbl_title)

        # Large Value
        self.lbl_value = QLabel("—")
        self.lbl_value.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 800;
            color: #FFFFFF;
        """)
        layout.addWidget(self.lbl_value)

        # Subtitle / Description
        self.lbl_sub = QLabel("Awaiting scan")
        self.lbl_sub.setStyleSheet("""
            font-size: 11px;
            color: #94A3B8;
        """)
        self.lbl_sub.setWordWrap(True)
        layout.addWidget(self.lbl_sub)

    def set_content(self, value: str, subtext: str = ""):
        self.lbl_value.setText(value)
        if subtext:
            self.lbl_sub.setText(subtext)


class DashboardCardsWidget(QWidget):
    """Container holding all summary metric cards in a horizontal row."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 1. Total Networks Card
        self.card_total = StatCard("Networks Found", "#00D2FF")
        layout.addWidget(self.card_total)

        # 2. Strongest Signal Card
        self.card_strongest = StatCard("Strongest Signal", "#38EF7D")
        layout.addWidget(self.card_strongest)

        # 3. 2.4 GHz Card
        self.card_24 = StatCard("2.4 GHz Band", "#FFA726")
        layout.addWidget(self.card_24)

        # 4. 5 GHz Card
        self.card_50 = StatCard("5 GHz Band", "#A78BFA")
        layout.addWidget(self.card_50)

        # 5. Best Channel Recommendation
        self.card_channel = StatCard("Recommended Ch", "#38BDF8")
        layout.addWidget(self.card_channel)

    def update_metrics(self, result: ScanResult):
        """Update all card statistics from scan result."""
        # Total
        self.card_total.set_content(
            str(result.count),
            f"{result.count_unknown_band} unknown bands" if result.count_unknown_band > 0 else f"Avg Signal: {result.average_signal}%"
        )

        # Strongest
        strongest = result.strongest_network
        if strongest:
            clean_name = strongest.ssid[:16] + "..." if len(strongest.ssid) > 16 else strongest.ssid
            self.card_strongest.set_content(
                f"{strongest.signal}%",
                f"{clean_name} ({strongest.rssi_dbm} dBm)"
            )
        else:
            self.card_strongest.set_content("—", "No networks found")

        # 2.4 GHz
        pct_24 = round((result.count_24ghz / result.count * 100)) if result.count > 0 else 0
        self.card_24.set_content(
            str(result.count_24ghz),
            f"{pct_24}% of discovered networks"
        )

        # 5 GHz
        pct_50 = round((result.count_5ghz / result.count * 100)) if result.count > 0 else 0
        self.card_50.set_content(
            str(result.count_5ghz),
            f"{pct_50}% of discovered networks"
        )

        # Best Channel Recommendation (2.4 GHz)
        if result.count > 0:
            best_ch, interference = result.recommend_best_24ghz_channel()
            self.card_channel.set_content(
                f"Channel {best_ch}",
                f"Least congested (direct APs: {interference})"
            )
        else:
            self.card_channel.set_content("—", "No channel data")
