# XTAG4 Enclosure

A compact, two-piece 3D-printable case for the XMOS XA-XTAG4 debugger. The assembled case measures **59.6 × 34.6 × 11.6 mm**. It provides access to the Micro-USB port and xSYS2 header, with labeled sight holes for the POWER and STATUS LEDs.

## Download

Get both print-oriented STL files and the assembled STEP model from the [latest release](https://github.com/JOYNED-GmbH/xtag4-enclosure/releases/latest).

## Print and assemble

- Print the base and lid in the supplied STL orientations. The outside face of the lid goes on the build plate.
- The parts were test-sliced on a Bambu Lab P2S in PETG at 0.20 mm layer height, with four walls and supports disabled.
- Seat the PCB on the four bosses, lower the lid over the xSYS2 header, and secure it with four M2 × 10 mm thread-forming screws for plastic. The screws pass through the original PCB mounting holes.

The enclosure was modeled against the [XMOS JGB0048 PCB design files](https://www.xmos.com/file/xtag-4-release/). The models passed digital clearance and mesh checks. Physical fit with the board and cable plugs remains untested.

## Edit and rebuild

Fork this repository and edit [`xtag4_enclosure.py`](xtag4_enclosure.py). The parameters at the top of the file are in millimetres. Start with `INNER_GAP` for PCB clearance, `WALL` for wall thickness, and `USB_WIDTH` for the USB opening.

Run these commands from the repository root with Python 3.12. The engravings use Arial Bold, so make that font available to match the release lettering.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install cadquery==2.6.1
python xtag4_enclosure.py
```

The script checks the modeled clearances and writes both STLs and the assembled STEP in the repository root. Keep generated files out of pull requests and describe any fit tests you ran.

## Licence

The enclosure design is licensed under the [CERN Open Hardware Licence Version 2 – Permissive](LICENSE) (`CERN-OHL-P-2.0`).
