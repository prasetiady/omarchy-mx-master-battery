# MX Master 2S battery for Omarchy

Show the battery level and charging state of a Logitech MX Master 2S in the Omarchy tray. Open the tray drawer and right-click the mouse icon to see the battery information.

The indicator checks the battery every minute. It uses Solaar if it is installed and can read the mouse. It tries up to three times, with a two-second delay between attempts and a 10-second timeout for each attempt. If all attempts fail, it uses UPower and Linux battery data. UPower can mark its percentage as unreliable, so treat it as an estimate.

## Requirements

- Omarchy 4.0.6-1; compatibility with other versions has not been verified.
- UPower, Python, PyGObject, GTK 3, and Ayatana AppIndicator.
- A connected Logitech MX Master 2S.
- Optional: Solaar, with permission to access the Logitech receiver.

## Install

Install and enable the plugin:

```bash
omarchy plugin add https://github.com/prasetiady/omarchy-mx-master-battery.git --enable
```

The plugin starts the indicator while it is enabled. It uses the existing system tray and does not change its settings or replace the tray widget.

## Update

To install the latest version, run:

```bash
omarchy plugin update prasetiady.mx-master-battery
```

If the tray does not show the changes, restart the shell with `omarchy restart shell`.

## Remove

Disable the plugin with `omarchy plugin disable prasetiady.mx-master-battery`, then remove it with `omarchy plugin remove prasetiady.mx-master-battery`.

## Troubleshoot

If the battery level is unknown, check that the mouse is connected and that Solaar or UPower can read it:

```bash
solaar show 'MX Master 2S'
upower -e
```

Solaar is optional. To inspect a mouse listed by UPower, run `upower -i <device-path>` with its device path from `upower -e`.
