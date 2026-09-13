"""Native NiceGUI simulator for the COM243 Product Code Validator."""

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
CATEGORY_OPTIONS = [
    "IT - IT Equipment",
    "EL - Electronics",
    "PR - Peripherals",
    "NW - Networking",
    "OF - Office Hardware",
]


def build_ui() -> None:
    """Build scanner, registration, and inventory workflows."""
    ui.dark_mode().enable()
    ui.add_head_html(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <!-- Inter & JetBrains Mono Fonts -->
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
        <!-- Google Material Icons -->
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        <style>
            body, * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
            .font-mono, .code-text, code, pre { font-family: 'JetBrains Mono', monospace !important; }
            .q-field--standard .q-field__control:before,
            .q-field--standard .q-field__control:after,
            .q-field--filled .q-field__control:before,
            .q-field--filled .q-field__control:after {
                display: none !important;
            }
            .q-field__bottom { display: none !important; }
            .q-table th {
                color: #94a3b8 !important;
                font-weight: 600 !important;
                font-size: 0.75rem !important;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            .q-table td { color: #e2e8f0 !important; font-size: 0.875rem !important; }
            .q-table tbody tr:hover { background: rgba(30, 41, 59, 0.6) !important; }
        </style>
        """,
        shared=True,
    )
    dfa = MinimizedDFA()
    generator = ProductCodeGenerator()

    with ui.column().classes("w-full min-h-screen bg-slate-950 p-6"):
        with ui.row().classes("w-full items-center justify-between"):
            with ui.column().classes("gap-0"):
                ui.label("Product Code Validator").classes("text-2xl font-bold text-white")
                ui.label("What's your DFA - COM243 Simulator").classes("text-sm text-slate-400")
            db_button = ui.button("✕ Database Offline").props("flat dense").classes(
                "rounded-full bg-rose-950 text-rose-400 border border-rose-500 px-3 py-2"
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
                        ).props("outlined dense").classes(f"flex-1 w-full font-mono {INPUT_CLASSES}")
                        scan_button = ui.button("Scan & Validate", color="indigo").classes(
                            "font-semibold"
                        )
                    with ui.row().classes("w-full flex-wrap gap-2 pt-2"):
                        quick_tests = {
                            "Valid Code": lambda: set_code(generator.generate_code()),
                            "Prefix Error": lambda: set_code(generator.generate_corrupted("short_prefix")),
                            "Year Error": lambda: set_code(generator.generate_corrupted("bad_year")),
                            "Dash Error": lambda: set_code(generator.generate_corrupted("dash_error")),
                            "Alphabet Error": lambda: set_code(generator.generate_corrupted("alphabet_error")),
                        }
                        for label, handler in quick_tests.items():
                            ui.button(label, on_click=handler).classes(
                                "bg-slate-850 hover:bg-slate-800 text-slate-300 border border-slate-700 text-xs px-3 py-1 rounded-full font-medium transition-colors"
                            )

                with ui.card().classes(
                    "w-full border-dashed border-2 border-slate-800 bg-slate-900/40 rounded-xl p-4 flex items-center justify-center"
                ):
                    ui.label("DFA TAPE SCANNER").classes("text-sm font-bold text-slate-400")
                    ui.icon("terminal", size="2rem").classes("text-slate-600")
                    tape_row = ui.row().classes("w-full flex-nowrap gap-2 overflow-x-auto py-3")
                    trace_row = ui.row().classes("w-full flex-nowrap gap-2 overflow-x-auto")
                    with trace_row:
                        with ui.column().classes("w-full items-center justify-center py-6 text-slate-500 gap-1"):
                            ui.icon("terminal", size="2rem").classes("text-slate-600")
                            ui.label(
                                "Awaiting input. Enter a code or click a test case above to trace state transitions."
                            ).classes("text-xs text-slate-400")

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
                    ).classes("w-full bg-transparent font-mono")

            with ui.tab_panel(register_tab).classes("min-h-96 items-center justify-center gap-4"):
                with ui.card().classes(f"w-full max-w-lg gap-4 {PANEL_CLASSES}"):
                    ui.label("REGISTER NEW PRODUCT").classes("text-lg font-bold")
                    product_name = ui.input("Product Name").props("outlined dense").classes(f"w-full {INPUT_CLASSES}")
                    price = ui.number("Price in PHP", min=0, precision=2).props("outlined dense").classes(
                        f"w-full {INPUT_CLASSES}"
                    )
                    category = ui.select(
                        CATEGORY_OPTIONS,
                        label="Category",
                        value=CATEGORY_OPTIONS[0],
                    ).props("outlined dense options-dense").classes(f"w-full {INPUT_CLASSES}")
                    register_button = ui.button(
                        "Generate Code & Register Product", color="positive"
                    ).classes("w-full font-semibold")
                    register_result = ui.column().classes("w-full")

            with ui.tab_panel(catalog_tab).classes("gap-4"):
                with ui.row().classes("w-full items-center justify-between"):
                    ui.label("INVENTORY CATALOG").classes("text-xl font-bold")
                    with ui.row().classes("items-center gap-2"):
                        catalog_count = ui.badge("0 products")
                        refresh_catalog_button = ui.button("Refresh", color="indigo")
                catalog_search = ui.input(
                    placeholder="Filter products by name or code..."
                ).props("outlined dense").classes(f"w-full {INPUT_CLASSES}")
                inventory_table = ui.table(
                    columns=[
                        {"name": "id", "label": "ID", "field": "id"},
                        {"name": "product_code", "label": "Code", "field": "product_code"},
                        {"name": "product_name", "label": "Product Name", "field": "product_name"},
                        {"name": "category", "label": "Category", "field": "category"},
                        {"name": "price", "label": "Price", "field": "price"},
                        {"name": "created_at", "label": "Registered Date", "field": "created_at"},
                        {"name": "actions", "label": "Actions", "field": "actions"},
                    ],
                    rows=[],
                    row_key="id",
                ).classes("w-full bg-slate-900 border border-slate-800 rounded-xl font-mono")
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

    def set_connection_state(connected: bool) -> None:
        db_button.text = "● Database Connected" if connected else "✕ Database Offline"
        db_button.classes(
            remove="bg-rose-950 text-rose-400 border-rose-500",
            add="bg-emerald-950 text-emerald-400 border-emerald-500"
            if connected
            else "bg-rose-950 text-rose-400 border-rose-500",
        )
        db_button.update()

    def refresh_connection() -> None:
        connected = db.test_connection()
        set_connection_state(connected)

    def on_db_badge_click() -> None:
        started = time.perf_counter()
        is_up = db.test_connection()
        milliseconds = int((time.perf_counter() - started) * 1000)
        set_connection_state(is_up)
        if is_up:
            ui.notify(
                f"Database connected ({milliseconds} ms)",
                type="positive",
                icon="check_circle",
                position="bottom-right",
                timeout=2500,
            )
        else:
            ui.notify(
                "Database connection failed",
                type="negative",
                icon="error",
                position="bottom-right",
                timeout=2500,
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

    async def scan_code() -> None:
        code = str(code_input.value or "")
        result = dfa.validate(code)
        tape_row.clear()
        trace_row.clear()
        for step in result["steps"]:
            with tape_row:
                ui.label(step["char"]).classes(
                    "rounded bg-slate-800 px-3 py-2 text-lg font-bold font-mono"
                )
            with trace_row:
                chip_color = "bg-rose-700" if step["to_state"] == "q_trap" else "bg-slate-800"
                ui.label(
                    f"[{step['char']}] : [{step['from_state']}] ➔ [{step['to_state']}]"
                ).classes(f"shrink-0 rounded px-3 py-2 {chip_color} font-mono text-sm")
            await asyncio.sleep(0.08)
        scanner_status.clear()
        product_details.clear()
        with scanner_status:
            with ui.card().classes(
                f"w-full {'bg-emerald-800 border border-emerald-500' if result['is_valid'] else 'bg-rose-800 border border-rose-500'} text-white rounded-xl"
            ):
                ui.label(
                    f"VERDICT: {'ACCEPTED' if result['is_valid'] else 'REJECTED'}"
                ).classes("text-xl font-bold")
                ui.label(
                    f"{'Final State' if result['is_valid'] else 'Halt State'}: {result['halt_state']}"
                ).classes("font-mono")
                if not result["is_valid"]:
                    ui.label(f"Reason: {result['error']}")
        if result["is_valid"]:
            product = db.get_product_by_code(code)
            with product_details:
                with ui.card().classes(
                    f"w-full {'bg-amber-900 border border-amber-500 text-amber-100' if product is None else 'bg-slate-900 border border-slate-700'} rounded-xl"
                ):
                    if product is None:
                        ui.label(
                            "Valid Code Syntax (ACCEPTED), but code is not registered in inventory."
                        )
                    else:
                        ui.label(product.get("product_name", "")).classes("text-xl font-bold")
                        ui.label(f"Price: ₱{float(product.get('price', 0)):,.2f}")
                        ui.label(f"Category: {product.get('category', '')}")
                        ui.label(f"Date: {product.get('created_at', '')}")
        db.save_log(
            code,
            "ACCEPTED" if result["is_valid"] else "REJECTED",
            result["halt_state"],
            result["error"],
        )
        refresh_connection()
        refresh_telemetry()

    def parse_category(selection: str) -> str:
        return selection.split(" ", 1)[0]

    async def register_product() -> None:
        register_result.clear()
        name = str(product_name.value or "").strip()
        amount = price.value
        category_code = parse_category(str(category.value or ""))
        if not name or amount is None:
            with register_result:
                ui.label("Enter a product name and price.").classes("text-rose-300")
            return
        code = generator.generate_unique_code(category_code, db.check_code_exists)
        if dfa.validate(code)["is_valid"] and db.insert_product(code, name, float(amount), category_code):
            with register_result:
                with ui.card().classes("w-full bg-emerald-800 border border-emerald-500 text-white rounded-xl"):
                    ui.label("Product registered").classes("text-xl font-bold")
                    ui.label(f"Generated code: {code}").classes("font-mono")
                    ui.label(f"{name} | {category_code} | ₱{float(amount):,.2f}")
            update_catalog()
            refresh_telemetry()
            ui.notify("Product registered", type="positive", timeout=2500)
        else:
            with register_result:
                ui.label("Product could not be registered in the database.").classes("text-rose-300")
        refresh_connection()

    async def scan_catalog_code(code: str) -> None:
        set_code(code)
        tabs.value = scanner_tab
        tabs.update()
        await scan_code()

    def delete_catalog_product(product_id: int) -> None:
        if db.delete_product(product_id):
            update_catalog()
            ui.notify("Product deleted", type="positive", timeout=2500)
        else:
            ui.notify("Product could not be deleted", type="negative", timeout=2500)

    async def handle_scan_event(event: Any) -> None:
        await scan_catalog_code(str(event.args))

    def handle_delete_event(event: Any) -> None:
        delete_catalog_product(int(event.args))

    db_button.on_click(on_db_badge_click)
    inventory_table.on("scan-code", handle_scan_event)
    inventory_table.on("delete-product", handle_delete_event)
    catalog_search.on_value_change(lambda _: render_catalog())
    refresh_catalog_button.on_click(update_catalog)
    scan_button.on_click(scan_code)
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
