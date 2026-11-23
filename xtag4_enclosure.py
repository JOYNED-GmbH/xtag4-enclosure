# SPDX-FileCopyrightText: 2026 JOYNED GmbH
# SPDX-License-Identifier: CERN-OHL-P-2.0
# Source: https://github.com/JOYNED-GmbH/xtag4-enclosure
# This source is provided without warranty. See LICENSE.
"""XMOS XA-XTAG4 enclosure, in millimetres. Run with CadQuery 2.6.

XY origin is the lower-left corner of the JGB0048-1V1 board viewed from
above, with micro-USB at X=0. Z=0 is the outside of the base floor.
Board XY dimensions and component centres come from XMOS's release v2.
"""

from pathlib import Path

import cadquery as cq

OUTPUT = Path(__file__).resolve().parent
BOARD_X, BOARD_Y, BOARD_T = 55.0, 30.0, 1.584
HOLES = [(3, 3), (3, 27), (45, 3), (45, 27)]
LEDS = [(32, 27), (32, 22)]
PCB_BOTTOM = 4.05
PCB_TOP = PCB_BOTTOM + BOARD_T
INNER_GAP = 0.45
WALL = 1.85
FLOOR = 1.8
SEAM = 9.10
TOP = 11.60
MARGIN = INNER_GAP + WALL
CX, CY = BOARD_X / 2, BOARD_Y / 2
USB_WIDTH, USB_LOW, USB_HIGH = 14.0, 2.65, 9.65
XSYS_CENTER = (50, 15)
XSYS_WIDTH, XSYS_LENGTH = 8.2, 20.8


def rounded_prism(x, y, length, width, radius, low, high):
    return (
        cq.Workplane("XY")
        .transformed(offset=(x, y, low))
        .box(length, width, high - low, centered=(True, True, False))
        .edges("|Z")
        .fillet(radius)
    )


