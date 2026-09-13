"""Native NiceGUI simulator for the COM243 product-code validator."""

from __future__ import annotations

import asyncio
from typing import Any

from nicegui import ui

import db
from core.dfa_engine import MinimizedDFA
from core.generator import ProductCodeGenerator


def build_ui() -> None:
	"""Build lookup/scanning and product-registration workflows."""
	ui.dark_mode().enable()

	dfa = MinimizedDFA()
	generator = ProductCodeGenerator()

	with ui.column().classes("w-full max-w-7xl mx-auto gap-5 p-6"):
		with ui.row().classes("w-full items-center justify-between"):
			with ui.column().classes("gap-0"):
				ui.label("Product Code Validator - What's your DFA").classes(
					"text-2xl font-bold tracking-wide"
				)
				ui.label("COM243 simulator").classes("text-sm text-slate-400")
			db_badge = ui.label().classes(
				"rounded-full px-3 py-1 text-sm font-semibold text-white"
			)

		with ui.tabs().classes("w-full") as tabs:
			lookup_tab = ui.tab("lookup", label="Product Lookup & DFA Scanner")
			register_tab = ui.tab("register", label="Register New Product")

		with ui.tab_panels(tabs, value=lookup_tab).classes("w-full"):
			with ui.tab_panel(lookup_tab).classes("gap-4"):
				with ui.card().classes("w-full"):
					ui.label("Lookup and scan a product code").classes(
						"text-lg font-semibold"
					)
					code_input = ui.input(
						value="IT-2026-001",
						label="Product code",
					).classes("w-full font-mono")
					validate_button = ui.button(
						"Validate & Search", color="primary"
					).classes("font-semibold")
					ui.label("Quick tests").classes("mt-2 text-sm font-semibold")
					with ui.row().classes("w-full flex-wrap gap-2"):
						valid_button = ui.button("Load Valid Code")
						prefix_button = ui.button("Inject Prefix Error")
						year_button = ui.button("Inject Year Error")
						symbol_button = ui.button("Inject Symbol Error")

			with ui.card().classes("w-full"):
				ui.label("Live animated trace").classes("text-lg font-semibold")
				trace_row = ui.row().classes("w-full flex-nowrap gap-2 overflow-x-auto")

			lookup_status = ui.column().classes("w-full")
			lookup_product = ui.column().classes("w-full")

			with ui.tab_panel(register_tab).classes("gap-4"):
				with ui.card().classes("w-full"):
					ui.label("Register a product").classes("text-lg font-semibold")
					product_name = ui.input(label="Product Name").classes("w-full")
					with ui.row().classes("w-full gap-4"):
						price = ui.number(
							label="Price",
							prefix="PHP ",
							min=0,
							precision=2,
						).classes("flex-1")
						category = ui.select(
							["IT", "HR", "CS", "MK", "FN"],
							label="Category",
							value="IT",
						).classes("flex-1")
					register_button = ui.button(
						"Generate Code & Register Product", color="primary"
					).classes("font-semibold")
				register_result = ui.column().classes("w-full")

		ui.label("Telemetry - latest validation runs").classes(
			"text-lg font-semibold"
		)
		audit_table = ui.table(
			columns=[
				{"name": "id", "label": "ID", "field": "id", "sortable": True},
				{"name": "input_code", "label": "Code", "field": "input_code"},
				{"name": "verdict", "label": "Verdict", "field": "verdict"},
				{"name": "halt_state", "label": "Halt State", "field": "halt_state"},
				{"name": "created_at", "label": "Timestamp", "field": "created_at"},
			],
			rows=[],
			row_key="id",
		).classes("w-full")

	def refresh_connection_badge() -> None:
		connected = db.test_connection()
		db_badge.text = "UniServer Connected" if connected else "UniServer Unreachable"
		db_badge.style(
			"background-color: #15803d;" if connected else "background-color: #b91c1c;"
		)

	def refresh_telemetry() -> None:
		audit_table.rows = db.get_recent_logs(10)
		audit_table.update()

	def set_code(value: str) -> None:
		code_input.value = value
		code_input.update()

	async def animate_trace(steps: list[dict[str, Any]]) -> None:
		trace_row.clear()
		for step in steps:
			with trace_row:
				ui.label(
					f"[{step['char']}] : {step['from_state']} -> {step['to_state']}"
				).classes("shrink-0 rounded bg-slate-800 px-3 py-2 font-mono text-sm")
			await asyncio.sleep(0.08)

	def show_lookup_result(code: str, result: dict[str, Any]) -> None:
		lookup_status.clear()
		lookup_product.clear()
		accepted = result["is_valid"]
		verdict = "ACCEPTED" if accepted else "REJECTED"
		banner_color = "bg-green-700" if accepted else "bg-red-700"
		reason = result["error"] or "Syntax accepted"
		with lookup_status:
			with ui.card().classes(f"w-full {banner_color} text-white"):
				ui.label(verdict).classes("text-xl font-bold")
				ui.label(f"Final state: {result['halt_state']}").classes("font-mono")
				if not accepted:
					ui.label(f"Reason: {reason}")
		if accepted:
			product = db.get_product_by_code(code)
			with lookup_product:
				with ui.card().classes("w-full"):
					if product is None:
						ui.label("Syntax Valid, but not registered in database.")
					else:
						ui.label("Registered product").classes("text-lg font-semibold")
						ui.label(f"Product Name: {product.get('product_name', '')}")
						ui.label(f"Category: {product.get('category', '')}")
						ui.label(f"Price: PHP {product.get('price', '')}")
						ui.label(f"Registration Date: {product.get('created_at', '')}")

	async def validate_and_search() -> None:
		code = str(code_input.value or "")
		result = dfa.validate(code)
		await animate_trace(result["steps"])
		show_lookup_result(code, result)
		verdict = "ACCEPTED" if result["is_valid"] else "REJECTED"
		db.save_log(code, verdict, result["halt_state"], result["error"])
		refresh_connection_badge()
		refresh_telemetry()

	def show_registration_result(code: str, name: str, amount: float, group: str) -> None:
		register_result.clear()
		with register_result:
			with ui.card().classes("w-full bg-green-700 text-white"):
				ui.label("Product registered").classes("text-xl font-bold")
				ui.label(f"Generated code: {code}").classes("font-mono")
				ui.label(f"Product Name: {name}")
				ui.label(f"Category: {group} | Price: PHP {amount:.2f}")

	async def register_product() -> None:
		name = str(product_name.value or "").strip()
		amount = price.value
		group = str(category.value or "")
		register_result.clear()
		if not name or amount is None or not group:
			with register_result:
				ui.label("Enter a product name, price, and category.").classes("text-red-400")
			return
		code = generator.generate_code(group)
		result = dfa.validate(code)
		if not result["is_valid"]:
			with register_result:
				ui.label("Generated code failed DFA validation.").classes("text-red-400")
			return
		if db.insert_product(code, name, float(amount), group):
			show_registration_result(code, name, float(amount), group)
		else:
			with register_result:
				ui.label("Product could not be registered in the database.").classes("text-red-400")
		refresh_connection_badge()
		refresh_telemetry()

	validate_button.on_click(validate_and_search)
	valid_button.on_click(lambda: set_code(generator.generate_code()))
	prefix_button.on_click(lambda: set_code(generator.generate_corrupted("short_prefix")))
	year_button.on_click(lambda: set_code(generator.generate_corrupted("bad_year")))
	symbol_button.on_click(lambda: set_code(generator.generate_corrupted("illegal_char")))
	register_button.on_click(register_product)

	refresh_connection_badge()
	refresh_telemetry()


def main() -> None:
	build_ui()
	ui.run(
		native=True,
		window_size=(1150, 850),
		title="Product Code Validator - What's your DFA",
		reload=False,
	)


if __name__ == "__main__":
	main()