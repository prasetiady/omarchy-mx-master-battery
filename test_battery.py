import importlib.machinery
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


loader = importlib.machinery.SourceFileLoader("battery_tray", str(Path(__file__).with_name("mx-master-battery-tray")))
spec = importlib.util.spec_from_loader(loader.name, loader)
tray = importlib.util.module_from_spec(spec)
loader.exec_module(tray)


class BatteryTests(unittest.TestCase):
    def test_solaar_is_preferred(self):
        with patch.object(tray.subprocess, "check_output", return_value="Battery: 50%, BatteryStatus.DISCHARGING"):
            self.assertEqual(tray.read_battery(), ("50%", "Discharging"))

    def test_failed_mouse_does_not_hide_later_mouse(self):
        def command(args, **kwargs):
            if args[0] == "solaar":
                raise FileNotFoundError()
            if args[1] == "-e":
                return "/mouse_first\n/mouse_second\n"
            if args[2] == "/mouse_first":
                raise subprocess.TimeoutExpired(args, 5)
            return "model: Logitech MX Master 2S\npresent: yes\npercentage: 50% (should be ignored)\nstate: discharging\n"

        with patch.object(tray.subprocess, "check_output", side_effect=command):
            self.assertEqual(tray.read_battery(), ("50%", "Discharging"))

    def test_sysfs_numeric_capacity(self):
        with tempfile.TemporaryDirectory() as directory:
            device = Path(directory) / "hidpp_battery_0"
            device.mkdir()
            (device / "model_name").write_text("Wireless Mouse MX Master 2S")
            (device / "capacity").write_text("75")
            (device / "status").write_text("Charging")
            original_path = tray.Path
            with patch.object(tray.subprocess, "check_output", side_effect=FileNotFoundError), \
                 patch.object(tray, "Path", side_effect=lambda _: original_path(directory)):
                self.assertEqual(tray.read_battery(), ("75%", "Charging"))


if __name__ == "__main__":
    unittest.main()
