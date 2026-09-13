"""Resilient database access for the product code validator."""

from __future__ import annotations

from typing import Any

import pymysql
from pymysql.connections import Connection


DB_CONFIG: dict[str, Any] = {
	"host": "127.0.0.1",
	"port": 3306,
	"user": "root",
	"password": "root",
	"database": "automata_validator",
	"connect_timeout": 5,
	"read_timeout": 5,
	"write_timeout": 5,
	"autocommit": False,
	"cursorclass": pymysql.cursors.DictCursor,
}


def test_connection() -> bool:
	"""Return whether the configured database accepts a ping."""
	connection: Connection | None = None
	try:
		connection = pymysql.connect(**DB_CONFIG)
		connection.ping()
		return True
	except Exception:
		return False
	finally:
		if connection is not None:
			try:
				connection.close()
			except Exception:
				pass


def save_log(
	code: str,
	verdict: str,
	halt_state: str,
	reason: str | None,
) -> bool:
	"""Save a validation result, returning False when the database is unavailable."""
	connection: Connection | None = None
	cursor: Any = None
	try:
		connection = pymysql.connect(**DB_CONFIG)
		cursor = connection.cursor()
		cursor.execute(
			"""
			INSERT INTO validation_logs
				(input_code, verdict, halt_state, failure_reason)
			VALUES (%s, %s, %s, %s)
			""",
			(code, verdict, halt_state, reason),
		)
		connection.commit()
		return True
	except Exception:
		if connection is not None:
			try:
				connection.rollback()
			except Exception:
				pass
		return False
	finally:
		if cursor is not None:
			try:
				cursor.close()
			except Exception:
				pass
		if connection is not None:
			try:
				connection.close()
			except Exception:
				pass


def get_recent_logs(limit: int = 10) -> list[dict]:
	"""Return the newest validation records, or an empty list on failure."""
	if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
		return []

	connection: Connection | None = None
	cursor: Any = None
	try:
		connection = pymysql.connect(**DB_CONFIG)
		cursor = connection.cursor()
		cursor.execute(
			"""
			SELECT id, input_code, verdict, halt_state, failure_reason, created_at
			FROM validation_logs
			ORDER BY id DESC
			LIMIT %s
			""",
			(limit,),
		)
		return list(cursor.fetchall())
	except Exception:
		return []
	finally:
		if cursor is not None:
			try:
				cursor.close()
			except Exception:
				pass
		if connection is not None:
			try:
				connection.close()
			except Exception:
				pass


def insert_product(code: str, name: str, price: float, category: str) -> bool:
	"""Insert a product, returning False for duplicate or database failures."""
	connection: Connection | None = None
	cursor: Any = None
	try:
		connection = pymysql.connect(**DB_CONFIG)
		cursor = connection.cursor()
		cursor.execute(
			"""
			INSERT INTO products (product_code, product_name, price, category)
			VALUES (%s, %s, %s, %s)
			""",
			(code, name, price, category),
		)
		connection.commit()
		return True
	except Exception:
		if connection is not None:
			try:
				connection.rollback()
			except Exception:
				pass
		return False
	finally:
		if cursor is not None:
			try:
				cursor.close()
			except Exception:
				pass
		if connection is not None:
			try:
				connection.close()
			except Exception:
				pass


def get_product_by_code(code: str) -> dict | None:
	"""Return a product by code, or None when it is missing or unavailable."""
	connection: Connection | None = None
	cursor: Any = None
	try:
		connection = pymysql.connect(**DB_CONFIG)
		cursor = connection.cursor()
		cursor.execute(
			"""
			SELECT id, product_code, product_name, price, category, created_at
			FROM products
			WHERE product_code = %s
			""",
			(code,),
		)
		product = cursor.fetchone()
		return dict(product) if product is not None else None
	except Exception:
		return None
	finally:
		if cursor is not None:
			try:
				cursor.close()
			except Exception:
				pass
		if connection is not None:
			try:
				connection.close()
			except Exception:
				pass


def get_all_products() -> list[dict]:
	"""Return formatted catalog rows, or an empty list when MySQL is unavailable."""
	connection: Connection | None = None
	cursor: Any = None
	try:
		connection = pymysql.connect(**DB_CONFIG)
		cursor = connection.cursor()
		cursor.execute(
			"""
			SELECT id, product_code, product_name, price, category, created_at
			FROM products
			ORDER BY id DESC
			"""
		)
		products: list[dict] = []
		for row in cursor.fetchall():
			if isinstance(row, dict):
				product_id = row.get("id")
				product_code = row.get("product_code")
				product_name = row.get("product_name")
				product_price = row.get("price")
				product_category = row.get("category")
				created_at = row.get("created_at")
			else:
				product_id, product_code, product_name, product_price, product_category, created_at = row
			products.append(
				{
					"id": product_id,
					"product_code": product_code,
					"product_name": product_name,
					"price": f"PHP {float(product_price):,.2f}",
					"raw_price": float(product_price),
					"category": product_category,
					"created_at": str(created_at),
				}
			)
		return products
	except Exception:
		return []
	finally:
		if cursor is not None:
			try:
				cursor.close()
			except Exception:
				pass
		if connection is not None:
			try:
				connection.close()
			except Exception:
				pass


def delete_product(product_id: int) -> bool:
	"""Delete a product by ID, returning False on database failure."""
	connection: Connection | None = None
	cursor: Any = None
	try:
		connection = pymysql.connect(**DB_CONFIG)
		cursor = connection.cursor()
		cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
		connection.commit()
		return True
	except Exception:
		if connection is not None:
			try:
				connection.rollback()
			except Exception:
				pass
		return False
	finally:
		if cursor is not None:
			try:
				cursor.close()
			except Exception:
				pass
		if connection is not None:
			try:
				connection.close()
			except Exception:
				pass


def check_code_exists(code: str) -> bool:
	"""Return whether a product code is already registered."""
	connection: Connection | None = None
	cursor: Any = None
	try:
		connection = pymysql.connect(**DB_CONFIG)
		cursor = connection.cursor()
		cursor.execute(
			"SELECT 1 FROM products WHERE product_code = %s LIMIT 1",
			(code,),
		)
		return cursor.fetchone() is not None
	except Exception:
		return False
	finally:
		if cursor is not None:
			try:
				cursor.close()
			except Exception:
				pass
		if connection is not None:
			try:
				connection.close()
			except Exception:
				pass