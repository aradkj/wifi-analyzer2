"""
WiFi Analyzer Pro - OUI Vendor Lookup Tests
"""

import unittest
from app.utils.oui_lookup import lookup_vendor


class TestOUILookup(unittest.TestCase):

    def test_known_vendors(self):
        self.assertEqual(lookup_vendor("00:1C:B3:11:22:33"), "Apple")
        self.assertEqual(lookup_vendor("00:1D:0F:AA:BB:CC"), "TP-Link")
        self.assertEqual(lookup_vendor("00:09:5B:44:55:66"), "Netgear")
        self.assertEqual(lookup_vendor("04:D9:F5:77:88:99"), "Asus")
        self.assertEqual(lookup_vendor("00:27:22:00:11:22"), "Ubiquiti")
        self.assertEqual(lookup_vendor("34:81:C4:AA:BB:CC"), "AVM FRITZ!")
        self.assertEqual(lookup_vendor("B8:27:EB:12:34:56"), "Raspberry Pi")

    def test_dash_separator(self):
        self.assertEqual(lookup_vendor("00-1c-b3-11-22-33"), "Apple")

    def test_private_mac(self):
        # Locally administered bit set: second hex digit has bit 1 set (2, 6, A, E)
        self.assertEqual(lookup_vendor("02:11:22:33:44:55"), "Private / Randomized")

    def test_invalid_input(self):
        self.assertEqual(lookup_vendor(""), "Unknown")
        self.assertEqual(lookup_vendor("123"), "Unknown")
        self.assertEqual(lookup_vendor("00:00:00:00:00:00"), "Unknown")
        self.assertEqual(lookup_vendor("FF:FF:FF:FF:FF:FF"), "Broadcast")


if __name__ == "__main__":
    unittest.main()
