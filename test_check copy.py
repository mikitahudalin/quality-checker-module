import pandas as pd
from sflab_quality_checker.quality_checker import QualityChecker
# from sflab_quality_checker import quality_checker
# checker = quality_checker.QualityChecker()

db_name = "crawlab"
collection = "upfield_price_track"
task_id = "a715ff5f-d177-4e2b-b10a-6484a3c256d6"
checker = QualityChecker()

checker.load_data(db_name = db_name,
                  task_id = task_id,
                  collection_name = collection)

# print(checker.data.head())

thresholds = {
    "promo_price": {
        "missing_threshold": 0.0,  # max 20% NaN
        "expected_type": "float64"  
    },
    # "old_price": {
    #     "missing_threshold": 0.1,  # max 10% NaN
    #     "expected_type": "float64"
    # },
    "availability": {
        "missing_threshold": 0.0,  # No NaN allowed
        "expected_type": "bool"
    },
    "title": {
        "missing_threshold": 0.0,  # max 10% NaN
        "expected_type": "object"
    }
}
rules = [
    {
        "conditions": [
            {"column": "promo_price", "condition": "isna"},
            {"column": "wrong_page", "condition": "isna"},
            {"column": "availability", "condition": "==", "value": True},
            
        ]
    },
    # {
    #     "conditions": [
    #         {"column": "old_price", "condition": "isna"},
    #         {"column": "price", "condition": "notna"}
    #     ]
    # }
]
checker.load_thresholds(thresholds = thresholds)
checker.load_rules(rules = rules)

missing_values_dict = checker.check_missing_values()
print(f"Missing Values Check:\n {missing_values_dict}\n")

data_types_dict = checker.check_data_types()
print(f"Data Types Check:\n {data_types_dict}\n")

bad_records_summary = checker.check_rules()
print(f"Rules summary: \n {bad_records_summary}")

final_output = checker.merge_outputs(missing_values_dict = checker.check_missing_values(),
                                      data_types_dict = checker.check_data_types(),
                                      bad_records_summary = checker.check_rules())

print(f"Final output: \n {final_output}")
