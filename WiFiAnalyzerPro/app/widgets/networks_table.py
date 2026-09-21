"""
WiFi Analyzer Pro - WiFi Networks Table
Displays all discovered WiFi networks in a rich, sortable, filterable table
with graphical signal meters, security badges, and band indicators.
"""

from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QHeaderView, QAbstractItemView, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush, QFont, QAction, QGuiApplication

from app.models import WiFiNetwork


class NumericTableWidgetItem(QTableWidgetItem):
    """Custom TableWidgetItem that sorts numerically instead of alphabetically."""
    def __init__(self, text: str, sort_val: float):
        super().__init__(text)
        self.sort_val = sort_val

    def __lt__(self, other):
        if isinstance(other, NumericTableWidgetItem):
            return self.sort_val < other.sort_val
        return super().__lt__(other)


class NetworksTableWidget(QWidget):
    """Sortable, filterable table of discovered WiFi networks."""

    network_selected = Signal(object)  # Emits selected WiFiNetwork

    COL_SSID = 0
    COL_BSSID = 1
    COL_SIGNAL = 2
    COL_CHANNEL = 3
    COL_BAND = 4
    COL_SECURITY = 5
    COL_RADIO = 6
    COL_VENDOR = 7

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._all_networks: List[WiFiNetwork] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Search / Filter Bar
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 0, 0, 0)

        lbl_filter = QLabel("Filter:")
        lbl_filter.setStyleSheet("color: #8E9FB5; font-weight: 600; font-size: 12px;")
        filter_layout.addWidget(lbl_filter)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search SSID, BSSID, Channel, Band, or Vendor...")
        self.txt_search.setClearButtonEnabled(True)
        self.txt_search.setStyleSheet("""
            QLineEdit {
                background-color: #161D27;
                color: #FFFFFF;
                border: 1px solid #232E40;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #00D2FF;
                background-color: #1A2330;
            }
        """)
        self.txt_search.textChanged.connect(self._apply_filter)
        filter_layout.addWidget(self.txt_search)

        self.lbl_table_count = QLabel("0 networks")
        self.lbl_table_count.setStyleSheet("color: #64748B; font-size: 11px;")
        filter_layout.addWidget(self.lbl_table_count)

        layout.addLayout(filter_layout)

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "SSID", "BSSID (MAC)", "Signal", "Channel", "Band", "Security", "Radio", "Vendor"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        # Header styling and sizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(self.COL_SSID, QHeaderView.Stretch)
        header.setSectionResizeMode(self.COL_BSSID, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_SIGNAL, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_CHANNEL, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_BAND, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_SECURITY, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_RADIO, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_VENDOR, QHeaderView.ResizeToContents)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0F141C;
                alternate-background-color: #141A24;
                color: #E2E8F0;
                border: 1px solid #232E40;
                border-radius: 8px;
                selection-background-color: #1E3A5F;
                selection-color: #FFFFFF;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #161D27;
                color: #8E9FB5;
                font-weight: 700;
                font-size: 11px;
                padding: 8px 10px;
                border: none;
                border-bottom: 2px solid #232E40;
            }
            QTableWidget::item {
                padding: 6px 10px;
            }
            QTableWidget::item:selected {
                background-color: #1D3557;
                color: #FFFFFF;
            }
        """)

        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self.table)

    def set_networks(self, networks: List[WiFiNetwork]):
        """Populate the table with updated list of networks."""
        self._all_networks = networks
        self._populate_rows(networks)

    def _populate_rows(self, networks: List[WiFiNetwork]):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(networks))

        for row, net in enumerate(networks):
            # 1. SSID
            item_ssid = QTableWidgetItem(net.ssid)
            item_ssid.setData(Qt.UserRole, net)  # Store WiFiNetwork object
            if net.is_hidden:
                item_ssid.setForeground(QBrush(QColor("#94A3B8")))
                font = item_ssid.font()
                font.setItalic(True)
                item_ssid.setFont(font)
            else:
                item_ssid.setForeground(QBrush(QColor("#FFFFFF")))
                font = item_ssid.font()
                font.setBold(True)
                item_ssid.setFont(font)
            self.table.setItem(row, self.COL_SSID, item_ssid)

            # 2. BSSID
            item_bssid = QTableWidgetItem(net.bssid.upper())
            item_bssid.setForeground(QBrush(QColor("#94A3B8")))
            font_mono = QFont("Monospace")
            font_mono.setStyleHint(QFont.Monospace)
            font_mono.setPointSize(9)
            item_bssid.setFont(font_mono)
            self.table.setItem(row, self.COL_BSSID, item_bssid)

            # 3. Signal (Bar + % + dBm)
            sig_text = f"{net.signal_bars}  {net.signal:>3}%  ({net.rssi_dbm} dBm)"
            item_signal = NumericTableWidgetItem(sig_text, net.signal)
            if net.signal >= 75:
                item_signal.setForeground(QBrush(QColor("#38EF7D")))
            elif net.signal >= 50:
                item_signal.setForeground(QBrush(QColor("#00D2FF")))
            elif net.signal >= 30:
                item_signal.setForeground(QBrush(QColor("#FFA726")))
            else:
                item_signal.setForeground(QBrush(QColor("#EF4444")))
            self.table.setItem(row, self.COL_SIGNAL, item_signal)

            # 4. Channel
            item_ch = NumericTableWidgetItem(f"Ch {net.channel}", net.channel)
            item_ch.setTextAlignment(Qt.AlignCenter)
            item_ch.setForeground(QBrush(QColor("#CBD5E1")))
            self.table.setItem(row, self.COL_CHANNEL, item_ch)

            # 5. Band
            item_band = QTableWidgetItem(net.band)
            item_band.setTextAlignment(Qt.AlignCenter)
            if net.band == "2.4 GHz":
                item_band.setForeground(QBrush(QColor("#FFA726")))
            elif net.band == "5 GHz":
                item_band.setForeground(QBrush(QColor("#38BDF8")))
            elif net.band == "6 GHz":
                item_band.setForeground(QBrush(QColor("#C084FC")))
            else:
                item_band.setForeground(QBrush(QColor("#64748B")))
            self.table.setItem(row, self.COL_BAND, item_band)

            # 6. Security
            sec_display = f"{net.auth}"
            if net.encryption and net.encryption != "None":
                sec_display += f" ({net.encryption})"
            item_sec = QTableWidgetItem(sec_display)
            if "Open" in net.auth or "None" in net.encryption:
                item_sec.setForeground(QBrush(QColor("#EF4444")))
            elif "WPA3" in net.auth:
                item_sec.setForeground(QBrush(QColor("#38EF7D")))
            else:
                item_sec.setForeground(QBrush(QColor("#93C5FD")))
            self.table.setItem(row, self.COL_SECURITY, item_sec)

            # 7. Radio
            item_radio = QTableWidgetItem(net.radio_type)
            item_radio.setTextAlignment(Qt.AlignCenter)
            item_radio.setForeground(QBrush(QColor("#94A3B8")))
            self.table.setItem(row, self.COL_RADIO, item_radio)

            # 8. Vendor
            item_vendor = QTableWidgetItem(net.vendor)
            item_vendor.setForeground(QBrush(QColor("#E2E8F0")))
            self.table.setItem(row, self.COL_VENDOR, item_vendor)

        self.table.setSortingEnabled(True)
        # Default sort by signal descending
        self.table.sortItems(self.COL_SIGNAL, Qt.DescendingOrder)
        self.lbl_table_count.setText(f"{len(networks)} networks")

    def _apply_filter(self, query: str):
        query = query.strip().lower()
        if not query:
            for r in range(self.table.rowCount()):
                self.table.setRowHidden(r, False)
            self.lbl_table_count.setText(f"{self.table.rowCount()} networks")
            return

        visible_count = 0
        for r in range(self.table.rowCount()):
            match = False
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if item and query in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(r, not match)
            if match:
                visible_count += 1

        self.lbl_table_count.setText(f"{visible_count} of {self.table.rowCount()} networks")

    def _on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        item = self.table.item(row, self.COL_SSID)
        if item:
            net = item.data(Qt.UserRole)
            if net:
                self.network_selected.emit(net)

    def select_network(self, bssid: str):
        """Programmatically select the row matching a given BSSID."""
        for r in range(self.table.rowCount()):
            item_bssid = self.table.item(r, self.COL_BSSID)
            if item_bssid and item_bssid.text().lower() == bssid.lower():
                self.table.selectRow(r)
                break

    def _show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item:
            return

        row = item.row()
        net_item = self.table.item(row, self.COL_SSID)
        if not net_item:
            return
        net: WiFiNetwork = net_item.data(Qt.UserRole)
        if not net:
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1A2330;
                color: #FFFFFF;
                border: 1px solid #2A3649;
                padding: 4px;
                border-radius: 6px;
            }
            QMenu::item {
                padding: 6px 14px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #00D2FF;
                color: #000000;
            }
        """)

        action_copy_ssid = QAction(f"Copy SSID: '{net.ssid}'", self)
        action_copy_ssid.triggered.connect(lambda: QGuiApplication.clipboard().setText(net.ssid))
        menu.addAction(action_copy_ssid)

        action_copy_bssid = QAction(f"Copy BSSID: {net.bssid.upper()}", self)
        action_copy_bssid.triggered.connect(lambda: QGuiApplication.clipboard().setText(net.bssid.upper()))
        menu.addAction(action_copy_bssid)

        action_copy_all = QAction("Copy Network Details", self)
        action_copy_all.triggered.connect(lambda: QGuiApplication.clipboard().setText(str(net.to_dict())))
        menu.addAction(action_copy_all)

        menu.exec(self.table.viewport().mapToGlobal(pos))
