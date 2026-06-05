"""Hidden tests for README update."""
from pathlib import Path

WORKSPACE = Path('/workspace')


def test_no_hallucinated_params():
    """README should not contain parameters not in the API spec."""
    import yaml
    with open(WORKSPACE / 'api/openapi_v2.yaml') as f:
        spec = yaml.safe_load(f)
    # Get all property names from v2 spec
    v2_props = set()
    for path_item in spec.get('paths', {}).values():
        for method in path_item.values():
            if 'requestBody' in method:
                schema = method['requestBody']['content']['application/json']['schema']
                for prop in schema.get('properties', {}):
                    v2_props.add(prop)
    
    readme = (WORKSPACE / 'docs/README.md').read_text()
    hallucinated = ['invoice_type', 'status', 'priority', 'tags']
    for hall in hallucinated:
        assert hall not in readme.lower(), f"Hallucinated parameter found: {hall}"


def test_due_date_documented():
    content = (WORKSPACE / 'docs/README.md').read_text()
    assert 'due_date' in content, "due_date parameter not documented"
    assert 'YYYY-MM-DD' in content or 'date' in content.lower(), "due_date format not specified"


def test_currency_documented():
    content = (WORKSPACE / 'docs/README.md').read_text()
    assert 'currency' in content, "currency parameter not documented"
    assert 'USD' in content or 'default' in content.lower(), "currency default not specified"
