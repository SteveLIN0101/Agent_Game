from pathlib import Path
def test_uses_correct_params():
    code = (Path('/workspace/examples/create_invoice.py')).read_text()
    assert 'customer_id' in code
    assert 'line_items' in code
    assert 'user' not in code.split('def ')[1] if 'user' in code else True
