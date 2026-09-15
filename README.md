# Product Code Validator — What's your DFA
> **COM243**  

A native desktop application built with Python, NiceGUI, and MySQL that validates structured inventory product codes using a formally defined and minimized Deterministic Finite Automaton (DFA).

## Table of Contents

- [Product Code Validator — What's your DFA](#product-code-validator--whats-your-dfa)
  - [Table of Contents](#table-of-contents)
  - [1. Formal Language Specification](#1-formal-language-specification)
    - [Regular Expression (RE)](#regular-expression-re)
    - [Formal 5-Tuple DFA Definition](#formal-5-tuple-dfa-definition)
  - [2. Category Domain Schema](#2-category-domain-schema)
  - [3. Project Architecture](#3-project-architecture)
  - [4. Syllabus Compliance Matrix](#4-syllabus-compliance-matrix)
  - [5. Setup \& Installation](#5-setup--installation)
    - [Prerequisites](#prerequisites)
    - [Step 1: Database Setup (UniServer Zero)](#step-1-database-setup-uniserver-zero)
    - [Step 2: Virtual Environment \& Dependencies](#step-2-virtual-environment--dependencies)
  - [6. Running the Project](#6-running-the-project)
    - [Standalone Desktop Application](#standalone-desktop-application)
    - [Automated Unit Tests](#automated-unit-tests)
  - [7. Application User Flows](#7-application-user-flows)

---

## 1. Formal Language Specification

The target language $L$ validates product serial codes categorized by hardware domain:

$$\text{Format: } [A\text{-}Z]^2 - [0\text{-}9]^4 - [0\text{-}9]^3 \quad (\text{e.g., } \texttt{IT-2026-001})$$

### Regular Expression (RE)
$$R = ([A\text{-}Z][A\text{-}Z]) \cdot '-' \cdot ([0\text{-}9][0\text{-}9][0\text{-}9][0\text{-}9]) \cdot '-' \cdot ([0\text{-}9][0\text{-}9][0\text{-}9])$$

### Formal 5-Tuple DFA Definition
The validator is formally defined as $M = (Q, \Sigma, \delta, q_0, F)$:
* **States ($Q$):** $\{q_0, q_1, q_2, q_3, q_4, q_5, q_6, q_7, q_8, q_9, q_{10}, q_{11}, q_{\text{trap}}\}$
* **Alphabet ($\Sigma$):** $\{A\dots Z\} \cup \{0\dots 9\} \cup \{'-'\}$ ($|\Sigma| = 37$)
* **Initial State:** $q_0$
* **Accepting / Final State ($F$):** $\{q_{11}\}$
* **Transition Function ($\delta$):** Pure dictionary lookup transition table mapping $(q_i, \sigma) \to q_{i+1}$. Any symbol not in $\Sigma$ or unexpected at state $q_i$ transitions to $q_{\text{trap}}$.

```text
  [A-Z]       [A-Z]        '-'        [0-9]       [0-9]       [0-9]       [0-9]        '-'        [0-9]       [0-9]       [0-9]
(q0) ───► (q1) ───► (q2) ───► (q3) ───► (q4) ───► (q5) ───► (q6) ───► (q7) ───► (q8) ───► (q9) ───► (q10) ───► ((q11))
  │         │         │         │         │         │         │         │         │         │         │
  └─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴──► [q_trap]
```

---

## 2. Category Domain Schema

| Prefix | Domain Category | Description | Example Assets |
| :---: | :--- | :--- | :--- |
| `IT` | IT Equipment | Enterprise computing infrastructure | Laptops, Rack Servers, Workstations |
| `EL` | Electronics | Internal components & circuitry | Power Supplies, Microcontrollers, ICs |
| `PR` | Peripherals | Input/Output accessories | Mechanical Keyboards, Mice, Monitors |
| `NW` | Networking | Telecommunications & routing | Gigabit Switches, Routers, Patch Panels |
| `OF` | Office Hardware | Physical workplace equipment | Ergonomic Desks, Executive Chairs |

---

## 3. Project Architecture

* **Desktop Framework:** NiceGUI running in native desktop mode via `pywebview`.
* **Database Layer:** PyMySQL connected to local MySQL (UniServer Zero XIII) on port `3306`.
* **Automata Engine:** Pure state-transition dictionary lookups (`core/dfa_engine.py`) without regular expression libraries (`re`) or arithmetic operations.

```text
Product-Validator/
├── core/
│   ├── __init__.py
│   ├── dfa_engine.py     # Formal Minimized DFA implementation
│   └── generator.py      # Category-aware collision-free code generator
├── tests/
│   └── test_dfa.py       # Automated pytest verification suite
├── db.py                 # Resilient PyMySQL database client
├── main.py               # Enterprise desktop UI & state visualizer
├── schema.sql            # MySQL schema (products & validation_logs)
├── requirements.txt      # Python dependencies
└── README.md             # Technical documentation
```

---

## 4. Syllabus Compliance Matrix

| Feature | Requirement Description | Implementation Detail |
| :---: | :--- | :--- |
| **1** | User Input Specification | Monospace text entry supporting structured alphanumeric tokens |
| **2** | Alphabet Validation ($\Sigma$) | Evaluates $\Sigma = \{A\text{-}Z\} \cup \{0\text{-}9\} \cup \{-\}$; flags alphabet violations directly |
| **3** | Symbol-by-Symbol Processing | Evaluates string iteratively using pure $\delta(q, c)$ transition lookups |
| **4** | State Transition Display | Step-by-step visual ticker tape showing $[c]: [q_i] \to [q_{i+1}]$ |
| **5** | Final State Identification | Reports halting at accepting state $q_{11}$ or non-accepting $q_{\text{trap}}$ |
| **6** | Accept/Reject Decision | High-contrast visual verdict (Emerald ACCEPT / Crimson REJECT) |
| **7** | Continuous Testing & Logging | Persistent execution history stored in MySQL `validation_logs` |

---

## 5. Setup & Installation

### Prerequisites
* Python 3.10+
* UniServer Zero XIII (or local MySQL instance running on port `3306`)

### Step 1: Database Setup (UniServer Zero)
1. Start UniServer Zero and ensure MySQL is running on port `3306`.
2. Open phpMyAdmin (`http://localhost/us_opt1/` or your local phpMyAdmin URL).
3. Create the database and import `schema.sql`:
   ```sql
   CREATE DATABASE IF NOT EXISTS automata_validator;
   USE automata_validator;
   ```
4. Run the schema creation queries from `schema.sql`.
5. Verify connection parameters in `db.py`:
   * **Host:** `127.0.0.1`
   * **Port:** `3306`
   * **User:** `root`
   * **Password:** `root`
   * **Database:** `automata_validator`

### Step 2: Virtual Environment & Dependencies
```bash
# Clone the repository
git clone [https://github.com/uno-jerome/Product-Validator.git](https://github.com/uno-jerome/Product-Validator.git)
cd Product-Validator

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 6. Running the Project

### Standalone Desktop Application
Launch the application window:
```bash
python main.py
```

### Automated Unit Tests
Verify the Minimized DFA against valid strings, syntax violations, and alphabet errors without launching the UI:
```bash
pytest tests/test_dfa.py -v
```

---

## 7. Application User Flows

1. **Scanner & Lookup:**
   * Enter a code manually or click a quick-test helper button (`Valid Code`, `Prefix Error`, `Year Error`, `Dash Error`, `Alphabet Error`).
   * Click **SCAN & VALIDATE** to trace the input through the DFA transition dictionary.
   * If `ACCEPTED`, the application searches MySQL to retrieve registration details or displays an unregistered status note.
   * All evaluations are logged to the **Validation History** table.

2. **Register Product:**
   * Enter Product Name, select a Category (`IT`, `EL`, `PR`, `NW`, `OF`), and set Price.
   * View live formatting inside the **Live Asset Tag Preview**.
   * Click **GENERATE CODE & REGISTER PRODUCT** to create a collision-free code, validate it with the DFA engine, and persist it to MySQL.

3. **Inventory Catalog:**
   * Search, filter, and paginate through registered assets.
   * Click **SCAN** on any row to send the product code directly to the validator for live tracing.
   * Click **DELETE** to remove an item from the database.