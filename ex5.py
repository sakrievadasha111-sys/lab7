from collections import defaultdict
from main import RAW_RECORDS, build_registry

def aggregate_defaultdict(records, group_field, metric_field):
    groups = defaultdict(list)

    for record in records:
        groups[record[group_field]].append(record[metric_field])

    result = {}

    for key, values in groups.items():
        result[key] = {
            "count": len(values),
            "sum": sum(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values)
        }

    return result

records, _ = build_registry(RAW_RECORDS)

result = aggregate_defaultdict(records, "field", "debit")

for key, value in sorted(result.items()):
    print(key, value)