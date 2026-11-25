from main import RAW_RECORDS, build_registry

test_records = RAW_RECORDS + [
    dict(RAW_RECORDS[0], debit=-10),
    dict(RAW_RECORDS[0], debit=100)
]

records, errors = build_registry(test_records)

print("Корректных записей:", len(records))

for index, code in errors:
    print(f"Строка {index}: {code}")



