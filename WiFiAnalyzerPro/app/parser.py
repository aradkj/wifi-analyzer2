"""
WiFi Analyzer Pro - Netsh Output Parser
Parses Windows 'netsh wlan show networks mode=bssid' output robustly.
Tolerant of localized Windows editions, hidden networks, and multi-BSSID routers.
"""

import re
from typing import List, Tuple, Optional
from datetime import datetime
from app.models import WiFiNetwork, ScanResult, determine_band, calculate_rssi_dbm, channel_to_frequency
from app.utils.oui_lookup import lookup_vendor

# Regex Patterns for Netsh Parsing
RE_INTERFACE = re.compile(r"^(?:Interface name|Nom de l'interface|Schnittstellenname|Nombre de interfaz)\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
RE_SSID_HEADER = re.compile(r"^SSID\s+\d+\s*:\s*(.*)$", re.IGNORECASE)
RE_BSSID_LINE = re.compile(r"BSSID\s+\d+\s*:\s*([0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2})", re.IGNORECASE)
RE_SIGNAL = re.compile(r"(?:Signal|Señal|Signallevel)\s*:\s*(\d{1,3})\s*%", re.IGNORECASE)
RE_CHANNEL = re.compile(r"(?:Channel|Canal|Kanal)\s*:\s*(\d+)", re.IGNORECASE)
RE_RADIO = re.compile(r"(?:Radio\s+type|Type\s+de\s+radio|Funktyp|Tipo\s+de\s+radio)\s*:\s*(802\.11[a-z0-9]+|802\.11)", re.IGNORECASE)
RE_AUTH = re.compile(r"(?:Authentication|Authentification|Authentifizierung|Autenticación)\s*:\s*(.+)$", re.IGNORECASE)
RE_ENCRYPTION = re.compile(r"(?:Encryption|Chiffrement|Verschlüsselung|Cifrado)\s*:\s*(.+)$", re.IGNORECASE)
RE_NET_TYPE = re.compile(r"(?:Network\s+type|Type\s+de\s+réseau|Netzwerktyp|Tipo\s+de\s+red)\s*:\s*(.+)$", re.IGNORECASE)

# Known error patterns in netsh output
ERROR_PATTERNS = [
    (re.compile(r"Wireless AutoConfig Service.*not running|Automatische WLAN-Konfiguration.*wurde nicht gestartet|Service de configuration automatique sans fil.*n'est pas en cours", re.IGNORECASE),
     "Wireless AutoConfig Service (wlansvc) is not running. Please start the WLAN service."),
    (re.compile(r"no wireless interface|keine Drahtlosschnittstelle|aucune interface sans fil|no hay ninguna interfaz", re.IGNORECASE),
     "WiFi adapter is unavailable or disabled."),
    (re.compile(r"Access is denied|Zugriff verweigert|Accès refusé|Acceso denegado", re.IGNORECASE),
     "Permission denied scanning WiFi networks. Try running as Administrator."),
    (re.compile(r"command.*not found|is not recognized|Befehl nicht gefunden", re.IGNORECASE),
     "Windows 'netsh' utility is not available on this system.")
]


def parse_netsh_output(raw_text: str) -> ScanResult:
    """
    Parse the full text output of 'netsh wlan show networks mode=bssid'.
    Never throws unhandled exceptions; returns clean ScanResult.
    """
    now = datetime.now()
    result = ScanResult(timestamp=now, raw_output=raw_text)

    if not raw_text or not raw_text.strip():
        result.success = False
        result.error_message = "No output received from WiFi scanner."
        return result

    # Check for known error signatures
    for pattern, err_msg in ERROR_PATTERNS:
        if pattern.search(raw_text):
            result.success = False
            result.error_message = err_msg
            return result

    # Extract interface name if present
    match_iface = RE_INTERFACE.search(raw_text)
    if match_iface:
        result.interface_name = match_iface.group(1).strip()

    # Split output into SSID blocks
    # Lines before the first SSID line are headers/interface info
    lines = raw_text.splitlines()

    networks: List[WiFiNetwork] = []
    seen_bssids = set()

    current_ssid_name: Optional[str] = None
    current_auth = "Unknown"
    current_encryption = "Unknown"
    current_net_type = "Infrastructure"
    is_hidden = False

    current_bssid: Optional[str] = None
    current_signal = 0
    current_channel = 0
    current_radio = "Unknown"

    def save_current_bssid():
        nonlocal current_bssid, current_signal, current_channel, current_radio
        if not current_bssid:
            return

        normalized_bssid = current_bssid.lower().replace("-", ":")
        if normalized_bssid in seen_bssids:
            current_bssid = None
            return
        seen_bssids.add(normalized_bssid)

        ssid_val = current_ssid_name if current_ssid_name is not None else ""
        if not ssid_val or ssid_val.strip() == "":
            ssid_val = "<Hidden Network>"
            hidden_flag = True
        else:
            hidden_flag = is_hidden

        band_val = determine_band(current_channel, current_radio)
        freq_val = channel_to_frequency(current_channel, band_val)
        rssi_val = calculate_rssi_dbm(current_signal)
        vendor_val = lookup_vendor(normalized_bssid)

        net = WiFiNetwork(
            ssid=ssid_val,
            bssid=normalized_bssid,
            signal=current_signal,
            channel=current_channel,
            band=band_val,
            auth=current_auth,
            encryption=current_encryption,
            radio_type=current_radio,
            network_type=current_net_type,
            is_hidden=hidden_flag,
            vendor=vendor_val,
            rssi_dbm=rssi_val,
            frequency_mhz=freq_val,
            first_seen=now,
            last_seen=now
        )
        networks.append(net)

        # Reset BSSID specific fields
        current_bssid = None
        current_signal = 0
        current_channel = 0
        current_radio = "Unknown"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check for new SSID
        ssid_match = RE_SSID_HEADER.match(stripped)
        if ssid_match:
            # Commit pending BSSID
            save_current_bssid()
            raw_ssid = ssid_match.group(1).strip()
            current_ssid_name = raw_ssid
            is_hidden = (len(raw_ssid) == 0)
            current_auth = "Unknown"
            current_encryption = "Unknown"
            current_net_type = "Infrastructure"
            continue

        # Check for new BSSID
        bssid_match = RE_BSSID_LINE.search(stripped)
        if bssid_match:
            # Commit previous BSSID within current SSID
            save_current_bssid()
            current_bssid = bssid_match.group(1).strip()
            current_signal = 0
            current_channel = 0
            current_radio = "Unknown"
            continue

        # If currently tracking an SSID/BSSID, check properties
        if current_bssid:
            sig_match = RE_SIGNAL.search(stripped)
            if sig_match:
                try:
                    current_signal = int(sig_match.group(1))
                except ValueError:
                    current_signal = 0
                continue

            ch_match = RE_CHANNEL.search(stripped)
            if ch_match:
                try:
                    current_channel = int(ch_match.group(1))
                except ValueError:
                    current_channel = 0
                continue

            rad_match = RE_RADIO.search(stripped)
            if rad_match:
                current_radio = rad_match.group(1).strip()
                continue

        # Properties at the SSID level
        auth_match = RE_AUTH.search(stripped)
        if auth_match:
            current_auth = auth_match.group(1).strip()
            continue

        enc_match = RE_ENCRYPTION.search(stripped)
        if enc_match:
            current_encryption = enc_match.group(1).strip()
            continue

        net_match = RE_NET_TYPE.search(stripped)
        if net_match:
            current_net_type = net_match.group(1).strip()
            continue

    # Commit any trailing BSSID
    save_current_bssid()

    # Sort networks by signal strength descending by default
    networks.sort(key=lambda n: n.signal, reverse=True)

    result.networks = networks
    result.success = True

    if not networks:
        result.error_message = "No WiFi networks found."

    return result
