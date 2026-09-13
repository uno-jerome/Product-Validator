# Product Code Validator - What's your DFA

This is a small COM243 simulator built to make a Deterministic Finite Automaton easier to see and understand. Enter a product code, watch it move through the DFA one character at a time, and see whether it reaches the accepting state. The same app also handles product registration, inventory lookup, and validation history through a native NiceGUI interface.

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

In simple terms, a code has a two-letter product category, a four-digit year or batch value, and a three-digit serial number. The supported categories are `IT` (IT Equipment), `EL` (Electronics), `PR` (Peripherals), `NW` (Networking), and `OF` (Office Hardware). The DFA accepts the code only when every character appears in the right place.

## Features

- A table-driven DFA that does not rely on regular expressions.
- Alphabet checking and immediate halting when the machine reaches `q_trap`.
- A minimized state layout from `q0` through `q11`, plus the dead state.
- A native dark-mode interface with three simple tabs: `SCANNER & LOOKUP`, `REGISTER PRODUCT`, and `INVENTORY CATALOG`.
- A live ticker trace that shows each character and its state transition.
- MySQL storage for registered products and validation history.
- A searchable catalog with quick scan and delete actions.
- A connection badge that can be clicked to check UniServer and report latency.

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

The `.github/` directory and instruction files are intentionally excluded by `.gitignore` in this local project setup.

## Requirements

- Python 3.10 or newer
- MySQL 5.7 or newer
- UniServer, or another MySQL server listening on port `3306`
- A MySQL user that matches the current local configuration:
  - Host: `127.0.0.1`
  - Port: `3306`
  - User: `root`
  - Password: `root`
  - Database: `automata_validator`

## Installation

From the project folder, create a virtual environment and install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell does not allow activation scripts, you can use the environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Database Setup

Start MySQL or UniServer on port `3306`. Then run `schema.sql` from SQLyog, the MySQL client, or another SQL tool:

```sql
source schema.sql;
```

The schema creates:

- `products`: product code, name, price, category, and registration timestamp.
- `validation_logs`: input code, ACCEPTED or REJECTED verdict, halt state, failure reason, and timestamp.

The UI can still open when MySQL is unavailable. The database layer reports safe fallback values such as `False`, `None`, or an empty list, and the header makes the connection state visible.

## Running the Application

From the repository root, run:

```powershell
.\.venv\Scripts\python.exe main.py
```

The native window is configured as:

```text
1280 x 880
Product Code Validator - What's your DFA
```

The app opens in a `1280 x 880` native window. The header badge shows whether the database is connected; clicking it checks again and reports the connection latency.

### Product Lookup & DFA Scanner

1. Enter a product code, or start with the default `IT-2026-001`.
2. Click `Scan & Validate`.
3. Follow the character ticker as each symbol moves through the state machine.
4. If the syntax is accepted, the app looks for matching product details in MySQL.
5. Check the audit telemetry panel below the scanner for the saved run.

The quick-test buttons load a valid code or introduce a prefix, year, or symbol error.

### Inventory Catalog

The `INVENTORY CATALOG` tab is the quickest way to browse what is in the database.
Search by product name or code, refresh the list, scan a code in the DFA, or delete a
test product directly from the table.

### Register New Product

1. Enter a product name and PHP price.
2. Choose a product category: IT Equipment, Electronics, Peripherals, Networking, or Office Hardware.
3. Click `Generate Code & Register Product`.

The app generates a code, checks it with `MinimizedDFA`, and saves it to `products` only after it passes validation. The inventory list refreshes as soon as registration succeeds.

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

The suite covers the COM243 rubric's ten accepted examples, ten rejected examples, the transition topology, generator corruption modes, and the rule that tracing stops as soon as the machine enters `q_trap`.

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
get_all_products() -> list[dict]
delete_product(product_id) -> bool
```

All SQL statements use PyMySQL parameter binding with `database="automata_validator"`.
Connections, cursors, transactions, and failures are handled inside the database layer,
so offline MySQL returns safe fallback values instead of crashing the UI.
