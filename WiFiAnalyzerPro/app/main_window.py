"""
WiFi Analyzer Pro - Main Application Window
Coordinates UI components, dashboard metrics, visualizers, background scanning threads,
auto-refresh scheduling, data export, and cross-widget selection synchronization.
"""

from datetime import datetime
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QTabWidget, QStatusBar, QFileDialog, QMessageBox,
    QFrame, QSplitter
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QFont, QPixmap

from app.models import ScanResult, WiFiNetwork
from app.scanner import WiFiScanner, ScanWorker
from app.widgets.dashboard_cards import DashboardCardsWidget
from app.widgets.networks_table import NetworksTableWidget
from app.widgets.signal_chart import SignalChartWidget
from app.widgets.radar import RadarWidget
from app.widgets.heatmap import ChannelHeatmapWidget
from app.utils.resources import get_app_icon_path
from app.utils.exporter import export_to_csv, export_to_json


class MainWindow(QMainWindow):
    """Main desktop application window for WiFi Analyzer Pro."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("WiFi Analyzer Pro")
        self.resize(1180, 780)
        self.setMinimumSize(920, 600)

        # Set application icon
        icon_path = get_app_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))

        # Core Scanner & Worker
        self.scanner = WiFiScanner(demo_mode=False)
        self.current_worker: Optional[ScanWorker] = None
        self.last_scan_result: Optional[ScanResult] = None

        # Auto-refresh timer
        self.auto_refresh_timer = QTimer(self)
        self.auto_refresh_timer.timeout.connect(self._on_auto_refresh_tick)

        # Build UI
        self._init_ui()

        # Perform initial scan after window shows
        QTimer.singleShot(400, self.trigger_scan)

    def _init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        central_widget.setAttribute(Qt.WA_StyledBackground, True)
        central_widget.setStyleSheet("background-color: #0A0E17;")
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(18, 14, 18, 14)
        root_layout.setSpacing(14)

        # 1. Top Header Bar
        header_layout = self._create_header()
        root_layout.addLayout(header_layout)

        # 2. Notification / Warning Banner (Hidden by default)
        self.banner = QFrame()
        self.banner.setObjectName("NotificationBanner")
        self.banner.setStyleSheet("""
            QFrame#NotificationBanner {
                background-color: #2D1A1E;
                border: 1px solid #7F1D1D;
                border-radius: 6px;
                padding: 6px 12px;
            }
        """)
        banner_layout = QHBoxLayout(self.banner)
        banner_layout.setContentsMargins(8, 4, 8, 4)
        self.lbl_banner_msg = QLabel("")
        self.lbl_banner_msg.setStyleSheet("color: #FCA5A5; font-size: 12px; font-weight: 600;")
        banner_layout.addWidget(self.lbl_banner_msg)
        banner_layout.addStretch()

        btn_dismiss = QPushButton("Dismiss")
        btn_dismiss.setStyleSheet("""
            QPushButton {
                background-color: #450A0A;
                color: #FECACA;
                border: 1px solid #991B1B;
                padding: 3px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #7F1D1D;
            }
        """)
        btn_dismiss.clicked.connect(lambda: self.banner.setVisible(False))
        banner_layout.addWidget(btn_dismiss)
        self.banner.setVisible(False)
        root_layout.addWidget(self.banner)

        # 3. Dashboard Cards
        self.dashboard_cards = DashboardCardsWidget()
        root_layout.addWidget(self.dashboard_cards)

        # 4. Main Multi-View Tabs
        self.tab_widget = QTabWidget()

        # Tab 1: Networks Table
        self.networks_table = NetworksTableWidget()
        self.networks_table.network_selected.connect(self._on_network_selected)
        self.tab_widget.addTab(self.networks_table, "Networks Table")

        # Tab 2: Radar View
        self.radar_widget = RadarWidget()
        self.radar_widget.network_selected.connect(self._on_network_selected)
        self.tab_widget.addTab(self.radar_widget, "Radar Sweep")

        # Tab 3: Signal Chart
        self.signal_chart = SignalChartWidget()
        self.signal_chart.network_selected.connect(self._on_network_selected)
        self.tab_widget.addTab(self.signal_chart, "Signal Chart")

        # Tab 4: Channel Heatmap
        self.heatmap_widget = ChannelHeatmapWidget()
        self.heatmap_widget.network_selected.connect(self._on_network_selected)
        self.tab_widget.addTab(self.heatmap_widget, "Channel Heatmap")

        # Tab 5: Overview (Combined Split View)
        overview_widget = self._create_overview_tab()
        self.tab_widget.addTab(overview_widget, "Dashboard Overview")

        root_layout.addWidget(self.tab_widget, stretch=1)

        # 5. Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.lbl_status = QLabel("Ready")
        self.lbl_status.setStyleSheet("color: #00D2FF; font-weight: 600;")
        self.status_bar.addWidget(self.lbl_status)

        self.lbl_backend = QLabel("Backend: Windows netsh (Silent Subprocess)")
        self.lbl_backend.setStyleSheet("color: #64748B; margin-left: 16px;")
        self.status_bar.addPermanentWidget(self.lbl_backend)

        self.lbl_last_scan = QLabel("Last Scan: Never")
        self.lbl_last_scan.setStyleSheet("color: #8E9FB5; margin-left: 16px;")
        self.status_bar.addPermanentWidget(self.lbl_last_scan)

    def _create_header(self) -> QHBoxLayout:
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)

        # Title and Subtitle Block
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        lbl_app_title = QLabel("WiFi Analyzer Pro")
        lbl_app_title.setStyleSheet("""
            font-size: 20px;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: 0.5px;
        """)
        title_box.addWidget(lbl_app_title)

        lbl_subtitle = QLabel("Analyze nearby wireless networks")
        lbl_subtitle.setStyleSheet("""
            font-size: 12px;
            color: #8E9FB5;
        """)
        title_box.addWidget(lbl_subtitle)

        header_layout.addLayout(title_box)
        header_layout.addStretch()

        # Control: Demo / Test Mode Toggle
        self.chk_demo = QCheckBox("Demo Mode")
        self.chk_demo.setToolTip("Toggle simulated WiFi data for demonstration or systems without physical WiFi adapters.")
        self.chk_demo.toggled.connect(self._on_demo_toggled)
        header_layout.addWidget(self.chk_demo)

        # Control: Auto-Refresh Interval
        lbl_auto = QLabel("Auto-Refresh:")
        lbl_auto.setStyleSheet("color: #8E9FB5; font-size: 12px;")
        header_layout.addWidget(lbl_auto)

        self.cmb_auto = QComboBox()
        self.cmb_auto.addItems(["Off", "Every 5s", "Every 10s", "Every 30s"])
        self.cmb_auto.currentIndexChanged.connect(self._on_auto_refresh_changed)
        header_layout.addWidget(self.cmb_auto)

        # Control: Export Button
        self.btn_export = QPushButton("Export...")
        self.btn_export.setToolTip("Export scan results to CSV or JSON format.")
        self.btn_export.clicked.connect(self._on_export_clicked)
        header_layout.addWidget(self.btn_export)

        # Control: Radar Animation Toggle
        self.btn_radar_anim = QPushButton("Pause Radar")
        self.btn_radar_anim.setToolTip("Pause or resume the radar sweep animation.")
        self.btn_radar_anim.clicked.connect(self._on_toggle_radar_anim)
        header_layout.addWidget(self.btn_radar_anim)

        # Prominent SCAN Button
        self.btn_scan = QPushButton("SCAN")
        self.btn_scan.setObjectName("ScanButton")
        self.btn_scan.setToolTip("Scan nearby WiFi networks using Windows netsh (completely in background).")
        self.btn_scan.clicked.connect(self.trigger_scan)
        header_layout.addWidget(self.btn_scan)

        return header_layout

    def _create_overview_tab(self) -> QWidget:
        """Combined split dashboard tab showing mini radar alongside quick charts."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        splitter = QSplitter(Qt.Horizontal)

        # Left: Mini Radar
        self.overview_radar = RadarWidget()
        self.overview_radar.network_selected.connect(self._on_network_selected)
        splitter.addWidget(self.overview_radar)

        # Right: Signal Chart
        self.overview_chart = SignalChartWidget()
        self.overview_chart.network_selected.connect(self._on_network_selected)
        splitter.addWidget(self.overview_chart)

        splitter.setSizes([450, 650])
        layout.addWidget(splitter)
        return widget

    def trigger_scan(self):
        """Initiate asynchronous background WiFi scan."""
        if self.current_worker and self.current_worker.isRunning():
            return

        # 1. Disable SCAN button temporarily
        self.btn_scan.setEnabled(False)
        self.btn_scan.setText("SCANNING...")

        # 2. Update status indicator
        self.lbl_status.setText("Scanning WiFi networks (Background Subprocess)...")
        self.lbl_status.setStyleSheet("color: #FFA726; font-weight: 600;")
        self.banner.setVisible(False)

        # 3. Launch background worker thread
        self.current_worker = ScanWorker(self.scanner, self)
        self.current_worker.scan_finished.connect(self._on_scan_completed)
        self.current_worker.scan_error.connect(self._on_scan_error)
        self.current_worker.start()

    def _on_scan_completed(self, result: ScanResult):
        """Handle successful or parsed scan results."""
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("SCAN")
        self.last_scan_result = result

        now_str = datetime.now().strftime("%H:%M:%S")
        self.lbl_last_scan.setText(f"Last Scan: {now_str}")

        if not result.success or result.count == 0:
            msg = result.error_message or "No WiFi networks found."
            self.lbl_status.setText(msg)
            self.lbl_status.setStyleSheet("color: #EF4444; font-weight: 600;")
            self.lbl_banner_msg.setText(f"Notice: {msg}")
            self.banner.setVisible(True)

            # Still update views with empty list so stale data clears
            self._update_all_views(result)
            return

        # Update status
        iface_txt = f" [{result.interface_name}]" if result.interface_name else ""
        self.lbl_status.setText(f"Scan complete: {result.count} networks found{iface_txt}")
        self.lbl_status.setStyleSheet("color: #38EF7D; font-weight: 600;")
        self.banner.setVisible(False)

        # Update all UI views
        self._update_all_views(result)

    def _update_all_views(self, result: ScanResult):
        """Broadcast new scan data to all components."""
        # 1. Update dashboard cards
        self.dashboard_cards.update_metrics(result)

        # 2. Update table
        self.networks_table.set_networks(result.networks)

        # 3. Update radar
        self.radar_widget.set_networks(result.networks)
        self.overview_radar.set_networks(result.networks)

        # 4. Update signal chart
        self.signal_chart.set_networks(result.networks)
        self.overview_chart.set_networks(result.networks)

        # 5. Update heatmap
        self.heatmap_widget.set_networks(result.networks)

    def _on_scan_error(self, err_msg: str):
        """Handle unexpected scan worker failure."""
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("SCAN")
        self.lbl_status.setText(f"Scan failed: {err_msg}")
        self.lbl_status.setStyleSheet("color: #EF4444; font-weight: 600;")
        self.lbl_banner_msg.setText(f"Error: {err_msg}")
        self.banner.setVisible(True)

    def _on_network_selected(self, net: WiFiNetwork):
        """Synchronize selection across all visualizers."""
        if not net:
            return
        bssid = net.bssid
        self.networks_table.select_network(bssid)
        self.radar_widget.set_selected_bssid(bssid)
        self.overview_radar.set_selected_bssid(bssid)
        self.signal_chart.select_network(bssid)
        self.overview_chart.select_network(bssid)
        self.heatmap_widget.select_network(bssid)

        self.status_bar.showMessage(
            f"Selected: {net.ssid} | Signal: {net.signal}% ({net.rssi_dbm} dBm) | Ch: {net.channel} ({net.band}) | BSSID: {net.bssid.upper()} | Vendor: {net.vendor}",
            6000
        )

    def _on_demo_toggled(self, checked: bool):
        self.scanner.demo_mode = checked
        if checked:
            self.lbl_backend.setText("Backend: Simulated Demo Mode")
            self.lbl_backend.setStyleSheet("color: #FFA726; margin-left: 16px;")
        else:
            self.lbl_backend.setText("Backend: Windows netsh (Silent Subprocess)")
            self.lbl_backend.setStyleSheet("color: #64748B; margin-left: 16px;")
        self.trigger_scan()

    def _on_auto_refresh_changed(self, index: int):
        intervals = {
            0: 0,       # Off
            1: 5000,    # 5s
            2: 10000,   # 10s
            3: 30000    # 30s
        }
        interval_ms = intervals.get(index, 0)
        if interval_ms > 0:
            self.auto_refresh_timer.start(interval_ms)
        else:
            self.auto_refresh_timer.stop()

    def _on_auto_refresh_tick(self):
        if not self.btn_scan.isEnabled():
            return
        self.trigger_scan()

    def _on_toggle_radar_anim(self):
        is_running = self.radar_widget.toggle_animation()
        self.overview_radar.toggle_animation()
        self.btn_radar_anim.setText("Pause Radar" if is_running else "Resume Radar")

    def _on_export_clicked(self):
        if not self.last_scan_result or not self.last_scan_result.networks:
            QMessageBox.information(
                self,
                "Export Scan Results",
                "No scan results available to export. Please perform a WiFi scan first."
            )
            return

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export WiFi Scan Results",
            f"WiFi_Scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv);;JSON Files (*.json)"
        )

        if not file_path:
            return

        success = False
        if file_path.lower().endswith(".json") or "JSON" in selected_filter:
            if not file_path.lower().endswith(".json"):
                file_path += ".json"
            success = export_to_json(self.last_scan_result, file_path)
        else:
            if not file_path.lower().endswith(".csv"):
                file_path += ".csv"
            success = export_to_csv(self.last_scan_result, file_path)

        if success:
            QMessageBox.information(
                self,
                "Export Successful",
                f"WiFi scan data successfully exported to:\n{file_path}"
            )
        else:
            QMessageBox.warning(
                self,
                "Export Failed",
                f"Failed to export scan data to:\n{file_path}"
            )

    def closeEvent(self, event):
        # Stop timers and worker threads cleanly
        self.auto_refresh_timer.stop()
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.wait(1000)
        super().closeEvent(event)
