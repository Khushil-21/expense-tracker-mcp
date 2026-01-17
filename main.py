from fastmcp import FastMCP
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("Expense Tracker")


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
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


init_db()


@mcp.tool()
def add_expense(date:str, amount:float, category:str, subcategory:str="", note:str=""):
    """Add new expense to DB"""
    with sqlite3.connect(DB_PATH) as db:
        cur = db.execute(
            "INSERT INTO expenses(date,amount,category,subcategory,note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note),
        )
    return {"status": "ok", "id": cur.lastrowid}

@mcp.tool()
def list_all_expense():
    """list all the expense from the DB"""
    with sqlite3.connect(DB_PATH) as db:
        cur = db.execute(
            """
            SELECT id, date, amount, category, subcategory
            FROM expenses
            ORDER BY date
        """
        )
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()

        return [dict(zip(cols, r)) for r in rows]

@mcp.tool()
def list_dated_expense(start_date: str, end_date: str):
    """List all expenses from the DB within a date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    with sqlite3.connect(DB_PATH) as db:
        cur = db.execute(
            """
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date >= ? AND date <= ?
            ORDER BY date DESC
            """,
            (start_date, end_date)
        )
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()

        return [dict(zip(cols, r)) for r in rows]

@mcp.tool()
def summarize(start_date, end_date, category=None):
    '''Summarize expenses by category within an inclusive date range.'''
    with sqlite3.connect(DB_PATH) as c:
        query = (
            """
            SELECT category, SUM(amount) AS total_amount
            FROM expenses
            WHERE date BETWEEN ? AND ?
            """
        )
        params = [start_date, end_date]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " GROUP BY category ORDER BY category ASC"

        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    # this is for local server
    # mcp.run()
    
    # for remote server 
    mcp.run(transport="http",host="0.0.0.0",port=8000)
