"""Generate valid and intentionally malformed product codes."""

from __future__ import annotations

import random


class ProductCodeGenerator:
	"""Create product codes matching the minimized DFA's language."""

	def generate_code(self, category: str = "IT", year: int = 2026) -> str:
		"""Return a code with a two-letter category and three-digit serial."""
		if len(category) != 2 or not category.isascii() or not category.isupper():
			raise ValueError("category must contain exactly two uppercase letters")
		if not isinstance(year, int) or isinstance(year, bool) or not 0 <= year <= 9999:
			raise ValueError("year must be an integer from 0 through 9999")
		serial = random.randint(1, 999)
		return f"{category}-{year:04d}-{serial:03d}"

	def generate_corrupted(self, corruption_type: str) -> str:
		"""Return a valid-format code with the requested deliberate defect."""
		valid_code = self.generate_code()

		if corruption_type == "short_prefix":
			return f"I{valid_code[2:]}"
		if corruption_type == "long_prefix":
			return f"ABC{valid_code[2:]}"
		if corruption_type == "bad_year":
			return valid_code.replace("2026", "20A6")
		if corruption_type == "bad_serial":
			return f"{valid_code[:-1]}A"
		if corruption_type == "illegal_char":
			return f"{valid_code[:-1]}!"
		raise ValueError(f"Unknown corruption type: {corruption_type}")

	def generate_valid(self) -> str:
		"""Backward-compatible alias for generating a valid product code."""
		return self.generate_code()