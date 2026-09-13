"""Minimized DFA for department-year-serial product codes."""

from __future__ import annotations


class MinimizedDFA:
	"""Validate product codes matching ``[A-Z]{2}-[0-9]{4}-[0-9]{3}``."""

	accept_state = "q11"
	trap_state = "q_trap"

	def __init__(self) -> None:
		uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		digits = "0123456789"
		self.sigma = set(uppercase + digits + "-")
		self.transitions: dict[str, dict[str, str]] = {
			"q0": {char: "q1" for char in uppercase},
			"q1": {char: "q2" for char in uppercase},
			"q2": {"-": "q3"},
			"q3": {char: "q4" for char in digits},
			"q4": {char: "q5" for char in digits},
			"q5": {char: "q6" for char in digits},
			"q6": {char: "q7" for char in digits},
			"q7": {"-": "q8"},
			"q8": {char: "q9" for char in digits},
			"q9": {char: "q10" for char in digits},
			"q10": {char: "q11" for char in digits},
			"q11": {},
			"q_trap": {},
		}

	def validate(self, code: str) -> dict:
		"""Process ``code`` one character at a time and return its trace."""
		current_state = "q0"
		steps: list[dict] = []
		error: str | None = None

		for step, char in enumerate(code, start=1):
			from_state = current_state
			if char not in self.sigma:
				error = f"Alphabet Violation: Symbol '{char}' not in Sigma"
				current_state = self.trap_state
			else:
				transition = self.transitions.get(current_state, {}).get(char)
				if transition is None:
					error = f"Syntax Violation: Unexpected '{char}' at state {current_state}"
					current_state = self.trap_state
				else:
					current_state = transition
			steps.append(
				{
					"step": step,
					"char": char,
					"from_state": from_state,
					"to_state": current_state,
				}
			)
			if current_state == self.trap_state:
				break

		is_valid = current_state == self.accept_state
		if not is_valid and current_state != self.trap_state:
			incomplete_state = current_state
			current_state = self.trap_state
			error = f"Syntax Violation: Incomplete input at state {incomplete_state}"
		return {
			"is_valid": is_valid,
			"halt_state": current_state,
			"error": error,
			"steps": steps,
		}


SelfCalculatingDFA = MinimizedDFA