def block(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def cylinder(x, y, radius, low, high):
    return cq.Solid.makeCylinder(radius, high - low, cq.Vector(x, y, low))


def cone(x, y, bottom_radius, top_radius, low, high):
    return cq.Solid.makeCone(
        bottom_radius, top_radius, high - low, cq.Vector(x, y, low)
    )


def exterior(low, high):
    return rounded_prism(
        CX, CY, BOARD_X + 2 * MARGIN, BOARD_Y + 2 * MARGIN, 3.0, low, high
    )


def usb_opening():
    half = USB_WIDTH / 2
    corner = 0.75
    profile = [
        (CY - half, USB_LOW + corner),
        (CY - half + corner, USB_LOW),
        (CY + half - corner, USB_LOW),
        (CY + half, USB_LOW + corner),
        (CY + half, USB_HIGH),
        (CY - half, USB_HIGH),
    ]
    return (
        cq.Workplane("YZ", origin=(-MARGIN - 1, 0, 0))
        .polyline(profile)
        .close()
        .extrude(MARGIN + 3)
        .val()
    )


def base():
    inside = rounded_prism(
        CX, CY, BOARD_X + 2 * INNER_GAP, BOARD_Y + 2 * INNER_GAP,
        2.05, FLOOR, SEAM + 1,
    ).val()
    shell = exterior(0, SEAM).edges("<Z").chamfer(0.45).val()
    shell = shell.cut(inside, usb_opening())
    for x, y in HOLES:
        shell = shell.fuse(cylinder(x, y, 2.35, FLOOR - 0.05, PCB_BOTTOM))
        pilot = cylinder(x, y, 0.85, 0.9, PCB_BOTTOM + 0.1)
        entry = cone(x, y, 0.85, 1.1, PCB_BOTTOM - 0.25, PCB_BOTTOM)
        shell = shell.cut(pilot, entry)
    return shell.clean()


def lid():
    cover = exterior(SEAM, TOP).edges(">Z").chamfer(0.55).val()
    for x, y in HOLES:
        # Collar bears on the laminate around the PCB's 3.05 mm hole.
        collar = cylinder(x, y, 2.15, PCB_TOP, SEAM + 0.1)
        cover = cover.fuse(collar)

    # Short guide ribs register the lid inside either long wall.
    for y0, y1 in [(-0.18, 0.82), (BOARD_Y - 0.82, BOARD_Y + 0.18)]:
        cover = cover.fuse(block(15, 24, y0, y1, SEAM - 1.05, SEAM + 0.1))

    aperture = rounded_prism(
        *XSYS_CENTER, XSYS_WIDTH, XSYS_LENGTH, 0.75, SEAM - 0.05, TOP + 1
    ).val()
    cover = cover.cut(aperture, usb_opening())
    for x, y in HOLES:
        clearance = cylinder(x, y, 1.16, PCB_TOP - 0.1, TOP + 0.1)
        cover = cover.cut(clearance)

    for x, y in LEDS:
        sight_hole = cylinder(x, y, 1.35, SEAM - 0.1, TOP + 0.1)
        flare = cone(x, y, 2.0, 1.35, SEAM, SEAM + 0.65)
        cover = cover.cut(sight_hole, flare)

    for label, x, y, size in [
        ("XTAG4", 19, 15, 4.6),
        ("P", 36, 27, 2.7),
        ("S", 36, 22, 2.7),
    ]:
        engraving = cq.Workplane("XY", origin=(x, y, TOP - 0.36)).text(
            label, size, 0.5, font="Arial", kind="bold", combine=False
        ).val()
        cover = cover.cut(engraving)
    return cover.clean()


def check_fit(tray, cover):
    board = rounded_prism(CX, CY, BOARD_X, BOARD_Y, 2, PCB_BOTTOM, PCB_TOP).val()
    # The connector is partly recessed into the 1 mm routing notch.
    board = board.cut(block(-1, 1, 10, 20, PCB_BOTTOM - 1, PCB_TOP + 1))
    board = board.cut(*(cylinder(x, y, 1.525, PCB_BOTTOM - 1, PCB_TOP + 1)
                        for x, y in HOLES))
    usb = block(-0.34, 5.32, 11.07, 18.93, PCB_TOP - 0.65, PCB_TOP + 2.75)
    usb_boot = block(-8, -0.34, 8.6, 21.4, 3.05, 9.25)
    header = block(47.15, 52.85, 5.4, 24.6, PCB_TOP, PCB_TOP + 5.6)
    cable_plug = block(46.2, 53.8, 5.0, 25.0, PCB_TOP + 4.9, TOP + 8)
    assert all(shape.isValid() and len(shape.Solids()) == 1 for shape in (tray, cover))
    assert tray.intersect(cover).Volume() < 1e-6
    for part in (board, usb, usb_boot, header, cable_plug):
        assert tray.intersect(part).Volume() < 1e-6
        assert cover.intersect(part).Volume() < 1e-6
    for x, y in HOLES:
        screw_shank = cylinder(x, y, 1.0, PCB_TOP - 0.01, TOP)
        assert cover.intersect(screw_shank).Volume() < 1e-6
    return board, usb, header


def export(tray, cover):
    # Outer face of lid on the build plate, with screw collars facing up.
    print_lid = cover.rotate((0, CY, 0), (1, CY, 0), 180).translate((0, 0, TOP))
    tray.exportStl(str(OUTPUT / "XTAG4-base.stl"), 0.01, 0.08)
    print_lid.exportStl(str(OUTPUT / "XTAG4-lid.stl"), 0.01, 0.08)
    assembly = cq.Assembly(name="XTAG4 enclosure")
    assembly.add(tray, name="Base", color=cq.Color(0.22, 0.27, 0.29))
    assembly.add(cover, name="Lid", color=cq.Color(0.10, 0.14, 0.16))
    assembly.export(str(OUTPUT / "XTAG4-enclosure.step"))


if __name__ == "__main__":
    tray, cover = base(), lid()
    check_fit(tray, cover)
    export(tray, cover)
