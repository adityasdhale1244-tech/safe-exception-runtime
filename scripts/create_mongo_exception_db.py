from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from pymongo import MongoClient
from pymongo.errors import PyMongoError

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "safe_exception_runtime")


def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]


def seed_languages(db):
    languages = [
        {"_id": "cpp", "name": "C++"},
        {"_id": "java", "name": "Java"},
        {"_id": "python", "name": "Python"},
    ]
    db.languages.delete_many({})
    db.languages.insert_many(languages)


def seed_categories(db):
    categories = [
        {"_id": "memory", "name": "Memory"},
        {"_id": "type", "name": "Type"},
        {"_id": "arithmetic", "name": "Arithmetic"},
        {"_id": "io", "name": "IO"},
        {"_id": "file_io", "name": "File IO"},
        {"_id": "bounds", "name": "Bounds"},
        {"_id": "input", "name": "Input"},
        {"_id": "logic", "name": "Logic"},
        {"_id": "runtime", "name": "Runtime"},
        {"_id": "database", "name": "Database"},
        {"_id": "null", "name": "Null"},
        {"_id": "parsing", "name": "Parsing"},
        {"_id": "network", "name": "Network"},
        {"_id": "security", "name": "Security"},
    ]
    db.categories.delete_many({})
    db.categories.insert_many(categories)


def seed_standard_exceptions(db):
    exceptions = [
        {
            "exception_id": "CPP-STD-001",
            "language_id": "cpp",
            "category_id": "memory",
            "canonical_name": "std::bad_alloc",
            "base_class": "std::exception",
            "description": "Failed to allocate memory",
            "severity": "HIGH",
            "default_recovery": "RETURN_DEFAULT",
            "is_standard": True,
            "is_user_defined": False,
            "aliases": ["bad_alloc", "memory allocation failed"],
            "created_at": datetime.now(timezone.utc),
        },
        {
            "exception_id": "CPP-STD-003",
            "language_id": "cpp",
            "category_id": "bounds",
            "canonical_name": "std::out_of_range",
            "base_class": "std::exception",
            "description": "Index or range error",
            "severity": "HIGH",
            "default_recovery": "SAFE_FALLBACK",
            "is_standard": True,
            "is_user_defined": False,
            "aliases": ["out_of_range", "index out of range"],
            "created_at": datetime.now(timezone.utc),
        },
        {
            "exception_id": "JAVA-STD-001",
            "language_id": "java",
            "category_id": "null",
            "canonical_name": "NullPointerException",
            "base_class": "RuntimeException",
            "description": "Null object access",
            "severity": "HIGH",
            "default_recovery": "RETURN_DEFAULT",
            "is_standard": True,
            "is_user_defined": False,
            "aliases": ["null pointer", "NPE"],
            "created_at": datetime.now(timezone.utc),
        },
        {
            "exception_id": "JAVA-STD-002",
            "language_id": "java",
            "category_id": "bounds",
            "canonical_name": "ArrayIndexOutOfBoundsException",
            "base_class": "IndexOutOfBoundsException",
            "description": "Array index invalid",
            "severity": "HIGH",
            "default_recovery": "SAFE_FALLBACK",
            "is_standard": True,
            "is_user_defined": False,
            "aliases": ["index out of bounds", "array index error"],
            "created_at": datetime.now(timezone.utc),
        },
        {
            "exception_id": "PY-STD-001",
            "language_id": "python",
            "category_id": "arithmetic",
            "canonical_name": "ZeroDivisionError",
            "base_class": "ArithmeticError",
            "description": "Division by zero",
            "severity": "HIGH",
            "default_recovery": "RETURN_DEFAULT",
            "is_standard": True,
            "is_user_defined": False,
            "aliases": ["division by zero", "zero division"],
            "created_at": datetime.now(timezone.utc),
        },
        {
            "exception_id": "PY-STD-002",
            "language_id": "python",
            "category_id": "bounds",
            "canonical_name": "IndexError",
            "base_class": "LookupError",
            "description": "Invalid sequence index",
            "severity": "MEDIUM",
            "default_recovery": "SAFE_FALLBACK",
            "is_standard": True,
            "is_user_defined": False,
            "aliases": ["list index out of range", "sequence index invalid"],
            "created_at": datetime.now(timezone.utc),
        },
    ]
    db.exception_catalog.delete_many({})
    db.exception_catalog.insert_many(exceptions)


def seed_recovery_rules(db):
    rules = [
        {"exception_id": "CPP-STD-001", "action": "RETURN_DEFAULT", "fallback_value": 0, "max_retries": 1, "metadata": {"note": "safe default memory allocation fallback"}},
        {"exception_id": "CPP-STD-003", "action": "SAFE_FALLBACK", "fallback_value": 0, "max_retries": 0, "metadata": {"note": "clamp index to valid range"}},
        {"exception_id": "JAVA-STD-001", "action": "RETURN_DEFAULT", "fallback_value": None, "max_retries": 0, "metadata": {"note": "return default null-safe value"}},
        {"exception_id": "JAVA-STD-002", "action": "SAFE_FALLBACK", "fallback_value": 0, "max_retries": 0, "metadata": {"note": "array index recovery"}},
        {"exception_id": "PY-STD-001", "action": "RETURN_DEFAULT", "fallback_value": 0, "max_retries": 0, "metadata": {"note": "divide by zero fallback"}},
        {"exception_id": "PY-STD-002", "action": "SAFE_FALLBACK", "fallback_value": 0, "max_retries": 0, "metadata": {"note": "sequence index fallback"}},
    ]
    db.recovery_rules.delete_many({})
    db.recovery_rules.insert_many(rules)


def seed_user_defined_exceptions(db):
    docs = [
        {
            "_id": "USR-CPP-001",
            "language_id": "cpp",
            "category_id": "logic",
            "class_name": "CustomDatabaseException",
            "project_name": "analytics_app",
            "description": "Custom database failure",
            "recovery_policy": "RETRY",
        },
        {
            "_id": "USR-JAVA-001",
            "language_id": "java",
            "category_id": "database",
            "class_name": "PaymentGatewayException",
            "project_name": "billing_service",
            "description": "Payment service failure",
            "recovery_policy": "RETRY",
        },
        {
            "_id": "USR-PY-001",
            "language_id": "python",
            "category_id": "network",
            "class_name": "NetworkTimeoutException",
            "project_name": "crawler",
            "description": "Remote timeout",
            "recovery_policy": "SAFE_FALLBACK",
        },
    ]
    db.user_defined_exceptions.delete_many({})
    db.user_defined_exceptions.insert_many(docs)


def main():
    db = get_db()
    try:
        seed_languages(db)
        seed_categories(db)
        seed_standard_exceptions(db)
        seed_recovery_rules(db)
        seed_user_defined_exceptions(db)
        print(f"MongoDB seeded successfully: {DB_NAME}")
        print("Collections created: languages, categories, exception_catalog, recovery_rules, user_defined_exceptions")
    except PyMongoError as exc:
        print(f"MongoDB initialization failed: {exc}")
        raise


if __name__ == "__main__":
    main()
