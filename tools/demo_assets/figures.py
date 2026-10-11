"""The figure the notebook shows after "Load Masks & Extract Features": the same plotting calls as NucleiSky2DApp.ipynb (offline tool)."""

from pathlib import Path


def segmentation_figure(lib: dict, data: dict, out: Path) -> None:
    """Full image and crop with their nucleus centroids in red, drawn as the notebook draws them (the image is below its 5000 px limit,
    so the notebook hides the two lower panels, which are left out here to avoid empty space); written as seg_figure.webp."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from PIL import Image
    viz, feat = lib["visualization"], lib["features"]
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    for col, (key, df, name) in enumerate((("full", data["df_full"], "Full"), ("crop", data["df_crop"], "Crop"))):
        img = data[key]
        shown = viz.imshow_safe(ax[col], img, title=f"{name} ({len(df)})")
        cent = feat.centroids_from_df(df, use_um=False, use_orig_px=True)
        safe = viz.downsample_points_for_display(cent)
        ax[col].scatter(safe[:, 1] * shown.shape[1] / img.shape[1], safe[:, 0] * shown.shape[0] / img.shape[0], s=1 if key == "full" else 6, c="r", alpha=0.5)
    png = out / "seg_figure.png"
    fig.savefig(png, dpi=100, bbox_inches="tight")
    plt.close(fig)
    with Image.open(png) as im:
        im.convert("RGB").save(out / "seg_figure.webp", "WEBP", quality=80, method=6)
    png.unlink()
