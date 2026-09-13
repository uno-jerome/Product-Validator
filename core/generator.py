"""Generate valid and intentionally malformed product codes."""

from __future__ import annotations

import random


class ProductCodeGenerator:
	"""Create product codes matching the minimized DFA's language."""

	CATEGORIES = {
		"IT": "IT Equipment",
		"EL": "Electronics",
		"PR": "Peripherals",
		"NW": "Networking",
		"OF": "Office Hardware",
	}

	def generate_code(
		self,
		category: str = "IT",
		year: int = 2026,
		serial: int | None = None,
	) -> str:
		"""Return a code with a known product category and three-digit serial."""
		if category not in self.CATEGORIES:
			raise ValueError("category must be one of the supported product categories")
		if not isinstance(year, int) or isinstance(year, bool) or not 0 <= year <= 9999:
			raise ValueError("year must be an integer from 0 through 9999")
		if serial is None:
			serial = random.randint(1, 999)
		if not isinstance(serial, int) or isinstance(serial, bool) or not 0 <= serial <= 999:
			raise ValueError("serial must be an integer from 0 through 999")
		return f"{category}-{year:04d}-{serial:03d}"

	def generate_for_category(self, category: str) -> str:
		"""Generate a current-year code for a selected product category."""
		return self.generate_code(category)

	def generate_unique_code(self, category: str, check_db_func) -> str:
		"""Generate a code until the supplied database check reports it is unused."""
		while True:
			code = self.generate_code(category)
			if not check_db_func(code):
				return code

	def generate_corrupted(self, corruption_type: str) -> str:
		"""Return a valid-format code with the requested deliberate defect."""
		valid_code = self.generate_code()

		if corruption_type == "short_prefix":
			return f"I{valid_code[2:]}"
		if corruption_type == "long_prefix":
			return f"ABC{valid_code[2:]}"
		if corruption_type == "bad_year":
			return valid_code.replace("2026", "20A6")
		if corruption_type == "dash_error":
			return valid_code.replace("-", "", 1)
		if corruption_type == "alphabet_error":
			return f"{valid_code[:-1]}!"
		if corruption_type == "bad_serial":
			return f"{valid_code[:-1]}A"
		if corruption_type == "illegal_char":
			return f"{valid_code[:-1]}!"
		raise ValueError(f"Unknown corruption type: {corruption_type}")

	def generate_valid(self) -> str:
		"""Backward-compatible alias for generating a valid product code."""
		return self.generate_code()