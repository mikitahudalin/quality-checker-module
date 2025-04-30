# QualityChecker

**QualityChecker** is a Python module designed to validate and assess the quality of scraped data, especially from MongoDB collections. It provides utilities to check for:

- Missing values  
- Data type mismatches  
- Custom rule-based identification of bad records

The module is built for integration into data scraping and ETL pipelines.

---

## Installation

```bash
pip install quality-checker  # if published to PyPI
# or clone manually:
git clone https://your.repo.url
```

---

## Dependencies

- `pandas`
- `sflabutils` — a custom internal library used for MongoDB and AWS Secrets Manager integration.  
  > **Note:** This can be replaced with standard packages such as `pymongo` and `boto3`.

---

## Usage Example

```python
from quality_checker.quality_checker import QualityChecker

checker = QualityChecker()

checker.load_data(
    db_name="crawlab",
    task_id="your-task-id",
    collection_name="your-collection"
)

thresholds = {
    "promo_price": {
        "missing_threshold": 0.0,
        "expected_type": "float64"
    },
    "availability": {
        "missing_threshold": 0.0,
        "expected_type": "bool"
    }
}

rules = [
    {
        "conditions": [
            {"column": "promo_price", "condition": "isna"},
            {"column": "wrong_page", "condition": "isna"},
            {"column": "availability", "condition": "==", "value": True},
        ]
    }
]

checker.load_thresholds(thresholds)
checker.load_rules(rules)

missing = checker.check_missing_values()
types = checker.check_data_types()
bad = checker.check_rules()

final = checker.merge_outputs(
    missing_values_dict=missing,
    data_types_dict=types,
    bad_records_summary=bad
)

print(final)
```

---

## API Reference

### `load_data(db_name, task_id, collection_name)`

Loads data from a MongoDB collection filtered by `task_id`.

### `load_thresholds(thresholds: dict)`

Loads column-specific validation thresholds for missing values and expected data types.

**Example:**
```python
{
    "price": {
        "missing_threshold": 0.1,
        "expected_type": "float64"
    }
}
```

### `check_missing_values() -> dict`

Checks each column for missing values that exceed the defined threshold.

### `check_data_types() -> dict`

Verifies that each column's data type matches the expected type.

### `load_rules(rules: list[dict])`

Loads a set of custom rules for identifying "bad records."

**Example:**
```python
[
    {
        "conditions": [
            {"column": "promo_price", "condition": "isna"},
            {"column": "availability", "condition": "==", "value": True}
        ]
    }
]
```

### `check_rules() -> dict`

Applies the loaded rules and returns all records that meet the "bad" criteria.

### `merge_outputs(...) -> dict`

Combines the results of missing values check, type validation, and bad record rules into a unified report.

---

## Notes

This module depends on internal utilities from `sflabutils`:

- `ScrapfinderlabMongoClient` — used to connect to MongoDB
- `secret_manager` — used to fetch credentials from AWS Secrets Manager

You may substitute these with:

- `pymongo.MongoClient`  
- `boto3.client('secretsmanager')`

---

## Roadmap / TODO

- Logging support  
- Spark DataFrame support  
- HTML report generation
