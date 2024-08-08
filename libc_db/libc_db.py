import sqlite3
import os

db_file = os.path.join(os.path.dirname(__file__), "data/libc.sqlite3")

conn = sqlite3.Connection(db_file)


def get_libc_list():
    cur = conn.execute("SELECT distinct filename FROM libc_info order by  create_date")
    ret = cur.fetchall()
    cur.close()
    return [a[0] for a in ret]


def has_libc(name, use_like=False):
    if use_like:
        cur = conn.execute("SELECT 1 FROM libc_info where filename like '%'||?||'%' limit 1", (name,))
    else:
        cur = conn.execute("SELECT 1 FROM libc_info where filename=? limit 1", (name,))
    return cur.fetchone() is not None


def search_symbol(symbol_name: str, libc_name: str = None, bits: int = None, version_no=None, use_like=False):
    if not symbol_name:
        return None
    cond = ""
    params = [symbol_name]
    if libc_name:
        cond += " and filename=? "
        params.append(libc_name)
    if bits:
        cond += " and bits=? "
        params.append(bits)
    if version_no:
        cond += " and version=? "
        params.append(version_no)
    if use_like:
        cur = conn.execute(
            f"SELECT address, filename, bits FROM libc_info WHERE symbol like '%'||?||'%' {cond} order by create_date desc",
            params)
    else:
        cur = conn.execute(
            f"SELECT address, filename, bits FROM libc_info WHERE symbol = ? {cond} order by create_date desc",
            params)
    ret = cur.fetchall()
    cur.close()
    return ret


def detect_libc(*args, bits=None, version_no=None):
    """detect_libc(symbol1, address1, symbol2, address2, ...)"""
    if len(args) <= 1:
        return None
    cond = ""
    params = []
    if bits:
        cond += " and bits=? "
        params.append(bits)
    if version_no:
        cond += " and version=? "
        params.append(version_no)
    ret = None
    for i in range(0, len(args), 2):
        sql = "SELECT distinct filename FROM libc_info WHERE symbol=? and (address&0xFFF)=?" + cond
        symbol = str(args[i])
        address = int(args[i + 1]) & 0xFFF
        cur = conn.execute(sql, [symbol, address] + params)
        tmp = cur.fetchall()
        if tmp is None:
            return None
        if ret is None:
            ret = set([a[0] for a in tmp])
        else:
            ret = ret.intersection([a[0] for a in tmp])
            if len(ret) == 0:
                return None
    return tuple(ret)


if __name__ == "__main__":
    print(detect_libc("strlen", 677056, bits=32))
