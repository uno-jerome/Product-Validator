# Product Code Validator - What's your DFA

A COM243 Formal Languages and Automata Theory simulator that validates product codes with a minimized, table-driven Deterministic Finite Automaton (DFA). The project also provides a native NiceGUI interface for product registration, product lookup, live DFA tracing, and MySQL audit logging.

## Product Code Language

Valid product codes follow this grammar:

```text
[A-Z]{2}-[0-9]{4}-[0-9]{3}
```

Examples:

```text
IT-2026-001
CS-2026-104
HR-2024-999
```

The DFA accepts exactly two uppercase category letters, a four-digit year or batch value, and a three-digit serial number.

## Features

- Pure dictionary-driven DFA validation with no regular expressions.
- Alphabet validation for uppercase letters, digits, and `-`.
- Immediate transition logging and halting at `q_trap`.
- Minimized state topology from `q0` through `q11`, plus `q_trap`.
- Native NiceGUI application with dark mode.
- Product lookup and DFA scanning workflow.
- Product registration workflow for categories `IT`, `HR`, `CS`, `MK`, and `FN`.
- Animated, character-by-character DFA transition trace.
- MySQL persistence for products and validation logs.
- Live UniServer connection status indicator.
- Telemetry table showing the latest ten validation runs.

## Project Layout

```text
ProductValidator/
|-- core/
|   |-- __init__.py
|   |-- dfa_engine.py       # MinimizedDFA implementation
|   `-- generator.py        # Valid and corrupted code generation
|-- database/               # Reserved database project directory
|-- tests/
|   `-- test_dfa.py         # COM243 verification suite
|-- db.py                   # Resilient PyMySQL client
|-- main.py                 # Native NiceGUI application
|-- requirements.txt
|-- schema.sql              # MySQL database and table definitions
|-- .gitignore
`-- README.md
```

The `.github/` directory and instruction files are intentionally excluded by `.gitignore`.

## Requirements

- Python 3.10 or newer
- MySQL 5.7 or newer
- UniServer or another MySQL server listening on port `3306`
- MySQL credentials matching the project configuration:
  - Host: `127.0.0.1`
  - Port: `3306`
  - User: `root`
  - Password: `root`
  - Database: `automata_validator`

## Installation

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On systems where script execution is restricted, run the project with the virtual-environment interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Database Setup

Start MySQL or UniServer on port `3306`, then execute `schema.sql` using SQLyog, the MySQL client, or another SQL tool:

```sql
source schema.sql;
```

The schema creates:

- `products`: product code, name, price, category, and registration timestamp.
- `validation_logs`: input code, ACCEPTED or REJECTED verdict, halt state, failure reason, and timestamp.

The application is designed to remain usable when MySQL is unavailable. Database operations return safe values such as `False`, `None`, or an empty list instead of crashing the UI.

## Running the Application

From the repository root:

```powershell
.\.venv\Scripts\python.exe main.py
```

The native window is configured as:

```text
1150 x 850
Product Code Validator - What's your DFA
```

### Product Lookup & DFA Scanner

1. Enter a product code or use the default `IT-2026-001`.
2. Select `Validate & Search`.
3. Watch the character-by-character transition trace.
4. For accepted syntax, view the registered product details if the code exists in MySQL.
5. Review the validation run in the telemetry table.

Quick test controls provide valid, prefix-error, year-error, and illegal-symbol inputs.

### Register New Product

1. Enter a product name.
2. Enter a PHP price.
3. Select a category.
4. Select `Generate Code & Register Product`.

The application generates a code, validates it through `MinimizedDFA`, and inserts it into the `products` table when valid.

## DFA State Model

| State | Meaning |
|---|---|
| `q0` | Start state |
| `q1` | After the first uppercase letter |
| `q2` | After the second uppercase letter |
| `q3` | After the first dash |
| `q4` | After year digit 1 |
| `q5` | After year digit 2 |
| `q6` | After year digit 3 |
| `q7` | After year digit 4 |
| `q8` | After the second dash |
| `q9` | After serial digit 1 |
| `q10` | After serial digit 2 |
| `q11` | After serial digit 3; accepting state |
| `q_trap` | Dead state for invalid input |

Each trace entry has this structure:

```python
{
    "step": 1,
    "char": "I",
    "from_state": "q0",
    "to_state": "q1",
}
```

## Testing

Run the complete verification suite:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -q
```

The suite covers the COM243 rubric's ten accepted examples, ten rejected examples, minimized transition topology, generator corruption modes, and immediate halt behavior after entering `q_trap`.

Compile the application modules without starting the UI:

```powershell
.\.venv\Scripts\python.exe -m py_compile main.py db.py core\dfa_engine.py core\generator.py
```

## Database API

`db.py` exposes resilient operations:

```python
test_connection() -> bool
save_log(code, verdict, halt_state, reason) -> bool
get_recent_logs(limit=10) -> list[dict]
insert_product(code, name, price, category) -> bool
get_product_by_code(code) -> dict | None
```

All SQL statements use PyMySQL parameter binding, and connections, cursors, transactions, and failures are handled inside the database layer.
