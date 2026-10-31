#!/usr/bin/env python3
"""Create the exception registry database.

This script builds the SQLite database for standard exceptions across C++, Java,
and Python, while keeping user-defined exceptions in a separate table.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "exception_registry.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


SCHEMA = """
CREATE TABLE IF NOT EXISTS language (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS category (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS exception_catalog (
    id TEXT PRIMARY KEY,
    language_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    canonical_name TEXT NOT NULL,
    base_class TEXT,
    description TEXT,
    severity TEXT CHECK(severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    default_recovery TEXT,
    is_standard INTEGER DEFAULT 1,
    is_user_defined INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(language_id) REFERENCES language(id),
    FOREIGN KEY(category_id) REFERENCES category(id)
);

CREATE TABLE IF NOT EXISTS exception_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exception_id TEXT NOT NULL,
    alias_name TEXT NOT NULL,
    alias_type TEXT CHECK(alias_type IN ('class', 'message', 'pattern')),
    FOREIGN KEY(exception_id) REFERENCES exception_catalog(id)
);

CREATE TABLE IF NOT EXISTS recovery_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exception_id TEXT NOT NULL,
    action TEXT CHECK(action IN ('RETURN_DEFAULT', 'RETRY', 'LOG_ONLY', 'IGNORE', 'RETHROW', 'SAFE_FALLBACK')) NOT NULL,
    fallback_value TEXT,
    max_retries INTEGER DEFAULT 0,
    metadata TEXT,
    FOREIGN KEY(exception_id) REFERENCES exception_catalog(id)
);

CREATE TABLE IF NOT EXISTS exception_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exception_id TEXT,
    language_id INTEGER,
    thrown_message TEXT,
    stack_trace TEXT,
    occurred_at TEXT DEFAULT CURRENT_TIMESTAMP,
    resolved INTEGER DEFAULT 0,
    resolution_method TEXT,
    FOREIGN KEY(exception_id) REFERENCES exception_catalog(id),
    FOREIGN KEY(language_id) REFERENCES language(id)
);

CREATE TABLE IF NOT EXISTS user_defined_exceptions (
    id TEXT PRIMARY KEY,
    language_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    class_name TEXT NOT NULL,
    project_name TEXT,
    description TEXT,
    recovery_policy TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(language_id) REFERENCES language(id),
    FOREIGN KEY(category_id) REFERENCES category(id)
);
"""

STANDARD_DATA = """
INSERT OR IGNORE INTO language (id, name) VALUES
(1, 'C++'),
(2, 'Java'),
(3, 'Python');

INSERT OR IGNORE INTO category (id, name) VALUES
(1, 'Memory'),
(2, 'Type'),
(3, 'Arithmetic'),
(4, 'IO'),
(5, 'File IO'),
(6, 'Bounds'),
(7, 'Input'),
(8, 'Logic'),
(9, 'Runtime'),
(10, 'Database'),
(11, 'Null'),
(12, 'Parsing'),
(13, 'Network'),
(14, 'Security');

