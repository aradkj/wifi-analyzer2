"""
WiFi Analyzer Pro - Subprocess Utilities
Ensures commands run 100% silently in the background without creating or flashing
console windows, Command Prompt, or PowerShell windows.
"""

from __future__ import annotations
import sys
import subprocess
from typing import Tuple, List, Union, Optional, Any


def get_silent_subprocess_flags() -> Tuple[Optional[Any], int]:
    """
    Constructs Windows-specific STARTUPINFO and creationflags to guarantee
    that subprocesses run completely hidden without flashing any console window.
    Safe to execute on non-Windows systems as well (returns benign defaults).
    """
    startupinfo: Optional[Any] = None
    creationflags: int = 0

    if sys.platform == "win32":
        # Windows-specific: Hide window flag
        if hasattr(subprocess, "STARTUPINFO"):
            startupinfo = subprocess.STARTUPINFO()
            if hasattr(subprocess, "STARTF_USESHOWWINDOW"):
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            if hasattr(subprocess, "SW_HIDE"):
                startupinfo.wShowWindow = subprocess.SW_HIDE

        # Windows-specific: CREATE_NO_WINDOW prevents console allocation entirely
        if hasattr(subprocess, "CREATE_NO_WINDOW"):
            creationflags |= subprocess.CREATE_NO_WINDOW

    return startupinfo, creationflags


def run_hidden_command(
    command: Union[List[str], str],
    timeout: int = 15,
    cwd: Optional[str] = None
) -> Tuple[int, str, str]:
    """
    Execute a system command in the background with zero visible console window.

    Args:
        command: Command and arguments as list or string.
        timeout: Execution timeout in seconds.
        cwd: Working directory.

    Returns:
        Tuple of (return_code, stdout_str, stderr_str)
    """
    startupinfo, creationflags = get_silent_subprocess_flags()

    # Determine command invocation format
    shell = False
    if isinstance(command, str):
        # Do not use shell=True unless necessary; splitting into args is safer
        # But if command is string without shell=True, on Windows it's handled directly
        pass

    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            startupinfo=startupinfo,
            creationflags=creationflags,
            timeout=timeout,
            shell=shell,
            cwd=cwd
        )

        # Robust decoding with fallback to avoid crashes on non-UTF8 Windows systems
        stdout_text = _decode_output(proc.stdout)
        stderr_text = _decode_output(proc.stderr)

        return proc.returncode, stdout_text, stderr_text

    except subprocess.TimeoutExpired as exc:
        stdout_text = _decode_output(exc.stdout) if exc.stdout else ""
        stderr_text = f"Command timed out after {timeout} seconds."
        return -1, stdout_text, stderr_text
    except FileNotFoundError as exc:
        return -2, "", f"Executable not found: {exc}"
    except Exception as exc:
        return -3, "", f"Subprocess execution error: {str(exc)}"


def _decode_output(raw_bytes: Optional[bytes]) -> str:
    """Decode raw subprocess output trying UTF-8, OEM/system code pages, and fallback."""
    if not raw_bytes:
        return ""

    # Common Windows encodings: utf-8, cp1252, oem (cp850/cp437)
    encodings_to_try = ["utf-8", "cp1252", "cp850", "cp437", "latin1"]
    for enc in encodings_to_try:
        try:
            return raw_bytes.decode(enc)
        except UnicodeDecodeError:
            continue

    # Fallback with replacement to guarantee zero crash
    return raw_bytes.decode("utf-8", errors="replace")
