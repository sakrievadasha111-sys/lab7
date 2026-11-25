REQUIRED = ("id", "field", "type", "status", "debit", "water_cut")

ALLOWED_STATUSES = {"в работе", "в простое", "в консервации"}

RAW_RECORDS = [
    {"id": "SK-101", "field": "Северное", "type": "добывающая",
     "status": "в работе", "debit": 48.5, "water_cut": 12.0},

    {"id": "SK-102", "field": "Северное", "type": "добывающая",
     "status": "в простое", "debit": 0.0, "water_cut": 0.0},

    {"id": "SK-103", "field": "Северное", "type": "нагнетательная",
     "status": "в работе", "debit": 0.0, "water_cut": 0.0},

    {"id": "SK-201", "field": "Южное", "type": "добывающая",
     "status": "в работе", "debit": 96.2, "water_cut": 35.5},

    {"id": "SK-202", "field": "Южное", "type": "добывающая",
     "status": "в работе", "debit": 72.4, "water_cut": 58.0},

    {"id": "SK-203", "field": "Южное", "type": "добывающая",
     "status": "в консервации", "debit": 0.0, "water_cut": 0.0},

    {"id": "SK-301", "field": "Западное", "type": "добывающая",
     "status": "в работе", "debit": 120.0, "water_cut": 61.4},

    {"id": "SK-302", "field": "Западное", "type": "наблюдательная",
     "status": "в простое", "debit": 0.0, "water_cut": 0.0},

    {"id": "SK-104", "field": "Северное", "type": "добывающая",
     "status": "в работе", "debit": "55", "water_cut": 8.0},

    {"id": "SK-204", "field": "Южное", "type": "добывающая",
     "status": "в работе", "water_cut": 44.0},
]


def is_number(value):
    return type(value) in (int, float)

def validate_record(record):
    if type(record) is not dict:
        return "NOT_DICT"

    for key in REQUIRED:
        if key not in record:
            return "MISSING"

    if type(record["id"]) is not str or not record["id"].strip():
        return "BAD_ID"

    if record["status"] not in ALLOWED_STATUSES:
        return "BAD_STATUS"

    if not is_number(record["debit"]) or record["debit"] < 0:
        return "BAD_DEBIT"

    if not is_number(record["water_cut"]):
        return "BAD_WATER_CUT"

    if not 0 <= record["water_cut"] <= 100:
        return "BAD_WATER_CUT"

    return None


def build_registry(raw):
    records, errors, seen = [], [], set()

    for index, record in enumerate(raw):
        code = validate_record(record)

        if code is None and record["id"] in seen:
            code = "DUPLICATE"

        if code is not None:
            errors.append((index, code))
            continue

        seen.add(record["id"])
        records.append(record)

    return records, errors


def aggregate(records, group_field, metric_field):
    result = {}

    for record in records:
        key = record[group_field]
        bucket = result.get(key)

        if bucket is None:
            bucket = {
                "count": 0,
                "sum": 0.0,
                "min": record[metric_field],
                "max": record[metric_field]
            }
            result[key] = bucket

        value = record[metric_field]

        bucket["count"] += 1
        bucket["sum"] += value
        bucket["min"] = min(bucket["min"], value)
        bucket["max"] = max(bucket["max"], value)

    for bucket in result.values():
        bucket["avg"] = bucket["sum"] / bucket["count"]

    return result


def unique_values(records, field):
    return {record[field] for record in records}

def ids_where(records, field, allowed):
    return {
        record["id"] for record in records
        if record[field] in allowed
    }

def ids_in_range(records, field, low, high):
    return {
        record["id"] for record in records
        if low <= record[field] <= high
    }


def print_aggregate(title, data, unit=""):
    print(title)

    for key in sorted(data):
        bucket = data[key]

        print(
            f"{key:<14} "
            f"count={bucket['count']:>2} "
            f"sum={bucket['sum']:>7.1f} "
            f"avg={bucket['avg']:>6.2f} "
            f"min={bucket['min']:>6.1f} "
            f"max={bucket['max']:>6.1f}{unit}"
        ) 


def main():
    records, errors = build_registry(RAW_RECORDS)

    print("Записей во входных данных:", len(RAW_RECORDS))
    print("Корректных записей:", len(records))
    print("Отклонённых записей:", len(errors))

    for index, code in errors:
        print(f"строка {index}: {code}")

    print()
    print_aggregate(
        "Агрегация по месторождению:",
        aggregate(records, "field", "debit")
    )

    print()
    print_aggregate(
        "Агрегация по статусу:",
        aggregate(records, "status", "water_cut"), " %"
    )

    print()
    print("Уникальные месторождения:",
          sorted(unique_values(records, "field")))

    print("Уникальных пар (месторождение, статус):",
          len({(r["field"], r["status"]) for r in records}))

    active = ids_where(records, "status", {"в работе"})
    wet = ids_in_range(records, "water_cut", 60, 100)

    print("Без сортировки:", active)
    print("С сортировкой:", sorted(active))

    print()
    print("В работе:", sorted(active))
    print("Обводнённость 60-100 %:", sorted(wet))

    print("Пересечение:", sorted(active & wet))
    print("Объединение:", sorted(active | wet))
    print("Разность:", sorted(active - wet))
    print("Симметрическая разность:", sorted(active ^ wet))

    print("Все обводнённые входят в работающие:", wet <= active)

    assert sum(
        b["count"]
        for b in aggregate(records, "field", "debit").values()
    ) == len(records)

    print("Проверка инварианта пройдена")

if __name__ == "__main__":
    main()