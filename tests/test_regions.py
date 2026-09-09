from tft.vision.capture import FractionalRegion
from tft.vision.regions import ScreenLayout


def test_fractional_region_scales_to_pixels():
    region = FractionalRegion(x=0.5, y=0.25, w=0.1, h=0.05)
    pixels = region.to_pixels(1920, 1080)
    assert pixels == {"left": 960, "top": 270, "width": 192, "height": 54}


def test_layout_round_trips_through_json(tmp_path):
    layout = ScreenLayout.empty()
    layout.set_region("gold", FractionalRegion(0.1, 0.2, 0.03, 0.02))
    path = tmp_path / "layout.json"

    layout.save(path)
    reloaded = ScreenLayout.load(path)

    assert "gold" in reloaded
    region = reloaded.get("gold")
    assert (region.x, region.y, region.w, region.h) == (0.1, 0.2, 0.03, 0.02)


def test_missing_region_raises_with_calibration_hint():
    layout = ScreenLayout.empty()
    try:
        layout.get("gold")
        assert False, "expected KeyError"
    except KeyError as exc:
        assert "calibrate" in str(exc)
