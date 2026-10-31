# Safe Exception Runtime

This project is an open-source exception catalog and recovery framework for common standard exceptions in C++, Java, and Python.

The database layer is now designed for MongoDB instead of SQLite.

## What this database stores

- `languages`: language definitions (`C++`, `Java`, `Python`)
- `categories`: exception categories such as `Arithmetic`, `Bounds`, `File IO`, `Memory`, `Type`, etc.
- `exception_catalog`: standard exceptions, metadata, and default recovery policy
- `recovery_rules`: action mapping for each exception type
- `exceptions_history`: events recorded when a real exception is detected and recovered
- `user_defined_exceptions`: separate collection for project-specific exceptions

## MongoDB collection design

### 1) languages
```json
{
  "_id": "cpp",
  "name": "C++"
}
```

### 2) categories
```json
{
  "_id": "bounds",
  "name": "Bounds"
}
```

### 3) exception_catalog
```json
{
  "exception_id": "CPP-STD-001",
  "language_id": "cpp",
  "category_id": "memory",
  "canonical_name": "std::bad_alloc",
  "base_class": "std::exception",
  "description": "Failed to allocate memory",
  "severity": "HIGH",
  "default_recovery": "RETURN_DEFAULT",
  "is_standard": true,
  "is_user_defined": false,
  "aliases": ["bad_alloc", "memory allocation failed"],
  "created_at": { "$date": "2026-10-31T00:00:00Z" }
}
```

### 4) recovery_rules
```json
{
  "exception_id": "PY-STD-001",
  "action": "RETURN_DEFAULT",
  "fallback_value": 0,
  "max_retries": 0,
  "metadata": {
    "notes": "divide by zero fallback"
  }
}
```

### 5) user_defined_exceptions
```json
{
  "_id": "USR-CPP-001",
  "language_id": "cpp",
  "category_id": "logic",
  "class_name": "CustomDatabaseException",
  "project_name": "analytics_app",
  "description": "Custom database failure",
  "recovery_policy": "RETRY"
}
```

## Why MongoDB here

MongoDB works well for this project because:

- exception entries are document-based and easy to evolve
- new aliases, metadata, or tags can be added without schema churn
- standard exceptions and user-defined exceptions can be separated cleanly
- you can query by language, category, severity, or recovered action easily

## Setup

1. Install MongoDB locally or use MongoDB Atlas.
2. Create a `.env` file from `.env.example`.
3. Run:

```bash
python3 scripts/create_mongo_exception_db.py
```

This script builds the exception registry collections and inserts the starter catalog.

## Example runtime flow

1. Exception occurs in the program
2. Program catches exception and extracts name/message
3. System looks up the document in `exception_catalog`
4. If not exact, it searches aliases and category similarity
5. It applies the `recovery_rules` action
6. It logs into `exception_history`
7. If unknown, it rethrows instead of hiding the error silently

## Important note

This project is designed for standard built-in exceptions only. User-defined exceptions are stored separately and are not part of the standard catalog by default.

This library is not a magical global fixer for every program. It is a practical, safe runtime framework for common built-in exceptions.

## License

MIT
