#!/usr/bin/env python3
"""Overlay preferred and alternate claims on a georeferenced LoC situation-map scan.

Pilot defaults: 27 June 1944, scan cs000022, control tools/loc12ag/sheet3_control.json.
Writes a PNG and a review CSV to a scratch folder. Map images and overlay outputs
are not part of the repository. This tool is not part of the build or run_checks.sh.

Needs numpy and Pillow (same as tools/loc12ag).
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import os
import sys
from datetime import datetime, timedelta

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WW2_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
LOC12AG = os.path.join(WW2_ROOT, "tools", "loc12ag")
sys.path.insert(0, LOC12AG)
import georef as georef  # noqa: E402

DEFAULT_DATE = "1944-06-27"
DEFAULT_SHEET = "cs000022"
DEFAULT_CONTROL = os.path.join(LOC12AG, "sheet3_control.json")
STATUSES = ("preferred", "alternate")
PREFERRED_FILL = (30, 90, 200, 230)
PREFERRED_RING = (30, 90, 200, 150)
ALTERNATE_FILL = (210, 110, 25, 230)
ALTERNATE_RING = (210, 110, 25, 150)
HALO = (0, 0, 0, 255)
LABEL_PREF = (255, 255, 255, 255)
LABEL_ALT = (255, 220, 160, 255)
CSV_COLUMNS = [
    "claim_id",
    "conflict_group_id",
    "claim_status",
    "unit_id",
    "unit_name",
    "nationality",
    "echelon",
    "date",
    "theater",
    "latitude",
    "longitude",
    "place_id",
    "place_name",
    "location_qualifier",
    "location_represents",
    "precision_km",
    "location_date",
    "location_basis",
    "confidence",
    "event_type",
    "current_activity",
    "reference_ids",
    "source_locator",
    "sheet_id",
    "sheet_date",
    "pixel_x",
    "pixel_y",
    "date_lag",
    "map_symbol_px",
    "map_symbol_py",
    "map_lat",
    "map_lon",
    "distance_km",
    "flags",
]


def parse_date(value):
    return datetime.strptime(value[:10], "%Y-%m-%d").date()


def parse_float(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def format_number(value):
    if value is None:
        return ""
    text = str(value)
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def load_csv_by_id(path, key):
    rows = {}
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows[row[key]] = row
    return rows


def load_claims(data_root):
    pattern = os.path.join(data_root, "claims", "*", "*.csv")
    rows = []
    for path in sorted(glob.glob(pattern)):
        with open(path, newline="", encoding="utf-8") as handle:
            rows.extend(csv.DictReader(handle))
    return rows


def sheet_bounds(fit, width, height, scale):
    """Lat/lon box of the image corners in control-point pixel space."""
    native_w = width / scale
    native_h = height / scale
    lons, lats = [], []
    for px, py in ((0, 0), (native_w - 1, 0), (0, native_h - 1), (native_w - 1, native_h - 1)):
        lon, lat = fit(px, py)
        lons.append(lon)
        lats.append(lat)
    return min(lats), max(lats), min(lons), max(lons)


def detect_scale(image_size, control):
    width, height = image_size
    max_x = max(point[0] for point in control)
    max_y = max(point[1] for point in control)
    if max_x < width and max_y < height:
        return 1.0
    for candidate in (0.5, 0.25):
        if max_x * candidate < width and max_y * candidate < height:
            return candidate
    return min(width / max_x, height / max_y)


def precision_radius_px(fit, lon, lat, precision_km, scale):
    if precision_km is None or precision_km <= 0:
        return 0
    x, y = georef.proj(lon, lat)
    lon2, lat2 = georef.unproj(x + precision_km, y)
    px1, py1 = fit.inv(lon, lat)
    px2, py2 = fit.inv(lon2, lat2)
    return max(1, int(round(math.hypot(px2 - px1, py2 - py1) * scale)))


def load_font(size):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ):
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def text_size(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_halo_text(draw, xy, text, font, fill):
    x, y = xy
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                draw.text((x + dx, y + dy), text, font=font, fill=HALO)
    draw.text((x, y), text, font=font, fill=fill)


def boxes_overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def place_label(placed, x, y, width, height, image_size):
    img_w, img_h = image_size
    y0 = y
    for _ in range(40):
        box = (x, y0, x + width, y0 + height)
        if (
            box[0] >= 0
            and box[1] >= 0
            and box[2] <= img_w
            and box[3] <= img_h
            and all(not boxes_overlap(box, other) for other in placed)
        ):
            placed.append(box)
            return x, y0
        y0 += height + 2
        if y0 + height > img_h:
            break
    x = max(0, min(x, img_w - width))
    y = max(0, min(y, img_h - height))
    placed.append((x, y, x + width, y + height))
    return x, y


def draw_diamond(draw, cx, cy, size, outline, width=2):
    points = [
        (cx, cy - size),
        (cx + size, cy),
        (cx, cy + size),
        (cx - size, cy),
    ]
    draw.polygon(points, outline=outline, width=width)


def draw_dashed_ellipse(draw, box, outline, dash=10, gap=6, width=2):
    x0, y0, x1, y1 = box
    rx = (x1 - x0) / 2
    ry = (y1 - y0) / 2
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    if rx <= 0 or ry <= 0:
        return
    circumference = math.pi * (3 * (rx + ry) - math.sqrt((3 * rx + ry) * (rx + 3 * ry)))
    steps = max(24, int(circumference / max(1, dash + gap)))
    for i in range(steps):
        t0 = 2 * math.pi * i / steps
        t1 = 2 * math.pi * (i + dash / (dash + gap)) / steps
        p0 = (cx + rx * math.cos(t0), cy + ry * math.sin(t0))
        p1 = (cx + rx * math.cos(t1), cy + ry * math.sin(t1))
        draw.line([p0, p1], fill=outline, width=width)


def draw_legend(draw, font, origin):
    x, y = origin
    pad = 8
    lines = [
        ("preferred", "filled circle: preferred claim"),
        ("alternate", "open diamond: alternate claim"),
    ]
    width = 0
    height = pad
    sizes = []
    for _, text in lines:
        w, h = text_size(draw, text, font)
        sizes.append((w, h))
        width = max(width, w)
        height += h + 6
    width += pad * 2 + 22
    height += pad
    draw.rectangle([x, y, x + width, y + height], fill=(0, 0, 0, 170), outline=(255, 255, 255, 200))
    cy = y + pad + 8
    for (kind, text), (w, h) in zip(lines, sizes):
        if kind == "preferred":
            draw.ellipse([x + pad, cy - 6, x + pad + 12, cy + 6], fill=PREFERRED_FILL, outline=(255, 255, 255, 255))
        else:
            draw_diamond(draw, x + pad + 6, cy, 6, ALTERNATE_FILL, width=2)
        draw_halo_text(draw, (x + pad + 20, cy - h // 2), text, font, LABEL_PREF)
        cy += h + 6


def select_claims(claims, places, units, fit, sheet_date, window_days, bounds, width, height, scale):
    lat_min, lat_max, lon_min, lon_max = bounds
    start = sheet_date - timedelta(days=window_days)
    end = sheet_date + timedelta(days=window_days)
    selected = []
    skipped = {"status": 0, "date": 0, "coords": 0, "bounds": 0, "off_image": 0}
    for claim in claims:
        status = (claim.get("claim_status") or "").strip()
        if status not in STATUSES:
            skipped["status"] += 1
            continue
        try:
            claim_date = parse_date(claim["date"])
        except (KeyError, ValueError):
            skipped["date"] += 1
            continue
        if claim_date < start or claim_date > end:
            skipped["date"] += 1
            continue
        place = places.get(claim.get("place_id") or "", {})
        unit = units.get(claim.get("unit_id") or "", {})
        lat = parse_float(claim.get("latitude"))
        lon = parse_float(claim.get("longitude"))
        if lat is None or lon is None:
            lat = parse_float(place.get("latitude"))
            lon = parse_float(place.get("longitude"))
        if lat is None or lon is None:
            skipped["coords"] += 1
            continue
        if not (lat_min <= lat <= lat_max and lon_min <= lon <= lon_max):
            skipped["bounds"] += 1
            continue
        native_x, native_y = fit.inv(lon, lat)
        px = int(round(native_x * scale))
        py = int(round(native_y * scale))
        if not (0 <= px < width and 0 <= py < height):
            skipped["off_image"] += 1
            continue
        precision = parse_float(claim.get("precision_km"))
        if precision is None:
            precision = parse_float(place.get("precision_km"))
        selected.append(
            {
                **claim,
                "latitude": f"{lat:.6f}".rstrip("0").rstrip("."),
                "longitude": f"{lon:.6f}".rstrip("0").rstrip("."),
                "place_name": place.get("name", ""),
                "unit_name": claim.get("unit_name") or unit.get("unit_name") or "",
                "precision_km": format_number(precision),
                "_lat": lat,
                "_lon": lon,
                "_precision": precision,
                "_date": claim_date,
                "_px": px,
                "_py": py,
            }
        )
    selected.sort(key=lambda row: (row["_date"].isoformat(), row["unit_id"], row["claim_id"]))
    return selected, skipped


def write_csv(path, rows, sheet_id, sheet_date):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = {key: row.get(key, "") or "" for key in CSV_COLUMNS}
            out["sheet_id"] = sheet_id
            out["sheet_date"] = sheet_date.isoformat()
            out["pixel_x"] = row["_px"]
            out["pixel_y"] = row["_py"]
            out["date_lag"] = (row["_date"] - sheet_date).days
            out["map_symbol_px"] = ""
            out["map_symbol_py"] = ""
            out["map_lat"] = ""
            out["map_lon"] = ""
            out["distance_km"] = ""
            out["flags"] = ""
            if abs(out["date_lag"]) > 1:
                out["flags"] = "date_lag"
            writer.writerow(out)


def render(image, rows, fit, scale, sheet_id, sheet_date, rms):
    base = image.convert("RGBA")
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    font_size = max(12, min(20, base.size[0] // 420))
    font = load_font(font_size)
    marker_r = max(5, int(round(7 * (0.5 if scale < 1 else 1))))
    placed = []

    for row in rows:
        px, py = row["_px"], row["_py"]
        radius = precision_radius_px(fit, row["_lon"], row["_lat"], row["_precision"], scale)
        box = [px - radius, py - radius, px + radius, py + radius]
        if row.get("claim_status") == "alternate":
            if radius:
                draw_dashed_ellipse(draw, box, ALTERNATE_RING, width=2)
            draw_diamond(draw, px, py, marker_r + 1, ALTERNATE_FILL, width=2)
        else:
            if radius:
                draw.ellipse(box, outline=PREFERRED_RING, width=2)
            draw.ellipse(
                [px - marker_r, py - marker_r, px + marker_r, py + marker_r],
                fill=PREFERRED_FILL,
                outline=(255, 255, 255, 255),
            )

    for row in rows:
        px, py = row["_px"], row["_py"]
        label = f"{row.get('unit_id', '')} {row.get('claim_id', '')} {row.get('confidence', '')} {row.get('date', '')}"
        text_w, text_h = text_size(draw, label, font)
        lx, ly = place_label(
            placed,
            px + marker_r + 4,
            py - text_h - 2,
            text_w,
            text_h,
            base.size,
        )
        fill = LABEL_ALT if row.get("claim_status") == "alternate" else LABEL_PREF
        draw_halo_text(draw, (lx, ly), label, font, fill)

    title = (
        f"{sheet_id}  {sheet_date.isoformat()}  "
        f"n={len(rows)}  georef RMS {rms:.2f} km"
    )
    title_font = load_font(font_size + 2)
    tw, th = text_size(draw, title, title_font)
    draw.rectangle([8, 8, 16 + tw, 16 + th], fill=(0, 0, 0, 170))
    draw_halo_text(draw, (12, 12), title, title_font, LABEL_PREF)
    draw_legend(draw, font, (8, base.size[1] - 70))
    return Image.alpha_composite(base, layer).convert("RGB")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Overlay preferred and alternate claims on a LoC situation-map scan."
    )
    parser.add_argument("--date", default=DEFAULT_DATE, help="sheet date (YYYY-MM-DD); default 1944-06-27")
    parser.add_argument("--sheet", default=DEFAULT_SHEET, help="scan id; default cs000022")
    parser.add_argument("--control", default=DEFAULT_CONTROL, help="georef control JSON")
    parser.add_argument("--image", required=True, help="path to the map scan (kept outside git)")
    parser.add_argument("--out", required=True, help="scratch directory for the PNG and CSV (outside git)")
    parser.add_argument("--data-root", default=os.path.join(WW2_ROOT, "data"))
    parser.add_argument("--window-days", type=int, default=1, help="select claims within ±N days; default 1")
    parser.add_argument(
        "--pixel-scale",
        default="auto",
        help="scale from control-point pixels to the image (1.0 full-res, 0.5 for IIIF pct:50, or auto)",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    sheet_date = parse_date(args.date)
    if not os.path.isfile(args.image):
        sys.exit(f"image not found: {args.image}")
    if not os.path.isfile(args.control):
        sys.exit(f"control file not found: {args.control}")
    os.makedirs(args.out, exist_ok=True)

    control_doc = json.load(open(args.control, encoding="utf-8"))
    order = control_doc.get("order", 1)
    if order != 1:
        sys.exit("Fit.inv requires an affine (order=1) control file")
    points = control_doc["control"]
    fit = georef.Fit(points, order)
    rms = float(np.sqrt((fit.res**2).mean()))

    image = Image.open(args.image)
    if args.pixel_scale == "auto":
        scale = detect_scale(image.size, points)
    else:
        scale = float(args.pixel_scale)

    bounds = sheet_bounds(fit, image.size[0], image.size[1], scale)
    places = load_csv_by_id(os.path.join(args.data_root, "places.csv"), "place_id")
    units = load_csv_by_id(os.path.join(args.data_root, "units.csv"), "unit_id")
    claims = load_claims(args.data_root)
    selected, skipped = select_claims(
        claims,
        places,
        units,
        fit,
        sheet_date,
        args.window_days,
        bounds,
        image.size[0],
        image.size[1],
        scale,
    )

    stem = f"overlay_{args.sheet}_{sheet_date.isoformat()}"
    png_path = os.path.join(args.out, f"{stem}.png")
    csv_path = os.path.join(args.out, f"{stem}.csv")
    render(image, selected, fit, scale, args.sheet, sheet_date, rms).save(png_path)
    write_csv(csv_path, selected, args.sheet, sheet_date)

    n_pref = sum(1 for row in selected if row.get("claim_status") == "preferred")
    n_alt = sum(1 for row in selected if row.get("claim_status") == "alternate")
    print("residuals km:", np.round(fit.res, 2), "rms", round(rms, 2))
    print(
        "sheet bounds lat [{:.4f}, {:.4f}] lon [{:.4f}, {:.4f}]".format(*bounds)
    )
    print(f"pixel scale: {scale}")
    print(f"n claims: {len(selected)} ({n_pref} preferred, {n_alt} alternate)")
    print(f"skipped: {skipped}")
    print(f"wrote {png_path}")
    print(f"wrote {csv_path}")
    if selected:
        print("sample:")
        for row in selected[:8]:
            print(
                f"  {row['claim_id']} {row['claim_status']} {row['unit_id']} "
                f"{row['date']} {row['_lat']},{row['_lon']} "
                f"px=({row['_px']},{row['_py']}) "
                f"lag={(row['_date'] - sheet_date).days} "
                f"conf={row.get('confidence', '')}"
            )


if __name__ == "__main__":
    main()
