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
INPUT_CLASSES = "bg-slate-800/70 text-white rounded-lg p-2"
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
            .font-mono, .code-token, pre, code { font-family: 'JetBrains Mono', monospace !important; }
            body { background-color: #0b0f19 !important; color: #f8fafc; }
            .q-field--outlined .q-field__control {
                background-color: #111827 !important;
                border-radius: 8px !important;
                border: 1px solid #1e293b !important;
                transition: border-color 0.2s ease;
            }
            .q-field--outlined.q-field--focused .q-field__control { border-color: #6366f1 !important; }
            .q-field--outlined .q-field__control:before,
            .q-field--outlined .q-field__control:after,
            .q-field--standard .q-field__control:before,
            .q-field--standard .q-field__control:after,
            .q-field--filled .q-field__control:before,
            .q-field--filled .q-field__control:after {
                display: none !important;
            }
            .q-field__label { color: #94a3b8 !important; font-size: 0.85rem !important; }
            .q-field__native, .q-field__input { color: #f8fafc !important; }
            .q-field__bottom { display: none !important; }
            .q-menu { background-color: #111827 !important; border: 1px solid #1e293b !important; border-radius: 8px !important; }
            .q-item { color: #e2e8f0 !important; font-size: 0.85rem !important; }
            .q-item--active, .q-item:hover { background-color: #1e293b !important; color: #818cf8 !important; }
            .q-table th {
                color: #94a3b8 !important;
                font-weight: 600 !important;
                font-size: 0.72rem !important;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            .q-table th { background: #111827 !important; }
            .q-table td {
                color: #e2e8f0 !important;
                font-size: 0.85rem !important;
                padding-top: 12px !important;
                padding-bottom: 12px !important;
                border-bottom: 1px solid rgba(30, 41, 59, 0.5) !important;
            }
            .q-table tbody td {
                padding-top: 14px !important;
                padding-bottom: 14px !important;
                font-size: 0.85rem !important;
                border-bottom: 1px solid rgba(30, 41, 59, 0.5) !important;
            }
            .q-table tbody tr { transition: background-color 0.2s ease; }
            .q-table tbody tr:hover { background: rgba(30, 41, 59, 0.4) !important; }
            .q-tabs__arrow { display: none !important; }
            .q-tabs__content { overflow: visible !important; }
            .q-notification {
                background: #111827 !important;
                color: #f8fafc !important;
                border: 1px solid #334155 !important;
                border-radius: 10px !important;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.35) !important;
            }
            .q-notification__icon { color: #818cf8 !important; }
            .no-scrollbar::-webkit-scrollbar { height: 4px; }
            .no-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
        </style>
        """,
        shared=True,
    )
    dfa = MinimizedDFA()
    generator = ProductCodeGenerator()

    with ui.column().classes("w-full max-w-6xl mx-auto px-6 py-4 gap-6"):
        with ui.row().classes("w-full items-center justify-between"):
            with ui.column().classes("gap-0"):
                ui.label("Product Code Validator").classes(
                    "text-2xl font-bold text-white"
                )
                ui.label("What's your DFA").classes(
                    "text-xs text-slate-400 font-medium tracking-wide mt-0.5"
                )
            with ui.row().classes(
                "items-center cursor-pointer px-3 py-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 transition-all hover:bg-emerald-500/20"
            ) as db_button:
                db_dot = ui.html(
                    '<span class="w-2 h-2 rounded-full bg-emerald-400 mr-2 inline-block"></span>'
                )
                db_label = ui.label("DATABASE CONNECTED").classes(
                    "font-mono text-xs font-semibold tracking-wide"
                )

        with ui.row().classes("w-full justify-center my-3"):
            with ui.tabs().props(
                'no-caps shrink dense active-color="white" indicator-color="primary"'
            ).classes("rounded-full border border-slate-800 bg-slate-900 p-1") as tabs:
                scanner_tab = ui.tab("scanner", label="SCANNER & LOOKUP")
                register_tab = ui.tab("register", label="REGISTER PRODUCT")
                catalog_tab = ui.tab("catalog", label="INVENTORY CATALOG")

        with ui.tab_panels(tabs, value=scanner_tab).classes("w-full bg-transparent"):
            with ui.tab_panel(scanner_tab).classes("gap-4"):
                with ui.card().classes(PANEL_CLASSES):
                    with ui.column().classes("w-full gap-1 mb-2"):
                        ui.label("Product Code").classes(
                            "text-xs font-medium text-slate-300"
                        )
                        with ui.row().classes("w-full items-center gap-3"):
                            code_input = (
                                ui.input(
                                    placeholder="e.g. IT-2026-001",
                                    value="IT-2026-001",
                                )
                                .props("outlined dense")
                                .classes("flex-grow font-mono text-sm h-10")
                            )
                            scan_button = ui.button(
                                "SCAN & VALIDATE", color="indigo"
                            ).classes(
                                "bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 rounded-lg text-xs h-10 transition tracking-wide shadow-md shadow-indigo-950/40"
                            )
                    with ui.row().classes("w-full flex-wrap gap-2 pt-2"):
                        quick_tests = {
                            "Valid Code": lambda: set_code(generator.generate_code()),
                            "Prefix Error": lambda: set_code(
                                generator.generate_corrupted("short_prefix")
                            ),
                            "Year Error": lambda: set_code(
                                generator.generate_corrupted("bad_year")
                            ),
                            "Dash Error": lambda: set_code(
                                generator.generate_corrupted("dash_error")
                            ),
                            "Alphabet Error": lambda: set_code(
                                generator.generate_corrupted("alphabet_error")
                            ),
                        }
                        for label, handler in quick_tests.items():
                            ui.button(label, on_click=handler).classes(
                                "bg-[#111827] hover:bg-slate-800 text-slate-300 hover:text-white text-xs px-3.5 py-1.5 rounded-lg border border-slate-800 hover:border-indigo-500/50 transition font-medium"
                            )

                with ui.card().classes(
                    "w-full border-dashed border border-slate-800 bg-slate-900/40 rounded-xl p-6 text-center text-slate-500 text-xs"
                ):
                    ui.label("DFA TAPE SCANNER").classes(
                        "text-xs font-semibold text-slate-400 tracking-wider uppercase"
                    )
                    trace_row = ui.row().classes(
                        "w-full flex-wrap gap-2 no-scrollbar py-3"
                    )
                    with trace_row:
                        with ui.column().classes(
                            "w-full items-center justify-center py-6 text-slate-500 gap-1"
                        ):
                            ui.icon("terminal", size="2rem").classes("text-slate-600")
                            ui.label(
                                "Awaiting input. Enter a code or click a test case above to trace state transitions."
                            ).classes("text-xs text-slate-400")

                scan_result = ui.column().classes("w-full")

                with ui.card().classes(PANEL_CLASSES):
                    ui.label("Validation History").classes(
                        "text-xs font-semibold text-slate-400 tracking-wider uppercase"
                    )
                    ui.label("Real-time automata verification telemetry").classes(
                        "text-xs text-slate-500"
                    )
                    audit_table = ui.table(
                        columns=[
                            {"name": "id", "label": "ID", "field": "id"},
                            {
                                "name": "input_code",
                                "label": "Code",
                                "field": "input_code",
                            },
                            {"name": "verdict", "label": "Verdict", "field": "verdict"},
                            {
                                "name": "halt_state",
                                "label": "Halt State",
                                "field": "halt_state",
                            },
                            {
                                "name": "created_at",
                                "label": "Timestamp",
                                "field": "created_at",
                            },
                        ],
                        rows=[],
                        row_key="id",
                        pagination={
                            "rowsPerPage": 10,
                            "rowsPerPageOptions": [10, 25, 50],
                            "sortBy": "id",
                            "descending": True,
                        },
                    ).classes("w-full bg-transparent font-mono")

            with ui.tab_panel(register_tab).classes("gap-4"):
                with ui.grid(columns=2).classes(
                    "grid grid-cols-1 md:grid-cols-2 gap-6 w-full"
                ):
                    with ui.card().classes(f"w-full {PANEL_CLASSES} p-6"):
                        ui.label("REGISTER NEW PRODUCT").classes(
                            "text-xs font-semibold text-slate-400 tracking-wider uppercase"
                        )
                        with ui.column().classes("w-full gap-3.5 mt-3"):
                            with ui.column().classes("w-full gap-1"):
                                ui.label("Product Name").classes(
                                    "text-xs font-medium text-slate-300"
                                )
                                product_name = (
                                    ui.input(placeholder="e.g. Mechanical Keyboard")
                                    .props("outlined dense")
                                    .classes("w-full font-sans")
                                )
                            with ui.column().classes("w-full gap-1"):
                                ui.label("Category").classes(
                                    "text-xs font-medium text-slate-300"
                                )
                                category = (
                                    ui.select(
                                        CATEGORY_OPTIONS,
                                        value=CATEGORY_OPTIONS[0],
                                    )
                                    .props("outlined dense options-dense")
                                    .classes("w-full font-sans")
                                )
                            with ui.column().classes("w-full gap-1"):
                                ui.label("Price in PHP").classes(
                                    "text-xs font-medium text-slate-300"
                                )
                                price = (
                                    ui.number(
                                        placeholder="0.00", value=None, format="%.2f"
                                    )
                                    .props("outlined dense")
                                    .classes("w-full font-mono")
                                )
                        register_button = ui.button(
                            "GENERATE CODE & REGISTER PRODUCT", color="indigo"
                        ).classes(
                            "bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2.5 rounded-lg w-full mt-2 transition text-sm"
                        )
                    with ui.card().classes(f"w-full {PANEL_CLASSES}"):
                        ui.label("LIVE ASSET TAG PREVIEW").classes(
                            "text-xs font-semibold text-slate-400 tracking-wider uppercase"
                        )
                        preview_panel = ui.column().classes(
                            "w-full bg-slate-900 border border-slate-800 rounded-xl p-8 items-center justify-center text-center"
                        )

            with ui.tab_panel(catalog_tab).classes("gap-4"):
                with ui.row().classes("w-full items-center justify-between mb-4"):
                    with ui.row().classes("items-baseline gap-2"):
                        ui.label("INVENTORY CATALOG").classes(
                            "text-xs font-semibold text-slate-400 tracking-wider uppercase"
                        )
                        count_label = ui.label("(0 items)").classes(
                            "text-xs font-mono text-slate-500"
                        )
                    refresh_catalog_button = (
                        ui.button("REFRESH")
                        .props("flat dense")
                        .classes(
                            "text-xs font-semibold text-indigo-400 hover:text-indigo-300 border border-slate-800 px-3 py-1 rounded"
                        )
                    )
                catalog_search = (
                    ui.input(placeholder="Filter products by name or code...")
                    .props("outlined dense")
                    .classes(f"w-full {INPUT_CLASSES}")
                )
                inventory_table = (
                    ui.table(
                        columns=[
                            {"name": "id", "label": "ID", "field": "id"},
                            {
                                "name": "product_code",
                                "label": "Code",
                                "field": "product_code",
                            },
                            {
                                "name": "product_name",
                                "label": "Product Name",
                                "field": "product_name",
                            },
                            {
                                "name": "category",
                                "label": "Category",
                                "field": "category",
                            },
                            {"name": "price", "label": "Price", "field": "price"},
                            {
                                "name": "created_at",
                                "label": "Registered Date",
                                "field": "created_at",
                            },
                            {"name": "actions", "label": "Actions", "field": "actions"},
                        ],
                        rows=[],
                        row_key="id",
                        pagination={
                            "rowsPerPage": 10,
                            "rowsPerPageOptions": [10, 25, 50],
                            "sortBy": "id",
                            "descending": True,
                        },
                    )
                    .props("flat bordered dense")
                    .classes(
                        "w-full bg-slate-900 border border-slate-800 rounded-xl font-mono"
                    )
                )
                inventory_table.add_slot(
                    "body-cell-actions",
                    """
                    <q-td key="actions" :props="props">
                        <q-btn flat dense size="sm" label="SCAN" class="text-indigo-400 hover:text-indigo-300 font-semibold text-xs"
                            @click="$parent.$emit('scan-code', props.row.product_code)" />
                        <q-btn flat dense size="sm" label="DELETE" class="text-slate-400 hover:text-rose-400 font-semibold text-xs ml-3"
                            @click="$parent.$emit('delete-product', props.row.id)" />
                    </q-td>
                    """,
                )

    catalog_rows: list[dict] = []

    def set_connection_state(connected: bool) -> None:
        db_label.text = "DATABASE CONNECTED" if connected else "DATABASE OFFLINE"
        db_dot.content = (
            '<span class="w-2 h-2 rounded-full mr-2 inline-block '
            + ("bg-emerald-400" if connected else "bg-rose-400")
            + '"></span>'
        )
        db_button.classes(
            remove="border-emerald-500/30 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border-rose-500/30 bg-rose-500/10 text-rose-400 hover:bg-rose-500/20",
            add=(
                "border-emerald-500/30 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20"
                if connected
                else "border-rose-500/30 bg-rose-500/10 text-rose-400 hover:bg-rose-500/20"
            ),
        )
        db_dot.update()
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
                color="dark",
                icon="check_circle",
                position="bottom-right",
                group=False,
                timeout=2000,
                close_button=False,
                classes="bg-slate-900 text-slate-100 border border-slate-700 shadow-xl",
            )
        else:
            ui.notify(
                "Database connection failed",
                color="dark",
                icon="error",
                position="bottom-right",
                group=False,
                timeout=2000,
                close_button=False,
                classes="bg-slate-900 text-slate-100 border border-slate-700 shadow-xl",
            )

    def notify_dark(message: str, icon: str | None = None) -> None:
        """Show one short, non-grouped slate toast without competing with DFA colors."""
        ui.notify(
            message,
            color="dark",
            icon=icon,
            group=False,
            position="bottom-right",
            timeout=2000,
            close_button=False,
            classes="bg-slate-900 text-slate-100 border border-slate-700 shadow-xl",
        )

    def refresh_telemetry() -> None:
        audit_table.update_rows(db.get_recent_logs(50))

    def set_code(value: str) -> None:
        code_input.value = value
        code_input.update()

    def render_preview(generated_code: str | None = None) -> None:
        preview_panel.clear()
        category_value = str(category.value or CATEGORY_OPTIONS[0])
        category_code = category_value.split(" ", 1)[0]
        category_name = category_value.split(" - ", 1)[-1]
        product_value = str(product_name.value or "Product Name")
        price_value = price.value
        price_text = (
            f"₱{float(price_value):,.2f}" if price_value is not None else "₱0.00"
        )
        code_text = generated_code or f"{category_code}-2026-###"
        with preview_panel:
            ui.label(f"CATEGORY: {category_name.upper()}").classes(
                "text-slate-400 text-xs font-semibold tracking-wider font-mono"
            )
            ui.label(code_text).classes(
                "text-2xl font-bold font-mono text-white my-3 tracking-widest"
            )
            ui.label(product_value).classes("text-slate-300")
            ui.label(price_text).classes("font-mono text-base mt-1 text-slate-300")

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
        count_label.text = f"({len(catalog_rows)} items)"
        count_label.update()

    def update_catalog() -> None:
        nonlocal catalog_rows
        catalog_rows = db.get_all_products()
        render_catalog()

    async def scan_code() -> None:
        code = str(code_input.value or "")
        result = dfa.validate(code)
        trace_row.clear()
        for step in result["steps"]:
            with trace_row:
                chip_color = (
                    "bg-slate-900 border border-rose-500 text-rose-400 shadow-sm shadow-rose-950/50"
                    if step["to_state"] == "q_trap"
                    else "bg-slate-900 border border-emerald-500/40 text-emerald-400 shadow-sm"
                )
                ui.label(
                    f"[{step['char']}] : [{step['from_state']}] ➔ [{step['to_state']}]"
                ).classes(
                    f"shrink-0 rounded-lg px-2.5 py-1.5 {chip_color} font-mono text-xs"
                )
            await asyncio.sleep(0.08)
        scan_result.clear()
        product = db.get_product_by_code(code) if result["is_valid"] else None
        if result["is_valid"] and product is not None:
            card_classes = "bg-slate-900 border border-emerald-500/40 rounded-xl p-4"
        elif result["is_valid"]:
            card_classes = "bg-slate-900 border border-emerald-500/40 rounded-xl p-4"
        else:
            card_classes = "bg-slate-900 border border-rose-500/40 rounded-xl p-4"
        with scan_result:
            with ui.card().classes(f"w-full {card_classes}"):
                if result["is_valid"]:
                    ui.label("VERDICT: ACCEPTED — Final State: q11").classes(
                        "text-emerald-400 font-mono font-bold text-sm"
                    )
                    if product is None:
                        ui.badge("NOT IN INVENTORY").classes(
                            "bg-slate-800 text-slate-100 font-mono text-xs font-semibold px-2.5 py-1 rounded border border-slate-700 tracking-wider"
                        )
                        ui.label(
                            "Valid code syntax, but unregistered in inventory."
                        ).classes("text-slate-300 text-xs mt-1")
                    else:
                        with ui.row().classes("items-center gap-3 mt-2"):
                            ui.label(product.get("product_name", "")).classes(
                                "text-base font-semibold text-white"
                            )
                            ui.badge(product.get("category", "")).classes(
                                "bg-slate-800 text-slate-300 font-mono text-xs font-medium px-2 py-0.5 rounded border border-slate-700 ml-2"
                            )
                        ui.label(
                            f"Price: ₱{float(product.get('price', 0)):,.2f}"
                        ).classes("font-mono text-slate-200")
                        ui.label(
                            f"Registered: {product.get('created_at', '')}"
                        ).classes("text-slate-400")
                else:
                    ui.label(
                        f"✕ VERDICT: REJECTED: Halt State: {result['halt_state']}"
                    ).classes("text-rose-300 font-semibold")
                    ui.label(result["error"] or "Unknown validation error").classes(
                        "mt-2 text-rose-100"
                    )
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
        name = str(product_name.value or "").strip()
        amount = price.value
        category_code = parse_category(str(category.value or ""))
        if not name or amount is None:
            notify_dark("Enter a product name and price.", "warning")
            return
        code = generator.generate_unique_code(category_code, db.check_code_exists)
        if dfa.validate(code)["is_valid"] and db.insert_product(
            code, name, float(amount), category_code
        ):
            render_preview(code)
            update_catalog()
            refresh_telemetry()
            notify_dark(
                "Product successfully registered into inventory", "check_circle"
            )
        else:
            notify_dark("Product could not be registered in the database.", "error")
        refresh_connection()

    async def scan_catalog_code(code: str) -> None:
        set_code(code)
        tabs.value = scanner_tab
        tabs.update()
        await scan_code()

    def delete_catalog_product(product_id: int) -> None:
        if db.delete_product(product_id):
            update_catalog()
            notify_dark("Product deleted", "check_circle")
        else:
            notify_dark("Product could not be deleted", "error")

    async def handle_scan_event(event: Any) -> None:
        await scan_catalog_code(str(event.args))

    def handle_delete_event(event: Any) -> None:
        delete_catalog_product(int(event.args))

    db_button.on("click", on_db_badge_click)
    inventory_table.on("scan-code", handle_scan_event)
    inventory_table.on("delete-product", handle_delete_event)
    catalog_search.on_value_change(lambda _: render_catalog())
    refresh_catalog_button.on_click(update_catalog)
    product_name.on_value_change(lambda _: render_preview())
    category.on_value_change(lambda _: render_preview())
    price.on_value_change(lambda _: render_preview())
    scan_button.on_click(scan_code)
    register_button.on_click(register_product)

    refresh_connection()
    refresh_telemetry()
    update_catalog()
    render_preview()


def main() -> None:
    build_ui()
    ui.run(
        title="Product Code Validator - What's your DFA",
        port=8000,
        native=False,
        reload=False,
        show=False,
    )


if __name__ == "__main__":
    main()
