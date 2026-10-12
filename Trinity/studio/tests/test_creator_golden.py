from creator_golden import golden_info_for_product, list_creator_products, list_golden_corpora


def test_registry_lists_two_v2_corpora():
    corpora = list_golden_corpora()
    ids = {c["id"] for c in corpora}
    assert "bigpicture-manual-17844" in ids
    assert "neutral-manual-journeys" in ids
    neutral = next(c for c in corpora if c["id"] == "neutral-manual-journeys")
    assert neutral["path_exists"]
    assert neutral.get("test_count") == 5


def test_products_include_requirements_non_tc():
    products = list_creator_products()
    by_id = {p["product_id"]: p for p in products}
    assert "requirements" in by_id
    req = by_id["requirements"]
    assert req["importer_default_project_key"] == "ONE"
    assert req["golden_corpus_id"] == "neutral-manual-journeys"


def test_bigpicture_uses_bp_corpus():
    info = golden_info_for_product("bigpicture")
    assert info["golden_corpus_id"] == "bigpicture-manual-17844"
    assert info["sampler_ready"] is True


def test_default_uses_neutral_corpus():
    info = golden_info_for_product("default")
    assert info["golden_corpus_id"] == "neutral-manual-journeys"
    assert info["golden_root_exists"] is True
