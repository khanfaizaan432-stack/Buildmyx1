import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from mplsoccer import VerticalPitch
import requests
from PIL import Image
from io import BytesIO
import numpy as np
from config import FORMATION_COORDS

PLACEHOLDER_COLOR = "#444444"

def circle_crop_rgba(img_arr):
    h, w = img_arr.shape[:2]
    yy, xx = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    radius = min(w, h) / 2 - 1
    mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= radius ** 2

    out = img_arr.copy()
    if out.shape[2] == 3:
        alpha = np.full((h, w, 1), 255, dtype=np.uint8)
        out = np.concatenate([out, alpha], axis=2)
    out[:, :, 3] = np.where(mask, out[:, :, 3], 0)
    return out

def fetch_image(url, size=(72, 72)):
    try:
        if not url:
            return None
        resp = requests.get(url, timeout=5)
        img  = Image.open(BytesIO(resp.content)).convert("RGBA")
        img  = img.resize(size, Image.LANCZOS)
        return circle_crop_rgba(np.array(img))
    except:
        return None

def draw_pitch(selected_players, formation, tactic):
    pitch = VerticalPitch(
        pitch_type="statsbomb",
        pitch_color="#1f5e38",
        line_color="#e9fff2",
        linewidth=1.8,
        goal_type="box",
    )
    fig, ax = pitch.draw(figsize=(7.5, 10.5))
    fig.patch.set_facecolor("#0b1420")

    # Layer subtle stripes for a more premium pitch texture.
    for stripe_idx in range(12):
        color = "#2a7a49" if stripe_idx % 2 == 0 else "#246c40"
        stripe = mpatches.Rectangle((0, stripe_idx * 10), 80, 10, color=color, alpha=0.32, zorder=0)
        ax.add_patch(stripe)

    # Soft vignette panel around the field.
    frame = mpatches.FancyBboxPatch(
        (-2.5, -2.5), 85, 125,
        boxstyle="round,pad=0.0,rounding_size=5",
        linewidth=2,
        edgecolor="#9de2b8",
        facecolor="none",
        alpha=0.22,
        zorder=2,
    )
    ax.add_patch(frame)

    coords = FORMATION_COORDS.get(formation, {})

    # group players by slot type and index within that type
    from collections import defaultdict
    slot_counters = defaultdict(int)

    for p in selected_players:
        slot      = p["slot"]
        idx       = slot_counters[slot]
        slot_counters[slot] += 1

        pos_list = coords.get(slot, [])
        if idx >= len(pos_list):
            continue

        # statsbomb pitch: x=0-120 (length), y=0-80 (width)
        # Vertical: x becomes visual height (y), y becomes visual width (x)
        coord_x, coord_y = pos_list[idx]
        # our coords are 0-100 scale
        px = coord_x / 100 * 80   # width
        py = coord_y / 100 * 120  # height

        # try to load player image
        img_arr = fetch_image(p["image_url"]) if p.get("image_url") else None

        # Marker halo and circular badge.
        ax.scatter(px, py, s=1200, c="#081014", alpha=0.34, zorder=4)
        ax.scatter(px, py, s=940, c="#f59b2f", edgecolors="white", linewidths=1.5, zorder=5)

        if img_arr is not None:
            img_obj = OffsetImage(img_arr, zoom=0.56)
            ab = AnnotationBbox(
                img_obj, (px, py),
                frameon=False,
                zorder=6,
            )
            ax.add_artist(ab)
        else:
            ax.plot(px, py, "o", color="#0b1f2d", markersize=15, zorder=6)

        # player name label
        short_name = p["Player"].split()[-1] if " " in p["Player"] else p["Player"]
        ax.text(
            px, py - 6, short_name,
            ha="center", va="top", fontsize=8,
            color="white", fontweight="bold",
            bbox=dict(facecolor="#00000088", edgecolor="none", boxstyle="round,pad=0.22")
        )

        # value label
        val_m = p["value"] / 1e6
        ax.text(
            px, py - 10, f"€{val_m:.0f}M",
            ha="center", va="top", fontsize=7, color="#f5a623", fontweight="bold"
        )

    ax.set_title(
        f"{formation}  •  {tactic}",
        color="#f2fff7", fontsize=16, fontweight="bold", pad=18
    )

    return fig
