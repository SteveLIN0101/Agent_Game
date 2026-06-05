# Pricing Module

Order pricing and discount calculation service.

## Usage

```python
from src.pricing import calculate_total

price = calculate_total(100, percent_coupon=0.10, fixed_coupon=15)
```

## Development

Run tests: `pytest tests/`
