"""
WiFi Analyzer Pro - WiFi Scanner Service
Executes 'netsh wlan show networks mode=bssid' silently without opening
any visible Command Prompt, PowerShell, or console windows.
Integrates PySide6 QThread for smooth, non-blocking UI operation.
"""

import sys
import random
from typing import Optional, List
from datetime import datetime

from PySide6.QtCore import QThread, Signal, QObject

from app.models import ScanResult, WiFiNetwork, determine_band, calculate_rssi_dbm, channel_to_frequency
from app.parser import parse_netsh_output
from app.utils.subprocess_utils import run_hidden_command
from app.utils.oui_lookup import lookup_vendor


class WiFiScanner:
    """Core WiFi scanning engine using Windows netsh WLAN commands."""

    def __init__(self, demo_mode: bool = False):
        self._demo_mode = demo_mode

    @property
    def demo_mode(self) -> bool:
        return self._demo_mode

    @demo_mode.setter
    def demo_mode(self, value: bool):
        self._demo_mode = value

    def scan(self) -> ScanResult:
        """
        Execute silent WiFi scan and return parsed results.
        Runs completely in background with CREATE_NO_WINDOW and SW_HIDE.
        """
        # If demo mode is active or running on non-Windows without netsh, generate simulated data
        if self._demo_mode:
            return self._generate_simulated_networks()

        # Execute Windows netsh command silently
        command = ["netsh", "wlan", "show", "networks", "mode=bssid"]
        returncode, stdout_str, stderr_str = run_hidden_command(command, timeout=12)

        # Handle execution failures
        if returncode == -2 or "Executable not found" in stderr_str:
            # netsh is missing (non-Windows system or stripped environment)
            if sys.platform != "win32":
                # In development/test on non-Windows, fall back gracefully to demo data
                res = self._generate_simulated_networks()
                res.interface_name = "Simulated Interface (Dev Mode)"
                return res
            return ScanResult(
                success=False,
                error_message="Windows 'netsh' command could not be located.",
                raw_output=stderr_str
            )

        if returncode == -1:
            return ScanResult(
                success=False,
                error_message="WiFi scan timed out. The wireless adapter took too long to respond.",
                raw_output=stderr_str
            )

        if returncode != 0 and not stdout_str:
            err = stderr_str.strip() if stderr_str else f"Command returned exit code {returncode}"
            return ScanResult(
                success=False,
                error_message=f"Unable to scan WiFi networks: {err}",
                raw_output=stderr_str
            )

        # Parse real output
        result = parse_netsh_output(stdout_str)
        return result

    def _generate_simulated_networks(self) -> ScanResult:
        """
        Generates realistic simulated WiFi networks for demonstration,
        testing environments, and PCs without physical WiFi adapters.
        """
        now = datetime.now()
        sample_profiles = [
            ("Apex_Ultra_WiFi", "A4:2B:B0:11:2A:3C", 94, 6, "2.4 GHz", "802.11ax", "WPA3-Personal", "CCMP"),
            ("Apex_Ultra_5G", "A4:2B:B0:11:2A:3D", 88, 36, "5 GHz", "802.11ax", "WPA3-Personal", "GCMP"),
            ("Starlink_Mesh_7", "70:4D:7B:88:99:AA", 82, 1, "2.4 GHz", "802.11ax", "WPA2-Personal", "CCMP"),
            ("Starlink_Mesh_7_5G", "70:4D:7B:88:99:AB", 79, 149, "5 GHz", "802.11ax", "WPA2-Personal", "CCMP"),
            ("TechCorp_Corporate", "00:27:22:33:44:55", 73, 11, "2.4 GHz", "802.11n", "WPA2-Enterprise", "CCMP"),
            ("TechCorp_5GHz", "00:27:22:33:44:56", 70, 44, "5 GHz", "802.11ac", "WPA2-Enterprise", "CCMP"),
            ("FRITZ!Box 7590 QA", "34:81:C4:DE:F1:02", 64, 6, "2.4 GHz", "802.11ac", "WPA2-Personal", "CCMP"),
            ("Coffee_Corner_Free", "10:0C:6B:55:66:77", 58, 6, "2.4 GHz", "802.11g", "Open", "None"),
            ("", "BC:EE:7B:44:33:22", 52, 157, "5 GHz", "802.11ac", "WPA2-Personal", "CCMP"),  # Hidden network
            ("Smart_Home_Hub", "18:FE:34:AA:BB:CC", 46, 1, "2.4 GHz", "802.11b", "WPA2-Personal", "TKIP"),
            ("Neighbor_Extender", "C4:6E:1F:90:12:34", 38, 11, "2.4 GHz", "802.11n", "WPA2-Personal", "CCMP"),
            ("Public_Transit_WiFi", "00:19:5B:66:77:88", 29, 6, "2.4 GHz", "802.11g", "Open", "None"),
            ("IoT_Sensor_Array", "84:CC:A8:12:34:56", 22, 1, "2.4 GHz", "802.11n", "WPA2-Personal", "CCMP"),
            ("Guest_Access_5G", "44:94:FC:10:20:30", 61, 52, "5 GHz", "802.11ac", "WPA2-Personal", "CCMP"),
        ]

        networks: List[WiFiNetwork] = []
        for ssid, bssid, base_sig, ch, band, radio, auth, enc in sample_profiles:
            # Apply slight jitter to signal for realistic dynamic behavior on repeat scans
            jitter = random.randint(-4, 4)
            sig = max(10, min(100, base_sig + jitter))
            is_hid = (len(ssid) == 0)
            disp_ssid = "<Hidden Network>" if is_hid else ssid
            freq = channel_to_frequency(ch, band)
            rssi = calculate_rssi_dbm(sig)
            vendor = lookup_vendor(bssid)

            net = WiFiNetwork(
                ssid=disp_ssid,
                bssid=bssid.lower(),
                signal=sig,
                channel=ch,
                band=band,
                auth=auth,
                encryption=enc,
                radio_type=radio,
                network_type="Infrastructure",
                is_hidden=is_hid,
                vendor=vendor,
                rssi_dbm=rssi,
                frequency_mhz=freq,
                first_seen=now,
                last_seen=now
            )
            networks.append(net)

        # Sort descending by signal
        networks.sort(key=lambda n: n.signal, reverse=True)

        return ScanResult(
            timestamp=now,
            networks=networks,
            interface_name="Wi-Fi (Active 802.11ax Adapter)",
            success=True,
            error_message=""
        )


class ScanWorker(QThread):
    """
    Background worker thread to execute WiFi scans asynchronously.
    Prevents UI freezing and keeps the application fluid.
    """
    scan_started = Signal()
    scan_finished = Signal(object)  # Emits ScanResult
    scan_error = Signal(str)

    def __init__(self, scanner: WiFiScanner, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._scanner = scanner

    def run(self):
        self.scan_started.emit()
        try:
            result = self._scanner.scan()
            self.scan_finished.emit(result)
        except Exception as exc:
            self.scan_error.emit(f"Unexpected scan error: {str(exc)}")
