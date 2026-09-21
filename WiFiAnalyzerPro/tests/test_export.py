"""
WiFi Analyzer Pro - Export Functionality Tests
"""

import os
import json
import csv
import tempfile
import unittest
from datetime import datetime

from app.models import WiFiNetwork, ScanResult
from app.utils.exporter import export_to_csv, export_to_json


class TestExport(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        n1 = WiFiNetwork(ssid="WiFi_Home", bssid="00:1d:0f:11:22:33", signal=90, channel=6, band="2.4 GHz", vendor="TP-Link")
        n2 = WiFiNetwork(ssid="WiFi_Office", bssid="00:1c:b3:44:55:66", signal=75, channel=36, band="5 GHz", vendor="Apple")
        self.result = ScanResult(
            timestamp=datetime(2026, 9, 20, 12, 0, 0),
            networks=[n1, n2],
            interface_name="Wi-Fi"
        )

    def test_csv_export(self):
        csv_path = os.path.join(self.tmp_dir, "test_scan.csv")
        success = export_to_csv(self.result, csv_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(csv_path))

        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["SSID"], "WiFi_Home")
            self.assertEqual(rows[0]["Vendor"], "TP-Link")
            self.assertEqual(rows[1]["SSID"], "WiFi_Office")

    def test_json_export(self):
        json_path = os.path.join(self.tmp_dir, "test_scan.json")
        success = export_to_json(self.result, json_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(json_path))

        with open(json_path, mode="r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["application"], "WiFi Analyzer Pro")
            self.assertEqual(data["total_networks"], 2)
            self.assertEqual(len(data["networks"]), 2)
            self.assertEqual(data["networks"][0]["ssid"], "WiFi_Home")


if __name__ == "__main__":
    unittest.main()
