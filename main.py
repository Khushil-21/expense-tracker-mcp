from fastmcp import FastMCP
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
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


@mcp.tool
def add_expense(date:str, amount:float, category:str, subcategory:str="", note:str=""):
    """Add new expense to DB"""
    with sqlite3.connect(DB_PATH) as db:
        cur = db.execute(
            "INSERT INTO expenses(date,amount,category,subcategory,note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note),
        )
    return {"status": "ok", "id": cur.lastrowid}


@mcp.tool
def list_expense():
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


if __name__ == "__main__":
    mcp.run()
