import pandas as pd
import json
from scrapfinderlabutils.mongo.mongo_client import ScrapfinderlabMongoClient

from scrapfinderlabutils.aws_client.secret_manager_client import secret_manager

class QualityChecker(object):
    def __init__(self):
  
        self.data = None
        self.task_id = None
        self.collection = None
        self.thresholds = {}
        self.rules = []
        self.client = ScrapfinderlabMongoClient(mongo_uri=secret_manager.get_secret('MONGO_URI'))

# CONNECTION METHODS
    def load_data(self, db_name, task_id: str, collection_name: str):
        """
        Load data from MongoDB using scrapfinder.utils.MongoClient.
        """
        print(type(self.client))  # Should output <class 'MongoClient'>
        query = {"task_id": task_id}
        self.data = pd.DataFrame(self.client.read_data(query = query,
                                                        collection_name = collection_name,
                                                        db_name = db_name))

# CHECKS FOR SEPARATE COLUMNS

    def load_thresholds(self, thresholds: dict):
        """
        Load thresholds from a dictionary.

        thresholds = {
                    "price": {
                        "missing_threshold": 0.2,  # less than 20% NaN
                        "expected_type": "float"
                    },
                    "availability": {
                        "missing_threshold": 0.1  # less than 10% NaN
                    }
                }
        """

        if not isinstance(thresholds, dict):
            raise ValueError("Thresholds must be a dictionary.")
        self.thresholds = thresholds

    def check_missing_values(self) -> dict:
        """
        Check for missing values in the data.
        Return only the columns exceeding the threshold.

        """
        if not self.thresholds:
            return {}
        missing_counts = self.data.isna().sum()
        total_rows = len(self.data)

        exceeded_thresholds = {}
        for col, settings in self.thresholds.items():
            if 'missing_threshold' in settings:
                missing_rate = missing_counts[col] / total_rows
                if missing_rate > settings['missing_threshold']:
                    exceeded_thresholds[col] = {
                        'missing_count': missing_counts[col],
                        'missing_rate': missing_rate,
                        'threshold': settings['missing_threshold']
                    }
        return exceeded_thresholds

    def check_data_types(self) -> dict:
        """
        Check for data type mismatches in the data.
        Return only the columns having mismatches.
        """
        if not self.thresholds:
            return {}
        
        mismatches = {}
        for col, settings in self.thresholds.items():
            if 'expected_type' in settings and col in self.data.columns:
                actual_type = str(self.data[col].dtype)
                expected_type = settings['expected_type']
                if actual_type != expected_type:
                    mismatches[col] = {
                        'actual_type': actual_type,
                        'expected_type': expected_type
                    }
        return mismatches



#CHECKS FOR BAD RECORDS WITH CUSTOM RULES

    def load_rules(self, rules: list[dict]):
        self.rules = rules


    def check_rules(self) -> dict:
        """
        Check for custom rules for BAD RECORDS in the data.
        rules = [
    {
        "conditions": [
            {"column": "promo_price", "condition": "isna"},
            {"column": "wrong_page", "condition": "isna"},
            {"column": "availability", "condition": "==", "value": True},
            
        ]
    },
    {
        "conditions": [
            {"column": "old_price", "condition": "isna"},
            {"column": "price", "condition": "notna"}
        ]
    }
]
        """
        self.data['bad_record'] = False  # all good by default

        for rule in self.rules:
            if "conditions" not in rule:
                continue

            mask = pd.Series(True, index=self.data.index)
            # Start with all True, then apply conditions to filter out bad records
            for condition in rule['conditions']:
                col = condition['column']
                cond_type = condition['condition']

                if col not in self.data.columns:
                    continue  # Skip if column not in data
                # print(f"Processing condition: {condition}, Mask sum before: {mask.sum()}")
                if cond_type == 'isna':
                    mask &= self.data[col].isna()
                elif cond_type == 'notna':
                    mask &= self.data[col].notna()
                elif cond_type == '==':
                    mask &= self.data[col] == condition['value']
                elif cond_type == '!=':
                    mask &= self.data[col] != condition['value']
                else:
                    raise ValueError(f"Unknown condition type: {cond_type}")

                # print(f"Processed condition: {condition}, Mask sum after: {mask.sum()}")

            self.data['bad_record'] |= mask

        bad_records = self.data[self.data["bad_record"]].drop(columns=["bad_record"])
        # Result
        result_json = {
            "bad_records_present": not bad_records.empty,
            "bad_records": [
                {
                    "index": idx,
                    "data": row.to_dict()
                } for idx, row in bad_records.iterrows()
            ]
        }

        return result_json


    def merge_outputs(self, missing_values_dict = None, data_types_dict = None, bad_records_summary = None):
        """
        Merge the outputs of the checks into a single dictionary.
        """
        result = {
            "missing_values": missing_values_dict,
            "data_types": data_types_dict,
            "bad_records": bad_records_summary
        }
        return result
