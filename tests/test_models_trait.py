from tft.models.trait import Trait, TraitTier

# Shape confirmed against a live fetch of
# https://raw.communitydragon.org/latest/cdragon/tft/en_us.json (set 18) -
# tier breakpoints live under "effects" as {"minUnits", "maxUnits", "style"},
# not "conditionalTraitSets"/"sets"/"min" as originally (wrongly) guessed.
REAL_SHAPE_TRAIT = {
    "apiName": "DA_18_Vanguard",
    "name": "Vanguard",
    "icon": "assets/ux/traiticons/trait_icon_18_vanguard.tex",
    "effects": [
        {"minUnits": 2, "maxUnits": 3, "style": 1},
        {"minUnits": 4, "maxUnits": 5, "style": 3},
        {"minUnits": 6, "maxUnits": 25000, "style": 5},
    ],
}


def test_from_cdragon_parses_real_effects_shape():
    trait = Trait.from_cdragon(REAL_SHAPE_TRAIT)

    assert trait.api_name == "DA_18_Vanguard"
    assert trait.display_name == "Vanguard"
    assert trait.icon_path == "assets/ux/traiticons/trait_icon_18_vanguard.tex"
    assert trait.tiers == (
        TraitTier(min_units=2, style=1),
        TraitTier(min_units=4, style=3),
        TraitTier(min_units=6, style=5),
    )


def test_from_cdragon_handles_missing_effects():
    trait = Trait.from_cdragon({"apiName": "X", "name": "X"})

    assert trait.tiers == ()
    assert trait.icon_path is None
