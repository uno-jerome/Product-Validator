---
description: Formal Language and Automata constraints for the Product Code Validator project
---

# Product Code Validator — Development Guidelines

## Project Purpose

This project is an academic implementation of a Deterministic Finite Automaton (DFA) that validates product codes and verifies an embedded modulo checksum purely through state transitions.

# Product Code Validator — Formal Language & Project Rules

## Academic Constraints (COM243 Course Specification)
1. Project Identity: "Product Code Validator - What's your DFA" (Example target: `IT-2026-001`).
2. Language Format: `[A-Z]{2}-[0-9]{4}-[0-9]{3}`
   - Prefix: Exactly 2 uppercase letters (Department: IT, HR, CS, etc.).
   - Dash: Exactly one '-' symbol.
   - Batch/Year: Exactly 4 digits (e.g., 2026).
   - Dash: Exactly one '-' symbol.
   - Serial: Exactly 3 digits (e.g., 001 to 999).
3. Automaton Rules:
   - Pure Minimized DFA (states q0 through q11, plus q_trap).
   - No regex (`re` module) allowed in validation logic.
   - Transitions must be strictly table-driven: `state = self.transitions[state][char]`.
4. Required Simulator Capabilities:
   - Validate alphabet membership symbol by symbol.
   - Display step-by-step state transitions.
   - Identify final state and output ACCEPTED or REJECTED.
   - Allow continuous multiple test cases.

## Database & GUI Specifications
- GUI: Native NiceGUI (`ui.run(native=True, window_size=(1150, 850))`).
- Database: MySQL (UniServer 3306, user `root`, password `root`, DB `automata_validator`).
- Functional Flows:
  1. Register Product: Name + Price + Category -> Generates valid code -> Validates via DFA -> Persists to MySQL `products`.
  2. Lookup & Verify: Enter code -> Runs Minimized DFA trace -> If ACCEPTED, fetches product details from MySQL.

## Code Standards

- Use Python 3.10+ type hints (`str`, `dict`, `tuple`, `list`).
- Avoid unhandled KeyErrors by using `.get()` with explicit fallback to `q_trap`.
- Track execution steps in a list of dicts: `[{"step": int, "char": str, "from_state": str, "to_state": str}]`.
