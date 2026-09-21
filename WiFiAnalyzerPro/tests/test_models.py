"""
WiFi Analyzer Pro - Model Unit Tests
"""

import unittest
from datetime import datetime
from app.models import (
    WiFiNetwork, ScanResult, determine_band, channel_to_frequency,
    calculate_rssi_dbm, signal_to_bars, get_signal_quality
)


class TestModels(unittest.TestCase):

    def test_determine_band(self):
        # 2.4 GHz channels
        self.assertEqual(determine_band(1, "802.11n"), "2.4 GHz")
        self.assertEqual(determine_band(6, "802.11g"), "2.4 GHz")
        self.assertEqual(determine_band(11, "802.11ax"), "2.4 GHz")
        self.assertEqual(determine_band(14, "802.11b"), "2.4 GHz")

        # 5 GHz channels
        self.assertEqual(determine_band(36, "802.11ac"), "5 GHz")
        self.assertEqual(determine_band(44, "802.11ax"), "5 GHz")
        self.assertEqual(determine_band(149, "802.11a"), "5 GHz")
        self.assertEqual(determine_band(165, "802.11n"), "5 GHz")

        # Unknown / Invalid
        self.assertEqual(determine_band(0), "Unknown")
        self.assertEqual(determine_band(-5), "Unknown")

        # 6 GHz (Wi-Fi 6E / 802.11ax/be) channels — channels are 1..233 stepping by 4
        self.assertEqual(determine_band(1, "802.11ax"), "6 GHz")
        self.assertEqual(determine_band(5, "802.11be"), "6 GHz")
        self.assertEqual(determine_band(37, "802.11ax"), "6 GHz")

    def test_channel_to_frequency(self):
        # 2.4 GHz
        self.assertEqual(channel_to_frequency(1, "2.4 GHz"), 2412)
        self.assertEqual(channel_to_frequency(6, "2.4 GHz"), 2437)
        self.assertEqual(channel_to_frequency(11, "2.4 GHz"), 2462)
        self.assertEqual(channel_to_frequency(14, "2.4 GHz"), 2484)

        # 5 GHz
        self.assertEqual(channel_to_frequency(36, "5 GHz"), 5180)
        self.assertEqual(channel_to_frequency(40, "5 GHz"), 5200)
        self.assertEqual(channel_to_frequency(149, "5 GHz"), 5745)

        # Unknown
        self.assertEqual(channel_to_frequency(0, "Unknown"), 0)

        # 6 GHz mapping (uses 5950 + channel*5 per code)
        self.assertEqual(channel_to_frequency(1, "6 GHz"), 5955)
        self.assertEqual(channel_to_frequency(5, "6 GHz"), 5975)
        self.assertEqual(channel_to_frequency(233, "6 GHz"), 5950 + (233 * 5))

    def test_calculate_rssi_dbm(self):
        self.assertEqual(calculate_rssi_dbm(100), -50)
        self.assertEqual(calculate_rssi_dbm(50), -75)
        self.assertEqual(calculate_rssi_dbm(0), -100)
        self.assertEqual(calculate_rssi_dbm(80), -60)

    def test_signal_to_bars(self):
        bars_100 = signal_to_bars(100, 10)
        self.assertEqual(bars_100, "██████████")
        bars_50 = signal_to_bars(50, 10)
        self.assertEqual(bars_50, "█████░░░░░")
        bars_0 = signal_to_bars(0, 10)
        self.assertEqual(bars_0, "░░░░░░░░░░")

    def test_get_signal_quality(self):
        self.assertEqual(get_signal_quality(95), "Excellent")
        self.assertEqual(get_signal_quality(75), "Excellent")
        self.assertEqual(get_signal_quality(60), "Good")
        self.assertEqual(get_signal_quality(40), "Fair")
        self.assertEqual(get_signal_quality(20), "Weak")

    def test_wifi_network_dataclass(self):
        net = WiFiNetwork(
            ssid="Home_WiFi",
            bssid="00:11:22:33:44:55",
            signal=88,
            channel=6,
            radio_type="802.11ax"
        )
        self.assertEqual(net.ssid, "Home_WiFi")
        self.assertEqual(net.band, "2.4 GHz")
        self.assertEqual(net.frequency_mhz, 2437)
        self.assertEqual(net.rssi_dbm, -56)
        self.assertFalse(net.is_hidden)
        self.assertEqual(net.quality_label, "Excellent")

    def test_hidden_network(self):
        net = WiFiNetwork(
            ssid="",
            bssid="AA:BB:CC:DD:EE:FF",
            signal=50,
            channel=36
        )
        self.assertTrue(net.is_hidden)
        self.assertEqual(net.ssid, "<Hidden Network>")

    def test_scan_result_metrics(self):
        n1 = WiFiNetwork(ssid="Net1", bssid="00:00:00:00:00:01", signal=90, channel=1, band="2.4 GHz")
        n2 = WiFiNetwork(ssid="Net2", bssid="00:00:00:00:00:02", signal=70, channel=6, band="2.4 GHz")
        n3 = WiFiNetwork(ssid="Net3", bssid="00:00:00:00:00:03", signal=60, channel=36, band="5 GHz")

        res = ScanResult(networks=[n1, n2, n3])
        self.assertEqual(res.count, 3)
        self.assertEqual(res.count_24ghz, 2)
        self.assertEqual(res.count_5ghz, 1)
        self.assertEqual(res.strongest_network.ssid, "Net1")
        self.assertEqual(res.average_signal, 73)

        # Recommendation should choose channel 11 since 1 and 6 have networks
        best_ch, interference = res.recommend_best_24ghz_channel()
        self.assertEqual(best_ch, 11)


if __name__ == "__main__":
    unittest.main()
