"""
WiFi Analyzer Pro - Parser Unit Tests
"""

import unittest
from app.parser import parse_netsh_output


class TestParser(unittest.TestCase):

    def test_standard_output(self):
        sample = """
Interface name : Wi-Fi
There are 2 networks currently visible.

SSID 1 : Office_Network
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP
    BSSID 1                 : 00:1d:0f:aa:bb:cc
         Signal             : 85%
         Radio type         : 802.11ax
         Channel            : 6
         Basic rates (Mbps) : 1 2 5.5 11
         Other rates (Mbps) : 6 9 12 18 24 36 48 54

SSID 2 : Guest_WiFi
    Network type            : Infrastructure
    Authentication          : Open
    Encryption              : None
    BSSID 1                 : 00:09:5b:11:22:33
         Signal             : 40%
         Radio type         : 802.11n
         Channel            : 149
"""
        result = parse_netsh_output(sample)
        self.assertTrue(result.success)
        self.assertEqual(result.count, 2)
        self.assertEqual(result.interface_name, "Wi-Fi")

        # First network (sorted by signal descending)
        net1 = result.networks[0]
        self.assertEqual(net1.ssid, "Office_Network")
        self.assertEqual(net1.signal, 85)
        self.assertEqual(net1.channel, 6)
        self.assertEqual(net1.band, "2.4 GHz")
        self.assertEqual(net1.vendor, "TP-Link")

        # Second network
        net2 = result.networks[1]
        self.assertEqual(net2.ssid, "Guest_WiFi")
        self.assertEqual(net2.signal, 40)
        self.assertEqual(net2.channel, 149)
        self.assertEqual(net2.band, "5 GHz")
        self.assertEqual(net2.vendor, "Netgear")

    def test_multi_bssid_mesh(self):
        sample = """
Interface name : Wi-Fi
There are 1 networks currently visible.

SSID 1 : DualBand_Router
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP
    BSSID 1                 : 04:d9:f5:12:34:56
         Signal             : 90%
         Radio type         : 802.11ax
         Channel            : 6
    BSSID 2                 : 04:d9:f5:12:34:57
         Signal             : 75%
         Radio type         : 802.11ax
         Channel            : 36
"""
        result = parse_netsh_output(sample)
        self.assertTrue(result.success)
        self.assertEqual(result.count, 2)
        # Should have both 2.4G and 5G bands
        self.assertEqual(result.count_24ghz, 1)
        self.assertEqual(result.count_5ghz, 1)
        self.assertTrue(all(n.vendor == "Asus" for n in result.networks))

    def test_hidden_ssid(self):
        sample = """
SSID 1 : 
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP
    BSSID 1                 : 00:1c:b3:aa:bb:cc
         Signal             : 60%
         Radio type         : 802.11ac
         Channel            : 44
"""
        result = parse_netsh_output(sample)
        self.assertTrue(result.success)
        self.assertEqual(result.count, 1)
        net = result.networks[0]
        self.assertTrue(net.is_hidden)
        self.assertEqual(net.ssid, "<Hidden Network>")
        self.assertEqual(net.vendor, "Apple")

    def test_service_stopped_error(self):
        sample = "The Wireless AutoConfig Service (wlansvc) is not running."
        result = parse_netsh_output(sample)
        self.assertFalse(result.success)
        self.assertIn("wlansvc", result.error_message)

    def test_no_interface_error(self):
        sample = "There is no wireless interface on the system."
        result = parse_netsh_output(sample)
        self.assertFalse(result.success)
        self.assertIn("unavailable", result.error_message.lower())

    def test_empty_output(self):
        result = parse_netsh_output("")
        self.assertFalse(result.success)

    def test_malformed_input_no_crash(self):
        garbage = "Random text! @@##$$%%^&*() 1234567890 \n\n ::: :: \x00\x01\x02"
        result = parse_netsh_output(garbage)
        self.assertTrue(result.success)
        self.assertEqual(result.count, 0)


if __name__ == "__main__":
    unittest.main()
