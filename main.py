from fastmcp import FastMCP
import os
import aiosqlite
import asyncio

DB_PATH = "/tmp/expenses.db"  # Writable (temporary)
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("Expense Tracker")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """
        )
        await db.commit()


asyncio.run(init_db())


@mcp.tool()
async def add_expense(
    date: str, amount: float, category: str, subcategory: str = "", note: str = ""
):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?, ?, ?, ?, ?)",
            (date, amount, category, subcategory, note),
        )
        await db.commit()
        return {"status": "ok", "id": cur.lastrowid}


@mcp.tool()
async def list_all_expense():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            SELECT id, date, amount, category, subcategory
            FROM expenses
            ORDER BY date
        """
        )
        rows = await cur.fetchall()
        cols = [d[0] for d in cur.description]

    return [dict(zip(cols, r)) for r in rows]


@mcp.tool()
async def list_dated_expense(start_date: str, end_date: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
        """,
            (start_date, end_date),
        )

        rows = await cur.fetchall()
        cols = [d[0] for d in cur.description]

    return [dict(zip(cols, r)) for r in rows]


@mcp.tool()
async def summarize(start_date: str, end_date: str, category: str | None = None):
    async with aiosqlite.connect(DB_PATH) as db:
        query = """
            SELECT category, SUM(amount) AS total_amount
            FROM expenses
            WHERE date BETWEEN ? AND ?
        """
        params = [start_date, end_date]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " GROUP BY category ORDER BY category ASC"

        cur = await db.execute(query, params)
        rows = await cur.fetchall()
        cols = [d[0] for d in cur.description]

    return [dict(zip(cols, r)) for r in rows]


# Keep this synchronous (simple file read, no DB, minimal overhead)
@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    # Local
    # mcp.run()

    # Remote
    mcp.run(transport="http", host="0.0.0.0", port=8000)