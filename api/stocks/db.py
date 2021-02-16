import sqlite3
from pathlib import Path

cwd = Path(__file__).parents[0]


class ORM:
    def __init__(self, db_path):
        if db_path == ':memory:' or db_path.startswith('/'):
            self.db_path = db_path
        else:
            self.db_path = cwd / f"../{db_path}"

    def migrations(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT count(*) FROM sqlite_master
                WHERE type='table';
            ''')
            result = c.fetchall()

            if result[0][0] < 2:
                c.execute(
                    '''CREATE TABLE users
                         (
                             username text UNIQUE, first text, last text,
                             budget real
                         )
                    '''
                )
                c.execute(
                    '''CREATE TABLE stocks
                         (
                             date text, username text, symbol text,
                             action text, qty real, price real
                         )
                    '''
                )

    def execute(self, query, args, action=None):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(query, args)
            if action:
                result = getattr(c, action)()
                return result

    def get_user(
        self,
        username,
    ):
        result = self.execute(
            '''
            SELECT username, first, last, budget
            FROM users WHERE username=?
            ''', (username,),
            action='fetchall'
        )

        if result:
            user = result[0]
            return {
                'username': user[0],
                'first': user[1],
                'last': user[2],
                'budget': user[3],
            }

    def create_user(
        self,
        username,
        first,
        last,
        budget,
    ):
        self.execute(
            """INSERT INTO users VALUES
                (
                   ?, ?, ?, ?
                )
            """, (username, first, last, budget)
        )

    def clear_holdings(
        self,
        username,
    ):
        self.execute(
            """
            DELETE FROM stocks
            WHERE username=?
            """, (username,),
        )

    def get_holdings(
        self,
        username,
        symbol,
    ):
        result = self.execute(
            """
            SELECT SUM(qty) FROM stocks
            WHERE username=? AND symbol=?;
            """, (username, symbol),
            action='fetchone',
        )
        return result[0]

    def get_total_holdings(
        self,
        username,
        date=None,
    ):
        if date:
            result = self.execute(
                """
                SELECT symbol,SUM(qty) FROM stocks
                WHERE username=?
                    AND date <= ?
                GROUP BY symbol;
                """, (username, date.isoformat()),
                action='fetchall',
            )
        else:
            result = self.execute(
                """
                SELECT symbol,SUM(qty) FROM stocks
                WHERE username=?
                GROUP BY symbol;
                """, (username,),
                action='fetchall',
            )
        return result

    def update_budget(
        self,
        username,
        budget
    ):
        self.execute(
            """UPDATE users
                    SET budget = ?
                WHERE username = ?
            """, (budget, username)
        )

    def update_user(
        self,
        username,
        first,
        last,
        budget,
    ):
        self.execute(
            """UPDATE users
                    SET first = ?,
                        last = ?,
                        budget = ?
                WHERE username = ?
            """, (first, last, budget, username)
        )


    def change_stock(
        self,
        date,
        username,
        symbol,
        action,
        quantity,
        price,
    ):
        self.execute(
            """INSERT INTO stocks VALUES
                (
                   ?, ?, ?, ?, ?, ?
                )
            """, (
                date, username, symbol, action, quantity, price
            )
        )

