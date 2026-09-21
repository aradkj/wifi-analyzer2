"""
WiFi Analyzer Pro - Data Models
Defines structured representations of WiFi networks, scan results, and wireless attributes.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Tuple


def channel_to_frequency(channel: int, band: str) -> int:
    """Calculate approximate center frequency in MHz given channel and band."""
    if band == "2.4 GHz" and 1 <= channel <= 14:
        if channel == 14:
            return 2484
        return 2407 + (channel * 5)
    elif band == "5 GHz" and 32 <= channel <= 177:
        return 5000 + (channel * 5)
    elif band == "6 GHz" and 1 <= channel <= 233:
        return 5950 + (channel * 5)
    return 0


def determine_band(channel: int, radio_type: str = "") -> str:
    """
    Determine wireless band from channel number and radio type.
    Returns '2.4 GHz', '5 GHz', '6 GHz', or 'Unknown'.
    """
    if channel <= 0:
        return "Unknown"

    radio = radio_type.lower()

    # Prefer explicit 6 GHz detection when radio indicates Wi-Fi 6E (ax/be)
    # Valid 6 GHz channels in this codebase are 1..233 with step 4: 1,5,9,...,233
    if ("ax" in radio or "be" in radio) and 1 <= channel <= 233 and ((channel - 1) % 4 == 0):
        return "6 GHz"

    # Standard 2.4 GHz channels 1 to 14
    if 1 <= channel <= 14:
        return "2.4 GHz"

    # Standard 5 GHz channels: 32 through 177
    if 32 <= channel <= 177:
        return "5 GHz"

    # 6 GHz band (Wi-Fi 6E / Wi-Fi 7): channels up to 233
    if 180 <= channel <= 233 and ("ax" in radio or "be" in radio):
        return "6 GHz"

    return "Unknown"


def calculate_rssi_dbm(signal_percent: int) -> int:
    """
    Convert Windows signal percentage (0-100%) to approximate RSSI in dBm.
    Common formula: dBm ~= (percent / 2) - 100
    Range: 100% -> -50 dBm, 50% -> -75 dBm, 0% -> -100 dBm
    """
    clamped = max(0, min(100, signal_percent))
    return int((clamped / 2.0) - 100)


def signal_to_bars(signal_percent: int, length: int = 10) -> str:
    """Generate a visual ASCII/Unicode block bar for signal strength."""
    clamped = max(0, min(100, signal_percent))
    filled = round((clamped / 100.0) * length)
    empty = length - filled
    return "█" * filled + "░" * empty


def get_signal_quality(signal_percent: int) -> str:
    """Return a descriptive quality tier for the signal percentage."""
    if signal_percent >= 75:
        return "Excellent"
    elif signal_percent >= 50:
        return "Good"
    elif signal_percent >= 30:
        return "Fair"
    else:
        return "Weak"


@dataclass
class WiFiNetwork:
    """Represents a discovered WiFi network (BSSID entry)."""
    ssid: str
    bssid: str
    signal: int = 0
    channel: int = 0
    band: str = "Unknown"
    auth: str = "Unknown"
    encryption: str = "Unknown"
    radio_type: str = "Unknown"
    network_type: str = "Infrastructure"
    is_hidden: bool = False
    vendor: str = "Unknown"
    rssi_dbm: int = -100
    frequency_mhz: int = 0
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        # Auto-compute derived attributes if not supplied
        if self.band == "Unknown" and self.channel > 0:
            self.band = determine_band(self.channel, self.radio_type)
        if self.frequency_mhz == 0 and self.channel > 0:
            self.frequency_mhz = channel_to_frequency(self.channel, self.band)
        if self.rssi_dbm == -100 and self.signal > 0:
            self.rssi_dbm = calculate_rssi_dbm(self.signal)
        if not self.ssid or self.ssid.strip() == "":
            self.is_hidden = True
            self.ssid = "<Hidden Network>"

    @property
    def signal_bars(self) -> str:
        return signal_to_bars(self.signal, length=10)

    @property
    def quality_label(self) -> str:
        return get_signal_quality(self.signal)

    @property
    def display_name(self) -> str:
        if self.is_hidden:
            return f"<Hidden> ({self.bssid[-5:]})"
        return self.ssid

    def to_dict(self) -> dict:
        return {
            "ssid": self.ssid,
            "bssid": self.bssid,
            "signal_percent": self.signal,
            "rssi_dbm": self.rssi_dbm,
            "channel": self.channel,
            "band": self.band,
            "frequency_mhz": self.frequency_mhz,
            "auth": self.auth,
            "encryption": self.encryption,
            "radio_type": self.radio_type,
            "network_type": self.network_type,
            "is_hidden": self.is_hidden,
            "vendor": self.vendor,
            "quality": self.quality_label,
            "last_seen": self.last_seen.isoformat(),
        }


@dataclass
class ScanResult:
    """Represents the outcome of a WiFi scan attempt."""
    timestamp: datetime = field(default_factory=datetime.now)
    networks: List[WiFiNetwork] = field(default_factory=list)
    interface_name: str = ""
    success: bool = True
    error_message: str = ""
    raw_output: str = ""

    @property
    def count(self) -> int:
        return len(self.networks)

    @property
    def strongest_network(self) -> Optional[WiFiNetwork]:
        if not self.networks:
            return None
        return max(self.networks, key=lambda net: net.signal)

    @property
    def count_24ghz(self) -> int:
        return sum(1 for net in self.networks if net.band == "2.4 GHz")

    @property
    def count_5ghz(self) -> int:
        return sum(1 for net in self.networks if net.band == "5 GHz")

    @property
    def count_6ghz(self) -> int:
        return sum(1 for net in self.networks if net.band == "6 GHz")

    @property
    def count_unknown_band(self) -> int:
        return sum(1 for net in self.networks if net.band == "Unknown")

    @property
    def average_signal(self) -> int:
        if not self.networks:
            return 0
        return round(sum(net.signal for net in self.networks) / len(self.networks))

    def get_channel_distribution(self, band: Optional[str] = None) -> Dict[int, int]:
        """Return a mapping of channel numbers to count of networks on that channel."""
        dist: Dict[int, int] = {}
        for net in self.networks:
            if band and net.band != band:
                continue
            if net.channel > 0:
                dist[net.channel] = dist.get(net.channel, 0) + 1
        return dist

    def recommend_best_24ghz_channel(self) -> Tuple[int, int]:
        """
        Evaluate non-overlapping channels (1, 6, 11) for interference.
        Returns tuple of (best_channel, interfering_network_count).
        Considers adjacent channel bleed (channels 1-5 bleed into 1, etc.).
        """
        ch_counts = self.get_channel_distribution("2.4 GHz")

        def calc_interference(primary_ch: int) -> int:
            interference = 0
            for ch, count in ch_counts.items():
                diff = abs(ch - primary_ch)
                if diff == 0:
                    interference += count * 3  # Co-channel interference
                elif diff <= 2:
                    interference += count * 2  # Close adjacent interference
                elif diff <= 4:
                    interference += count * 1  # Distant adjacent interference
            return interference

        candidates = [1, 6, 11]
        scored = [(ch, calc_interference(ch), ch_counts.get(ch, 0)) for ch in candidates]
        scored.sort(key=lambda item: (item[1], item[2]))
        best_ch, _, direct_count = scored[0]
        return best_ch, direct_count
