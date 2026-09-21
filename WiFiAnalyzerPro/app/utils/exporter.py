"""
WiFi Analyzer Pro - Scan Exporter
Exports discovered WiFi networks and scan metadata to CSV or JSON formats.
"""

import csv
import json
from datetime import datetime
from typing import List
from app.models import ScanResult, WiFiNetwork


def export_to_csv(result: ScanResult, file_path: str) -> bool:
    """Export scan result to a standard CSV file."""
    try:
        fieldnames = [
            "SSID",
            "BSSID",
            "Signal (%)",
            "RSSI (dBm)",
            "Channel",
            "Band",
            "Frequency (MHz)",
            "Authentication",
            "Encryption",
            "Radio Type",
            "Network Type",
            "Hidden",
            "Vendor",
            "Quality",
            "Timestamp"
        ]

        with open(file_path, mode="w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for net in result.networks:
                writer.writerow({
                    "SSID": net.ssid,
                    "BSSID": net.bssid,
                    "Signal (%)": net.signal,
                    "RSSI (dBm)": net.rssi_dbm,
                    "Channel": net.channel,
                    "Band": net.band,
                    "Frequency (MHz)": net.frequency_mhz,
                    "Authentication": net.auth,
                    "Encryption": net.encryption,
                    "Radio Type": net.radio_type,
                    "Network Type": net.network_type,
                    "Hidden": "Yes" if net.is_hidden else "No",
                    "Vendor": net.vendor,
                    "Quality": net.quality_label,
                    "Timestamp": result.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                })
        return True
    except Exception as exc:
        print(f"CSV Export Error: {exc}")
        return False


def export_to_json(result: ScanResult, file_path: str) -> bool:
    """Export scan result to a structured JSON file."""
    try:
        data = {
            "application": "WiFi Analyzer Pro",
            "scan_timestamp": result.timestamp.isoformat(),
            "interface_name": result.interface_name,
            "total_networks": result.count,
            "count_24ghz": result.count_24ghz,
            "count_5ghz": result.count_5ghz,
            "count_6ghz": result.count_6ghz,
            "average_signal": result.average_signal,
            "strongest_ssid": result.strongest_network.ssid if result.strongest_network else None,
            "networks": [net.to_dict() for net in result.networks]
        }

        with open(file_path, mode="w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=2, ensure_ascii=False)
        return True
    except Exception as exc:
        print(f"JSON Export Error: {exc}")
        return False
