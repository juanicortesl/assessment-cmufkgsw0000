from app.services.pricing import calculate_deed_fee


def test_calculate_notary_fee_standard_tier():
    fee_urgent = calculate_deed_fee("PODER_ESPECIAL", urgent=True)
    assert fee_urgent == 18990
    fee_regular = calculate_deed_fee("PODER_ESPECIAL", urgent=False)
    assert fee_regular == 14990
