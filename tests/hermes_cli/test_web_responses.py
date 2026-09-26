"""Every dashboard HTTP route documents what it returns in ``/openapi.json``.

The contracts in ``hermes_cli/web_responses`` are attached with ``responses=`` (documentation only), and
``web_responses/check.py`` validates only the statuses a route documents, so nothing but this check stops a
new route from landing with FastAPI's empty ``{}`` success schema.
"""

from fastapi.routing import APIRoute

from hermes_cli import web_server


def _is_fastapi_default(response: dict) -> bool:
    """FastAPI's placeholder for an undocumented route: no description of its own, empty schemas."""
    schemas = [media.get("schema") for media in response.get("content", {}).values()]
    return response.get("description") == "Successful Response" and all(not s for s in schemas)


def test_every_route_documents_its_response():
    spec = web_server.app.openapi()
    undocumented = []
    for route in web_server.app.routes:
        if not isinstance(route, APIRoute) or not route.include_in_schema:
            continue
        for method in route.methods - {"HEAD"} or route.methods:
            responses = spec["paths"][route.path_format][method.lower()]["responses"]
            if all(_is_fastapi_default(r) for code, r in responses.items() if code != "422"):
                undocumented.append(f"{method} {route.path_format} ({route.endpoint.__module__})")
    assert not undocumented, "add a model from hermes_cli/web_responses via responses=:\n" + "\n".join(undocumented)


def test_response_contract_names_are_unique():
    # Two models sharing a class name make FastAPI fall back to module-qualified component names.
    names = web_server.app.openapi()["components"]["schemas"]
    assert not [n for n in names if "__" in n and not n.startswith("Body_")]
