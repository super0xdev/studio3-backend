from solana.publickey import PublicKey
from ..sql import utils
import logging


class Table:

    @classmethod
    def select(cls, **where):
        if 'verbose' in where:
            verbose = True
            del where['verbose']
        else:
            verbose = False
        if 'order_by' in where:
            order_str = f" ORDER BY {where['order_by']}"
            del where['order_by']
        else:
            order_str = ""
        columns = list(cls.__dataclass_fields__)
        query = f"SELECT {','.join(columns)} FROM {cls._table_name}"
        query = cls._build_where_clause(query, where) + order_str
        if verbose:
            logging.info(f"QUERY:\n{query}")
        conn, cursor = utils.initialize_connection_and_cursor()
        cursor.execute(query)
        records = list()
        for items in cursor:
            kwargs = dict()
            for i, value in enumerate(items):
                try:
                    col = columns[i]
                    if value is None:
                        kwargs[col] = None
                    else:
                        kwargs[col] = cls.__dataclass_fields__[col].type(value)
                except TypeError as _e:
                    kwargs[columns[i]] = None
            records.append(cls(**kwargs))
        utils.close_connection_and_cursor(conn, cursor)
        return records

    @classmethod
    def delete(cls, **where):
        if 'verbose' in where:
            verbose = True
            del where['verbose']
        else:
            verbose = False
        query = f"DELETE FROM {cls._table_name}"
        query = cls._build_where_clause(query, where)
        if verbose:
            logging.info(f"QUERY:\n{query}")
        conn, cursor = utils.initialize_connection_and_cursor()
        cursor.execute(query)
        rowcount = cursor.rowcount
        utils.close_connection_and_cursor(conn, cursor)
        return rowcount

    @classmethod
    def update(cls, values: dict, **where):
        query = f"UPDATE {cls._table_name} SET"
        for k, v in values.items():
            _type = cls.__dataclass_fields__[k].type
            if v == "NULL":
                query += f" {k} = {v},"
            elif _type == PublicKey:
                query += f" {k} = X'{utils.pk2bin(v)}',"
            elif _type == str:
                query += f" {k} = '{v}',"
            else:
                query += f" {k} = {v},"
        query = query[:-1]
        query = cls._build_where_clause(query, where)
        conn, cursor = utils.initialize_connection_and_cursor()
        cursor.execute(query)
        rowcount = cursor.rowcount
        utils.close_connection_and_cursor(conn, cursor)
        return rowcount

    @classmethod
    def insert(cls, **values):
        col_str = ""
        val_str = ""
        for k,v in values.items():
            col_str += f"{k},"
            _type = cls.__dataclass_fields__[k].type
            if v == "NULL":
                val_str += f"{k},"
            elif _type == PublicKey:
                val_str += f"X'{utils.pk2bin(v)}',"
            elif _type == str:
                val_str += f"'{v}',"
            else:
                val_str += f"{v},"
        col_str = col_str[:-1]
        val_str = val_str[:-1]
        query = f"INSERT INTO {cls._table_name} ({col_str}) VALUES ({val_str})"
        conn, cursor = utils.initialize_connection_and_cursor()
        cursor.execute(query)
        rowcount = cursor.rowcount
        utils.close_connection_and_cursor(conn, cursor)
        return rowcount

    @classmethod
    def _build_where_clause(cls, query, where):
        if len(where) > 0:
            query += " WHERE"
            for k, v in where.items():
                _type = cls.__dataclass_fields__[k].type
                if type(v) == tuple:
                    if type(v[1]) == type(lambda: 1):
                        rhs = v[1]()
                    else:
                        rhs = v[1]
                    query += f" ({k} {v[0]} {rhs}) AND"
                elif v in ['NULL', 'NOT NULL']:
                    query += f" ({k} IS {v}) AND"
                elif _type == PublicKey:
                    query += f" ({k} = X'{utils.pk2bin(v)}') AND"
                elif _type == str:
                    query += f" ({k} = '{v}') AND"
                else:
                    query += f" ({k} = {v}) AND"
            query = query[:-4]
        return query












