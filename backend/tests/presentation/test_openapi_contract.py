from fastapi.testclient import TestClient

from presentation.api import create_app


def test_openapi_includes_error_contract() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    openapi_schema = response.json()

    assert "ErrorResponse" in openapi_schema["components"]["schemas"]

    spaces_get_responses = openapi_schema["paths"]["/spaces"]["get"]["responses"]
    assert "400" in spaces_get_responses
    assert "404" in spaces_get_responses
    assert "409" in spaces_get_responses
    assert "422" in spaces_get_responses
    assert "500" in spaces_get_responses
