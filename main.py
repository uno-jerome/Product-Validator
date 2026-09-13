"""Native NiceGUI simulator for the COM243 product-code validator."""

from __future__ import annotations

import asyncio
import time
from typing import Any

from nicegui import ui

import db
from core.dfa_engine import MinimizedDFA
from core.generator import ProductCodeGenerator


PANEL_CLASSES = "w-full bg-slate-900 border border-slate-800 rounded-xl shadow-md"
INPUT_CLASSES = "bg-slate-800 border border-slate-700 text-white rounded-lg p-2"


def build_ui() -> None:
    """Build the scanner, registration, and inventory workflows."""
    ui.dark_mode().enable()
    dfa = MinimizedDFA()
    generator = ProductCodeGenerator()

    with ui.column().classes("w-full min-h-screen bg-slate-950 p-6 font-mono"):
        with ui.row().classes("w-full items-center justify-between"):
            with ui.column().classes("gap-0"):
                ui.label("Product Code Validator").classes("text-2xl font-bold text-white")
                ui.label("What's your DFA - COM243 Simulator").classes("text-sm text-slate-400")
            db_pill = ui.badge("Database Offline").classes(
                "bg-rose-950 border border-rose-500 text-rose-300 cursor-pointer px-3 py-2"
            )

        with ui.tabs().classes(
            "mx-auto rounded-full border border-slate-800 bg-slate-900 p-1"
        ) as tabs:
            scanner_tab = ui.tab("scanner", label="SCANNER & LOOKUP")
            register_tab = ui.tab("register", label="REGISTER PRODUCT")
            catalog_tab = ui.tab("catalog", label="INVENTORY CATALOG")

        with ui.tab_panels(tabs, value=scanner_tab).classes("w-full bg-transparent"):
            with ui.tab_panel(scanner_tab).classes("gap-4"):
                with ui.card().classes(PANEL_CLASSES):
                    with ui.row().classes("w-full items-end gap-3"):
                        code_input = ui.input(
                            "Product code",
                            placeholder="e.g. IT-2026-001",
                            value="IT-2026-001",
                        ).classes(f"flex-1 font-mono {INPUT_CLASSES}")
                        scan_button = ui.button("Scan & Validate", color="indigo").classes(
                            "font-semibold"
                        )
                    with ui.row().classes("w-full flex-wrap gap-2 pt-2"):
                        valid_button = ui.button("Load Valid Code", color="indigo").classes(
                            "bg-slate-800 text-xs text-slate-300"
                        )
                        prefix_button = ui.button("Inject Prefix Error").classes(
                            "bg-slate-800 text-xs text-slate-300"
                        )
                        year_button = ui.button("Inject Year Error").classes(
                            "bg-slate-800 text-xs text-slate-300"
                        )
                        symbol_button = ui.button("Inject Symbol Error").classes(
                            "bg-slate-800 text-xs text-slate-300"
                        )

                with ui.card().classes(PANEL_CLASSES):
                    ui.label("DFA TAPE SCANNER").classes("text-sm font-bold text-slate-400")
                    tape_row = ui.row().classes("w-full flex-nowrap gap-2 overflow-x-auto py-3")
                    trace_row = ui.row().classes("w-full flex-nowrap gap-2 overflow-x-auto")
                    with trace_row:
                        ui.label(
                            "Ready for evaluation. Enter a code above or pick a test case to view symbol transitions."
                        ).classes("text-sm text-slate-500")

                scanner_status = ui.column().classes("w-full")
                product_details = ui.column().classes("w-full")

                with ui.card().classes(PANEL_CLASSES):
                    ui.label("AUDIT TELEMETRY").classes("text-sm font-bold text-slate-400")
                    audit_table = ui.table(
                        columns=[
                            {"name": "id", "label": "ID", "field": "id"},
                            {"name": "input_code", "label": "Code", "field": "input_code"},
                            {"name": "verdict", "label": "Verdict", "field": "verdict"},
                            {"name": "halt_state", "label": "Halt State", "field": "halt_state"},
                            {"name": "created_at", "label": "Timestamp", "field": "created_at"},
                        ],
                        rows=[],
                        row_key="id",
                    ).classes("w-full bg-transparent")

            with ui.tab_panel(register_tab).classes("min-h-96 items-center justify-center gap-4"):
                with ui.card().classes(f"w-full max-w-xl {PANEL_CLASSES}"):
                    ui.label("REGISTER NEW PRODUCT").classes("text-lg font-bold")
                    product_name = ui.input("Product Name").classes(f"w-full {INPUT_CLASSES}")
                    price = ui.number("Price in PHP", min=0, precision=2).classes(
                        f"w-full {INPUT_CLASSES}"
                    )
                    category = ui.select(
                        ["IT", "HR", "CS", "MK", "FN"],
                        label="Department Code",
                        value="IT",
                    ).classes(f"w-full {INPUT_CLASSES}")
                    register_button = ui.button(
                        "Generate Code & Register Product", color="positive"
                    ).classes("w-full font-semibold")
                    register_result = ui.column().classes("w-full")

            with ui.tab_panel(catalog_tab).classes("gap-4"):
                with ui.row().classes("w-full items-center justify-between"):
                    ui.label("INVENTORY CATALOG").classes("text-xl font-bold")
                    with ui.row().classes("items-center gap-2"):
                        catalog_count = ui.badge("0 products")
                        refresh_catalog_button = ui.button("Refresh Catalog", color="indigo")
                catalog_search = ui.input(
                    placeholder="Filter products by name or code..."
                ).classes(f"w-full {INPUT_CLASSES}")
                inventory_table = ui.table(
                    columns=[
                        {"name": "id", "label": "ID", "field": "id"},
                        {"name": "product_code", "label": "Code", "field": "product_code"},
                        {"name": "product_name", "label": "Product Name", "field": "product_name"},
                        {"name": "category", "label": "Category", "field": "category"},
                        {"name": "price", "label": "Price", "field": "price"},
                        {"name": "created_at", "label": "Registered At", "field": "created_at"},
                        {"name": "actions", "label": "Actions", "field": "actions"},
                    ],
                    rows=[],
                    row_key="id",
                ).classes("w-full bg-slate-900 border border-slate-800 rounded-xl")
                inventory_table.add_slot(
                    "body-cell-actions",
                    """
                    <q-td key="actions" :props="props">
                        <q-btn flat dense color="primary" label="Scan"
                            @click="$parent.$emit('scan-code', props.row.product_code)" />
                        <q-btn outline dense color="negative" label="Delete"
                            @click="$parent.$emit('delete-product', props.row.id)" />
                    </q-td>
                    """,
                )

    catalog_rows: list[dict] = []

    def set_badge_state(connected: bool) -> None:
        db_pill.text = "● Database Connected" if connected else "✕ Database Offline"
        db_pill.classes(
            remove="bg-rose-950 border-rose-500 text-rose-300",
            add="bg-emerald-950 border-emerald-500 text-emerald-300"
            if connected
            else "bg-rose-950 border-rose-500 text-rose-300",
        )
        db_pill.update()

    def refresh_connection(show_notification: bool = False) -> None:
        started = time.perf_counter()
        connected = db.test_connection()
        latency_ms = (time.perf_counter() - started) * 1000
        set_badge_state(connected)
        if show_notification:
            ui.notify(
                f"Database {'connected' if connected else 'offline'} - {latency_ms:.0f} ms",
                type="positive" if connected else "negative",
            )

    def refresh_telemetry() -> None:
        audit_table.update_rows(db.get_recent_logs(10))

    def set_code(value: str) -> None:
        code_input.value = value
        code_input.update()

    def format_catalog_rows(rows: list[dict]) -> list[dict]:
        formatted = []
        for row in rows:
            item = dict(row)
            item["price"] = f"₱{float(row.get('raw_price', 0)):,.2f}"
            formatted.append(item)
        return formatted

    def filter_catalog() -> list[dict]:
        query = str(catalog_search.value or "").strip().lower()
        return [
            row
            for row in catalog_rows
            if not query
            or query in str(row.get("product_name", "")).lower()
            or query in str(row.get("product_code", "")).lower()
        ]

    def render_catalog() -> None:
        inventory_table.update_rows(format_catalog_rows(filter_catalog()))
        catalog_count.text = f"{len(catalog_rows)} products"
        catalog_count.update()

    def update_catalog() -> None:
        nonlocal catalog_rows
        catalog_rows = db.get_all_products()
        render_catalog()

    async def scan_catalog_code(code: str) -> None:
        set_code(code)
        tabs.value = scanner_tab
        tabs.update()
        await scan_code()

    def delete_catalog_product(product_id: int) -> None:
        if db.delete_product(product_id):
            update_catalog()
            ui.notify("Product deleted", type="positive")
        else:
            ui.notify("Product could not be deleted", type="negative")

    async def handle_scan_event(event: Any) -> None:
        await scan_catalog_code(str(event.args))

    def handle_delete_event(event: Any) -> None:
        delete_catalog_product(int(event.args))

    async def animate_trace(steps: list[dict[str, Any]]) -> None:
        tape_row.clear()
        trace_row.clear()
        for step in steps:
            with tape_row:
                ui.label(step["char"]).classes(
                    "rounded bg-slate-800 px-3 py-2 text-lg font-bold font-mono"
                )
            with trace_row:
                chip_color = (
                    "bg-rose-700 shadow-lg shadow-rose-500/30"
                    if step["to_state"] == "q_trap"
                    else "bg-slate-800 shadow-lg shadow-indigo-500/20"
                )
                ui.label(
                    f"[{step['char']}] : [{step['from_state']}] ➔ [{step['to_state']}]"
                ).classes(f"shrink-0 rounded px-3 py-2 {chip_color} font-mono text-sm")
            await asyncio.sleep(0.08)

    def show_scan_result(code: str, result: dict[str, Any]) -> None:
        scanner_status.clear()
        product_details.clear()
        accepted = result["is_valid"]
        with scanner_status:
            with ui.card().classes(
                f"w-full {'bg-emerald-800 border border-emerald-500' if accepted else 'bg-rose-800 border border-rose-500'} text-white rounded-xl"
            ):
                ui.label(f"VERDICT: {'ACCEPTED' if accepted else 'REJECTED'}").classes(
                    "text-xl font-bold"
                )
                ui.label(
                    f"{'Final State' if accepted else 'Halt State'}: {result['halt_state']}"
                ).classes("font-mono")
                if not accepted:
                    ui.label(f"Reason: {result['error']}")
        if accepted:
            product = db.get_product_by_code(code)
            with product_details:
                with ui.card().classes(
                    f"w-full {'bg-amber-900 border border-amber-500 text-amber-100' if product is None else 'bg-slate-900 border border-slate-700'} rounded-xl"
                ):
                    if product is None:
                        ui.label(
                            "Code syntax is valid (ACCEPTED), but no matching item was found in the inventory database."
                        )
                    else:
                        ui.label(product.get("product_name", "")).classes("text-xl font-bold")
                        ui.label(f"Price: ₱{float(product.get('price', 0)):,.2f}")
                        ui.label(f"Category: {product.get('category', '')}")
                        ui.label(f"Date: {product.get('created_at', '')}")

    async def scan_code() -> None:
        code = str(code_input.value or "")
        result = dfa.validate(code)
        await animate_trace(result["steps"])
        show_scan_result(code, result)
        db.save_log(
            code,
            "ACCEPTED" if result["is_valid"] else "REJECTED",
            result["halt_state"],
            result["error"],
        )
        refresh_connection()
        refresh_telemetry()

    async def register_product() -> None:
        register_result.clear()
        name = str(product_name.value or "").strip()
        amount = price.value
        group = str(category.value or "")
        if not name or amount is None:
            with register_result:
                ui.label("Enter a product name and price.").classes("text-rose-300")
            return
        code = generator.generate_for_category(group)
        if dfa.validate(code)["is_valid"] and db.insert_product(code, name, float(amount), group):
            with register_result:
                with ui.card().classes("w-full bg-emerald-800 border border-emerald-500 text-white rounded-xl"):
                    ui.label("Product registered").classes("text-xl font-bold")
                    ui.label(f"Generated code: {code}").classes("font-mono")
                    ui.label(f"{name} | {group} | ₱{float(amount):,.2f}")
            update_catalog()
            refresh_telemetry()
            ui.notify("Product registered", type="positive")
        else:
            with register_result:
                ui.label("Product could not be registered in the database.").classes("text-rose-300")
        refresh_connection()

    async def check_connection() -> None:
        refresh_connection(show_notification=True)

    inventory_table.on("scan-code", handle_scan_event)
    inventory_table.on("delete-product", handle_delete_event)
    catalog_search.on_value_change(lambda _: render_catalog())
    refresh_catalog_button.on_click(update_catalog)
    db_pill.on("click", check_connection)
    scan_button.on_click(scan_code)
    valid_button.on_click(lambda: set_code(generator.generate_code()))
    prefix_button.on_click(lambda: set_code(generator.generate_corrupted("short_prefix")))
    year_button.on_click(lambda: set_code(generator.generate_corrupted("bad_year")))
    symbol_button.on_click(lambda: set_code(generator.generate_corrupted("illegal_char")))
    register_button.on_click(register_product)

    refresh_connection()
    refresh_telemetry()
    update_catalog()


def main() -> None:
    build_ui()
    ui.run(
        native=True,
        window_size=(1280, 880),
        title="Product Code Validator - What's your DFA",
        reload=False,
    )


if __name__ == "__main__":
    main()