INSERT OR IGNORE INTO exception_catalog (
    id, language_id, category_id, canonical_name, base_class, description, severity, default_recovery, is_standard, is_user_defined
) VALUES
('CPP-STD-001', 1, 1, 'std::bad_alloc', 'std::exception', 'Failed to allocate memory', 'HIGH', 'RETURN_DEFAULT', 1, 0),
('CPP-STD-002', 1, 2, 'std::bad_cast', 'std::exception', 'Invalid dynamic cast', 'MEDIUM', 'LOG_ONLY', 1, 0),
('CPP-STD-003', 1, 6, 'std::out_of_range', 'std::exception', 'Index or range error', 'HIGH', 'SAFE_FALLBACK', 1, 0),
('CPP-STD-004', 1, 3, 'std::overflow_error', 'std::runtime_error', 'Arithmetic overflow', 'HIGH', 'RETURN_DEFAULT', 1, 0),
('CPP-STD-005', 1, 3, 'std::underflow_error', 'std::runtime_error', 'Arithmetic underflow', 'HIGH', 'RETURN_DEFAULT', 1, 0),
('CPP-STD-006', 1, 7, 'std::invalid_argument', 'std::logic_error', 'Invalid function argument', 'MEDIUM', 'RETURN_DEFAULT', 1, 0),
('CPP-STD-007', 1, 9, 'std::runtime_error', 'std::exception', 'General runtime error', 'MEDIUM', 'LOG_ONLY', 1, 0),
('CPP-STD-008', 1, 8, 'std::logic_error', 'std::exception', 'Logic error in program', 'MEDIUM', 'RETHROW', 1, 0),
('JAVA-STD-001', 2, 11, 'NullPointerException', 'RuntimeException', 'Null object access', 'HIGH', 'RETURN_DEFAULT', 1, 0),
('JAVA-STD-002', 2, 6, 'ArrayIndexOutOfBoundsException', 'IndexOutOfBoundsException', 'Array index invalid', 'HIGH', 'SAFE_FALLBACK', 1, 0),
('JAVA-STD-003', 2, 12, 'NumberFormatException', 'IllegalArgumentException', 'Could not parse number', 'MEDIUM', 'RETURN_DEFAULT', 1, 0),
('JAVA-STD-004', 2, 3, 'ArithmeticException', 'RuntimeException', 'Arithmetic failure', 'HIGH', 'RETURN_DEFAULT', 1, 0),
('JAVA-STD-005', 2, 7, 'IllegalArgumentException', 'RuntimeException', 'Invalid argument', 'MEDIUM', 'RETURN_DEFAULT', 1, 0),
('JAVA-STD-006', 2, 4, 'IOException', 'Exception', 'Input/output failure', 'MEDIUM', 'LOG_ONLY', 1, 0),
('JAVA-STD-007', 2, 5, 'FileNotFoundException', 'IOException', 'File not found', 'MEDIUM', 'LOG_ONLY', 1, 0),
('JAVA-STD-008', 2, 10, 'SQLException', 'Exception', 'Database access error', 'HIGH', 'RETRY', 1, 0),
('JAVA-STD-009', 2, 2, 'ClassCastException', 'RuntimeException', 'Invalid cast', 'MEDIUM', 'LOG_ONLY', 1, 0),
('PY-STD-001', 3, 3, 'ZeroDivisionError', 'ArithmeticError', 'Division by zero', 'HIGH', 'RETURN_DEFAULT', 1, 0),
('PY-STD-002', 3, 6, 'IndexError', 'LookupError', 'Invalid sequence index', 'MEDIUM', 'SAFE_FALLBACK', 1, 0),
('PY-STD-003', 3, 7, 'ValueError', 'Exception', 'Incorrect value passed', 'MEDIUM', 'RETURN_DEFAULT', 1, 0),
('PY-STD-004', 3, 2, 'TypeError', 'Exception', 'Wrong type used', 'MEDIUM', 'RETURN_DEFAULT', 1, 0),
('PY-STD-005', 3, 5, 'FileNotFoundError', 'OSError', 'File does not exist', 'MEDIUM', 'LOG_ONLY', 1, 0),
('PY-STD-006', 3, 5, 'PermissionError', 'OSError', 'Permission denied', 'MEDIUM', 'LOG_ONLY', 1, 0),
('PY-STD-007', 3, 1, 'MemoryError', 'Exception', 'Out of memory', 'CRITICAL', 'RETHROW', 1, 0),
('PY-STD-008', 3, 3, 'OverflowError', 'ArithmeticError', 'Integer overflow', 'MEDIUM', 'RETURN_DEFAULT', 1, 0),
('PY-STD-009', 3, 1, 'ImportError', 'Exception', 'Module import failed', 'MEDIUM', 'LOG_ONLY', 1, 0),
('PY-STD-010', 3, 7, 'KeyError', 'LookupError', 'Missing dictionary key', 'MEDIUM', 'SAFE_FALLBACK', 1, 0);

INSERT OR IGNORE INTO recovery_rules (exception_id, action, fallback_value, max_retries, metadata) VALUES
('CPP-STD-001', 'RETURN_DEFAULT', '0', 1, 'safe default memory allocation fallback'),
('CPP-STD-003', 'SAFE_FALLBACK', '0', 0, 'clamp index to valid range'),
('CPP-STD-006', 'RETURN_DEFAULT', '0', 0, 'invalid argument fallback'),
('JAVA-STD-001', 'RETURN_DEFAULT', 'null', 0, 'return default null-safe value'),
('JAVA-STD-002', 'SAFE_FALLBACK', '0', 0, 'array index recovery'),
('JAVA-STD-003', 'RETURN_DEFAULT', '0', 0, 'parse fallback'),
('JAVA-STD-004', 'RETURN_DEFAULT', '0', 0, 'safe arithmetic fallback'),
('PY-STD-001', 'RETURN_DEFAULT', '0', 0, 'divide by zero fallback'),
('PY-STD-002', 'SAFE_FALLBACK', '0', 0, 'sequence index fallback'),
('PY-STD-005', 'LOG_ONLY', 'null', 0, 'file missing allowed as empty result');

INSERT OR IGNORE INTO user_defined_exceptions (
    id, language_id, category_id, class_name, project_name, description, recovery_policy
) VALUES
('USR-CPP-001', 1, 8, 'CustomDatabaseException', 'analytics_app', 'Custom database issue', 'RETRY'),
('USR-JAVA-001', 2, 10, 'PaymentGatewayException', 'billing_service', 'Payment failure', 'RETRY'),
('USR-PY-001', 3, 13, 'NetworkTimeoutException', 'crawler', 'Remote timeout', 'SAFE_FALLBACK');

INSERT OR IGNORE INTO exception_aliases (exception_id, alias_name, alias_type) VALUES
('CPP-STD-003', 'out_of_range', 'class'),
('CPP-STD-003', 'index out of range', 'message'),
('JAVA-STD-002', 'index out of bounds', 'message'),
('PY-STD-001', 'division by zero', 'message'),
('PY-STD-002', 'list index out of range', 'message');
"""


def build_database() -> Path:
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.executescript(STANDARD_DATA)
    conn.commit()
    conn.close()
    return DB_PATH


if __name__ == "__main__":
    db_path = build_database()
    print(f"Database created successfully at: {db_path}")
    print(f"Database size: {db_path.stat().st_size} bytes")
    print("To inspect: sqlite3 data/exception_registry.db '.tables'")
    print("To query: sqlite3 data/exception_registry.db 'SELECT * FROM exception_catalog LIMIT 5;' ")
    print("Note: user-defined exceptions are stored separately in user_defined_exceptions.")
