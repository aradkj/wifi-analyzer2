"""
WiFi Analyzer Pro - OUI (Organizationally Unique Identifier) Lookup
Maps MAC/BSSID addresses to network hardware manufacturers.
"""

from typing import Dict

# Comprehensive table of top WiFi chipset & router hardware vendors
OUI_TABLE: Dict[str, str] = {
    # Apple
    "00:17:F2": "Apple", "00:1C:B3": "Apple", "00:1E:52": "Apple", "00:23:12": "Apple",
    "00:25:00": "Apple", "00:26:08": "Apple", "00:26:BB": "Apple", "28:CF:E9": "Apple",
    "3C:07:54": "Apple", "3C:2E:F9": "Apple", "60:03:08": "Apple", "70:56:81": "Apple",
    "78:4F:43": "Apple", "80:E6:50": "Apple", "88:66:5A": "Apple", "A4:83:E7": "Apple",
    "AC:BC:32": "Apple", "BC:52:B7": "Apple", "DC:A9:04": "Apple", "F0:18:98": "Apple",

    # Intel
    "00:13:02": "Intel", "00:15:00": "Intel", "00:16:EA": "Intel", "00:19:D1": "Intel",
    "00:21:6A": "Intel", "00:24:D7": "Intel", "34:13:E8": "Intel", "48:51:B7": "Intel",
    "5C:80:B6": "Intel", "68:05:CA": "Intel", "7C:5C:F8": "Intel", "80:86:F2": "Intel",
    "8C:16:45": "Intel", "A4:4E:31": "Intel", "C8:5B:76": "Intel", "E4:A7:A0": "Intel",

    # TP-Link
    "00:1D:0F": "TP-Link", "00:21:27": "TP-Link", "00:23:CD": "TP-Link", "00:27:19": "TP-Link",
    "14:CF:92": "TP-Link", "18:A6:F7": "TP-Link", "1C:3B:F3": "TP-Link", "30:B5:C2": "TP-Link",
    "50:C7:BF": "TP-Link", "54:AF:97": "TP-Link", "60:32:B1": "TP-Link", "68:FF:7B": "TP-Link",
    "70:4F:57": "TP-Link", "74:DA:38": "TP-Link", "84:16:F9": "TP-Link", "98:DA:C4": "TP-Link",
    "A4:2B:B0": "TP-Link", "C0:06:C3": "TP-Link", "C4:6E:1F": "TP-Link", "D8:07:B6": "TP-Link",
    "E4:C3:2A": "TP-Link", "E8:48:B8": "TP-Link", "EC:08:6B": "TP-Link", "F4:F2:6D": "TP-Link",

    # Netgear
    "00:09:5B": "Netgear", "00:0F:B5": "Netgear", "00:14:6C": "Netgear", "00:18:4D": "Netgear",
    "00:1B:2F": "Netgear", "00:1E:2A": "Netgear", "00:24:B2": "Netgear", "00:26:F2": "Netgear",
    "10:0C:6B": "Netgear", "20:4E:7F": "Netgear", "28:C6:8E": "Netgear", "44:94:FC": "Netgear",
    "78:D2:94": "Netgear", "84:1B:5E": "Netgear", "9C:3D:CF": "Netgear", "A0:04:60": "Netgear",
    "C0:FF:D4": "Netgear", "C4:04:15": "Netgear", "E0:46:9A": "Netgear", "E4:F4:C6": "Netgear",

    # Asus (ASUSTek)
    "00:0C:6E": "Asus", "00:11:2F": "Asus", "00:15:F2": "Asus", "00:18:F3": "Asus",
    "00:1E:8C": "Asus", "00:22:15": "Asus", "00:26:18": "Asus", "04:D9:F5": "Asus",
    "08:62:66": "Asus", "10:7B:44": "Asus", "1C:87:2C": "Asus", "2C:4D:54": "Asus",
    "38:D5:47": "Asus", "40:16:7E": "Asus", "50:46:5D": "Asus", "60:45:CB": "Asus",
    "70:4D:7B": "Asus", "AC:9E:17": "Asus", "BC:EE:7B": "Asus", "F0:79:59": "Asus",

    # Cisco / Linksys
    "00:00:0C": "Cisco", "00:01:42": "Cisco", "00:04:4D": "Cisco", "00:06:52": "Cisco",
    "00:11:21": "Cisco", "00:14:1C": "Cisco", "00:18:BA": "Cisco", "00:21:55": "Cisco",
    "00:06:25": "Linksys", "00:0F:66": "Linksys", "00:14:BF": "Linksys", "00:18:39": "Linksys",
    "00:22:6B": "Linksys", "00:25:9C": "Linksys", "14:91:82": "Linksys", "C0:56:27": "Linksys",

    # Ubiquiti
    "00:15:6D": "Ubiquiti", "00:27:22": "Ubiquiti", "04:18:D6": "Ubiquiti", "24:A4:3C": "Ubiquiti",
    "44:D9:E7": "Ubiquiti", "68:72:51": "Ubiquiti", "74:83:C2": "Ubiquiti", "78:8A:20": "Ubiquiti",
    "80:2A:A8": "Ubiquiti", "B4:FB:E4": "Ubiquiti", "DC:9F:DB": "Ubiquiti", "F0:9F:C2": "Ubiquiti",

    # Huawei
    "00:18:82": "Huawei", "00:1E:10": "Huawei", "00:25:68": "Huawei", "00:25:9E": "Huawei",
    "08:19:A6": "Huawei", "10:1B:54": "Huawei", "20:2B:C1": "Huawei", "28:31:52": "Huawei",
    "34:CD:BE": "Huawei", "48:46:FB": "Huawei", "70:7B:E8": "Huawei", "E0:24:7F": "Huawei",

    # D-Link
    "00:05:5D": "D-Link", "00:0D:88": "D-Link", "00:13:46": "D-Link", "00:15:E9": "D-Link",
    "00:17:9A": "D-Link", "00:19:5B": "D-Link", "00:1B:11": "D-Link", "00:1E:58": "D-Link",
    "1C:7E:E5": "D-Link", "28:10:7B": "D-Link", "78:54:2E": "D-Link", "B0:C5:54": "D-Link",

    # Google
    "00:1A:11": "Google", "3C:5A:37": "Google", "54:60:09": "Google", "70:EE:50": "Google",
    "D8:6C:63": "Google", "F4:F5:DB": "Google", "F8:8F:C2": "Google",

    # Samsung
    "00:00:F0": "Samsung", "00:07:AB": "Samsung", "00:12:FB": "Samsung", "00:15:99": "Samsung",
    "00:1D:25": "Samsung", "00:21:19": "Samsung", "00:24:54": "Samsung", "5C:F6:DC": "Samsung",

    # Xiaomi
    "04:CF:8C": "Xiaomi", "14:F6:5A": "Xiaomi", "28:6C:07": "Xiaomi", "34:80:DF": "Xiaomi",
    "50:64:2B": "Xiaomi", "64:09:80": "Xiaomi", "78:11:DC": "Xiaomi", "A4:93:3F": "Xiaomi",

    # Amazon
    "00:FC:8B": "Amazon", "38:F7:3D": "Amazon", "40:B4:CD": "Amazon", "44:65:0D": "Amazon",
    "68:37:E9": "Amazon", "AC:63:BE": "Amazon", "FC:A1:83": "Amazon",

    # Arris / Motorola
    "00:00:CA": "Arris", "00:08:0E": "Arris", "00:15:CE": "Arris", "00:1D:CD": "Arris",
    "00:24:A0": "Arris", "38:4C:90": "Arris", "58:56:E8": "Arris", "94:87:70": "Arris",

    # AVM (FRITZ!Box)
    "00:04:0E": "AVM FRITZ!", "00:1A:4F": "AVM FRITZ!", "00:24:FE": "AVM FRITZ!",
    "34:81:C4": "AVM FRITZ!", "38:10:D5": "AVM FRITZ!", "9C:C7:A6": "AVM FRITZ!",

    # Technicolor / Thomson
    "00:10:7B": "Technicolor", "00:14:7F": "Technicolor", "00:19:70": "Technicolor",
    "44:32:C8": "Technicolor", "58:98:35": "Technicolor",

    # Raspberry Pi
    "B8:27:EB": "Raspberry Pi", "DC:A6:32": "Raspberry Pi", "E4:5F:01": "Raspberry Pi",
    "28:CD:C1": "Raspberry Pi", "D8:3A:DD": "Raspberry Pi",

    # Micro-Star (MSI)
    "00:16:17": "MSI", "00:19:DB": "MSI", "00:1D:92": "MSI", "40:8D:5C": "MSI",

    # Belkin
    "00:11:50": "Belkin", "00:17:3F": "Belkin", "00:1C:DF": "Belkin", "08:86:3B": "Belkin",

    # ZyXEL
    "00:02:CF": "ZyXEL", "00:13:49": "ZyXEL", "00:19:CB": "ZyXEL", "50:67:F0": "ZyXEL",

    # Synology
    "00:11:32": "Synology",

    # Espressif (ESP8266 / ESP32 IoT devices)
    "18:FE:34": "Espressif IoT", "24:0A:C4": "Espressif IoT", "30:AE:A4": "Espressif IoT",
    "84:CC:A8": "Espressif IoT", "A4:CF:12": "Espressif IoT", "C4:4F:33": "Espressif IoT",
}


def lookup_vendor(bssid: str) -> str:
    """
    Look up device manufacturer from BSSID MAC address.
    Normalizes separators to colons and checks first 3 bytes (OUI).
    """
    if not bssid or len(bssid) < 8:
        return "Unknown"

    cleaned = bssid.upper().replace("-", ":").replace(".", ":").strip()
    if cleaned in ("FF:FF:FF:FF:FF:FF", "00:00:00:00:00:00"):
        return "Broadcast" if "FF" in cleaned else "Unknown"

    parts = cleaned.split(":")
    if len(parts) >= 3:
        prefix = f"{parts[0]:0>2}:{parts[1]:0>2}:{parts[2]:0>2}"
        if prefix in OUI_TABLE:
            return OUI_TABLE[prefix]

    # Check for locally administered MAC address (private/randomized MAC)
    try:
        first_byte = int(parts[0], 16)
        if first_byte & 0x02:
            return "Private / Randomized"
    except (ValueError, IndexError):
        pass

    return "Unknown"
