from time_tracker_api.security import parse_jwt, parse_tenant_id_from_iss_claim


def test_parse_jwt_with_valid_input(valid_jwt: str):
    result = parse_jwt("Bearer %s" % valid_jwt)

    assert result is not None
    assert type(result) is dict


def test_parse_jwt_with_invalid_input():
    result = parse_jwt("whetever")

    assert result is None


def test_parse_tenant_id_from_iss_claim_with_valid_input():
    valid_iss_claim = "https://securityioet.b2clogin.com/b21c4e98-c4bf-420f-9d76-e51c2515c7a4/v2.0/"

    result = parse_tenant_id_from_iss_claim(valid_iss_claim)

    assert result is not None
    assert type(result) is str
    assert result == "b21c4e98-c4bf-420f-9d76-e51c2515c7a4"


def test_parse_tenant_id_from_iss_claim_with_invalid_input():
    invalid_iss_claim1 = "https://securityioet.b2clogin.com/whatever/v2.0/"
    invalid_iss_claim2 = ""

    result1 = parse_tenant_id_from_iss_claim(invalid_iss_claim1)
    result2 = parse_tenant_id_from_iss_claim(invalid_iss_claim2)

    assert result1 == result2 == None
