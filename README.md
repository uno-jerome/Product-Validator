# Product Code Validator — What's your DFA
> **COM243: Theory of Automata & Formal Languages**  
> Desktop Inventory Management & Minimized DFA Simulator

A native desktop application built with Python, NiceGUI, and MySQL that validates structured inventory product codes using a formally defined and minimized Deterministic Finite Automaton (DFA).

---

## 1. Formal Language Specification

The target language $L$ validates product serial codes categorized by department hardware domain:

$$\text{Format: } [A\text{-}Z]^2 - [0\text{-}9]^4 - [0\text{-}9]^3 \quad (\text{e.g., } \texttt{IT-2026-001})$$

### Regular Expression (RE)
$$R = ([A\text{-}Z][A\text{-}Z]) \cdot '-' \cdot ([0\text{-}9][0\text{-}9][0\text{-}9][0\text{-}9]) \cdot '-' \cdot ([0\text{-}9][0\text{-}9][0\text{-}9])$$

### Formal 5-Tuple DFA Definition
The validator is defined as $M = (Q, \Sigma, \delta, q_0, F)$:
* **States ($Q$):** $\{q_0, q_1, q_2, q_3, q_4, q_5, q_6, q_7, q_8, q_9, q_{10}, q_{11}, q_{\text{trap}}\}$
* **Alphabet ($\Sigma$):** $\{A\dots Z\} \cup \{0\dots 9\} \cup \{'-'\}$ ($\vert{}\Sigma\vert{} = 37$)
* **Initial State:** $q_0$
* **Accepting / Final State ($F$):** $\{q_{11}\}$
* **Transition Function ($\delta$):** Pure dictionary lookup transition table mapping $(q_i, \sigma) \to q_{i+1}$. Any invalid symbol or unexpected transition immediately routes to $q_{\text{trap}}$.

---

## 2. Category Domain Schema

| Prefix | Domain Category | Description |
| :--- | :--- | :--- |
| `IT` | IT Equipment | Laptops, Desktops, Servers |
| `EL` | Electronics | Components, Power Supplies, Microcontrollers |
| `PR` | Peripherals | Keyboards, Mice, Monitors, Webcams |
| `NW` | Networking | Routers, Switches, Access Points |
| `OF` | Office Hardware | Ergonomic Desks, Chairs, Physical Assets |

---

## 3. Project Architecture

* **GUI Framework:** NiceGUI running in native desktop mode via `pywebview`.
* **Database Layer:** PyMySQL connected to local MySQL (UniServer Zero XIII) on port 3306.
* **Automata Engine:** Pure transition lookup table (`core/dfa_engine.py`) without external regex libraries or runtime arithmetic.

```text
Product-Validator/
├── core/
│   ├── dfa_engine.py     # Formal Minimized DFA implementation
│   └── generator.py      # Category-based valid code generator
├── db.py                 # Resilient PyMySQL database interface
├── main.py               # Enterprise desktop UI & state visualizer
├── schema.sql            # MySQL table schemas (products & validation_logs)
├── requirements.txt      # Project dependencies
└── README.md