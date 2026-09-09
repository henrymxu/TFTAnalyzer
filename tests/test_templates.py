import numpy as np

from tft.vision.templates import TemplateLibrary


def _textured_image(seed: int, size: int = 32) -> np.ndarray:
    # Normalized cross-correlation (TM_CCOEFF_NORMED) is degenerate on flat,
    # zero-variance images, so fixtures need real texture like an icon would have.
    rng = np.random.default_rng(seed)
    return rng.integers(0, 255, (size, size, 3), dtype=np.uint8)


def test_best_match_picks_closest_template(tmp_path):
    import cv2

    templates_dir = tmp_path / "champions"
    templates_dir.mkdir()
    ahri_template = _textured_image(seed=1)
    cv2.imwrite(str(templates_dir / "Ahri.png"), ahri_template)
    cv2.imwrite(str(templates_dir / "Jinx.png"), _textured_image(seed=2))

    library = TemplateLibrary(templates_dir)
    assert len(library) == 2

    query = ahri_template  # exact match should win decisively
    match = library.best_match(query, min_confidence=0.5)

    assert match is not None
    assert match.name == "Ahri"


def test_best_match_returns_none_below_confidence_threshold(tmp_path):
    import cv2

    templates_dir = tmp_path / "champions"
    templates_dir.mkdir()
    cv2.imwrite(str(templates_dir / "Ahri.png"), _textured_image(seed=1))

    library = TemplateLibrary(templates_dir)
    unrelated = _textured_image(seed=99)

    match = library.best_match(unrelated, min_confidence=0.999)
    assert match is None


def test_empty_directory_yields_empty_library(tmp_path):
    library = TemplateLibrary(tmp_path / "does-not-exist")
    assert len(library) == 0
    assert library.best_match(_textured_image(seed=1)) is None
