"""Country pie and equirectangular map for the pinned citation reporter.

Boundaries: Natural Earth 1:110m, v5.1.2, public domain.
https://github.com/nvkelso/natural-earth-vector/tree/v5.1.2
Country attribution follows the upstream reporter (first country-coded authorship).
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Polygon
import pandas as pd

BOUNDARIES = Path(__file__).with_name("world-countries.geojson")


def plot_citation_geography(df_country, title_stub, outdir, safe_filename):
    if df_country is None or df_country.empty or df_country["count"].sum() <= 0:
        return None
    counts = df_country.groupby("country")["count"].sum().sort_values(ascending=False)
    top = counts.iloc[:8].copy()
    if len(counts) > 8:
        top = pd.concat([top, pd.Series({"Other": counts.iloc[8:].sum()})])
    features = json.loads(BOUNDARIES.read_text())["features"]
    codes = {f["properties"]["ISO_A2_EH"] for f in features}
    unmapped = int(sum(n for code, n in counts.items() if code not in codes))
    mapped = {code: int(n) for code, n in counts.items() if code in codes and n > 0}
    fig = plt.figure(figsize=(9, 4.68), facecolor="white")
    grid = fig.add_gridspec(2, 2, width_ratios=[1, 2.3], height_ratios=[1, 1.1],
                            left=.02, right=.98, bottom=.22, top=.91, wspace=.12, hspace=.08)
    pie = fig.add_subplot(grid[0, 0])
    wedges, _ = pie.pie(top.values, colors=plt.get_cmap("tab10").colors[:len(top)],
                       startangle=90, wedgeprops={"edgecolor": "white", "linewidth": .6})
    pie.set_title("Country share", fontsize=10)
    legend = fig.add_subplot(grid[1, 0])
    total = counts.sum()
    legend.legend(wedges, [f"{c}: {int(n)} ({n / total:.1%})" for c, n in top.items()],
                  loc="upper center", frameon=False, fontsize=8, handlelength=1)
    legend.axis("off")
    world = fig.add_subplot(grid[:, 1])
    norm = LogNorm(vmin=1, vmax=max(2, max(mapped.values(), default=1)))
    cmap = plt.get_cmap("YlGnBu")
    for feature in features:
        code = feature["properties"]["ISO_A2_EH"]
        if code == "AQ":
            continue
        geometry = feature["geometry"]
        polygons = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
        for polygon in polygons:
            world.add_patch(Polygon(polygon[0], facecolor=cmap(norm(mapped[code])) if code in mapped else "#e5e7eb",
                                    edgecolor="white", linewidth=.25))
    world.set(xlim=(-180, 180), ylim=(-60, 85), aspect="equal")
    world.axis("off")
    world.set_title("Citing publications by country", fontsize=11, pad=12)
    if mapped:
        bar = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=world, orientation="horizontal",
                           fraction=.045, pad=.08, shrink=.8)
        ticks = sorted({1, max(mapped.values())})
        bar.set_ticks(ticks, labels=[str(t) for t in ticks])
        bar.ax.tick_params(labelsize=8)
        bar.set_label("Citing publications (log scale)", fontsize=8)
    else:
        world.text(0, -48, "No mapped country data", ha="center", fontsize=9)
    fig.text(.98, .025, f"Grey: no recorded citations | Unmapped/unknown: {unmapped}\n"
             "Country: first country-coded authorship | Boundaries: Natural Earth (public domain)",
             ha="right", fontsize=7, color="#555555")
    path = Path(outdir) / f"{safe_filename(title_stub)}_citations_by_country.png"
    fig.savefig(path, dpi=190)
    plt.close(fig)
    return str(path)
