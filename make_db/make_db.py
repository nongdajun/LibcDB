#!/bin/env python3
import sqlite3
import os
import re
import time
import requests
import tarfile


conn = sqlite3.Connection("../libc_db/data/libc.sqlite3")


def init_db():
    global conn
    conn.execute(r"""CREATE TABLE if not exists libc_info (
        filename    TEXT    NOT NULL,
        version     TEXT    NOT NULL,
        symbol      TEXT    NOT NULL,
        address     INTEGER NOT NULL,
        bits        INTEGER,
        create_date INTEGER
    );
    """)

    conn.execute(r"""CREATE INDEX if not exists idx_sym_addr ON libc_info (
        symbol,
        address
    );
    """)


def process_libc_info(filename, sym_info):
    filename = filename.lower()
    version = re.findall(r"[\d]\.[\d\.]+", filename)[0]
    if version.endswith("."):
        version = version[:-1]
    if "amd64" in filename:
        bits = 64
    elif "i386" in filename:
        bits = 32
    else:
        bits = None
    print(filename, version, bits)
    arr = sym_info.splitlines(keepends=False)
    for line in arr:
        a = line.strip().split(" ")
        assert len(a) == 2
        s, addr = a
        addr = int(addr, 16)
        cur = conn.execute(
            "SELECT 1 FROM libc_info where filename=? and symbol=? and address=?",
            (filename, s, addr))
        if not cur.fetchone():
            conn.execute(
                "INSERT INTO libc_info (filename, version, symbol, address, bits, create_date) VALUES (?, ?, ?, ?, ?, ?)",
                (filename, version, s, addr, bits, int(time.time())))
        else:
            # print("PASS")
            pass

    conn.commit()


def load_libc_database_dir(db_dir):
    for file in os.listdir(db_dir):
        if not file.endswith(".symbols"):
            continue
        filename = file[:-8]
        with open(os.path.join(db_dir, file)) as f:
            sym_info = f.read().strip()
        process_libc_info(filename, sym_info)


def get_ubuntu_libc(url, name):
    cur = conn.execute("SELECT 1 FROM libc_info where filename=? limit 1",[name])
    if cur.fetchone():

        return
    print("NAME:", name)
    print("DOWNLOADING:", url)
    resp = requests.get(url)
    assert resp.status_code == 200
    with open("download/"+name+".deb", "wb") as f:
        f.write(resp.content)

    os.chdir("./tmp/")

    e_file = "data.tar.xz"

    os.system(f"ar x ./download/{name}.deb  {e_file} 2>/dev/null")

    if not os.path.exists(e_file):
        e_file = "data.tar.zst"
        os.system(f"ar x ./download/{name}.deb  {e_file}")

    c_file = os.popen(f'''tar -tf {e_file} | grep  "/libc.so.6$"''').read().strip()

    print("LIBC:", c_file)

    if e_file.endswith(".zst"):
        os.system(f"tar -xf ./{e_file}  {c_file}")
    else:
        tf = tarfile.open(e_file)
        member = tf.getmember(c_file)
        c_file = "libc.so.6"
        with open(c_file, "wb") as f:
            f.write(tf.extractfile(member).read())

    os.unlink(e_file)
    os.chdir("..")

    c_file = os.path.join("./tmp/", c_file)
    assert os.path.exists(c_file)

    os.system(f"./add.sh {c_file} '{name}' ")

    os.unlink(c_file)

    with open(f"db/{name}.symbols") as f:
        sym_dat = f.read()

    process_libc_info(name, sym_dat)


def get_ubuntu_all():
    common_url = 'https://mirror.tuna.tsinghua.edu.cn/ubuntu/pool/main/g/glibc/'
    old_url = 'http://old-releases.ubuntu.com/ubuntu/pool/main/g/glibc/'

    def get_list(url, arch):
        content = str(requests.get(url).content)
        #print(content)
        return re.findall('(libc6_2\.[0-9][0-9]-[0-9]ubuntu[0-9\.]*_{}).deb'.format(arch), content)

    common_list = get_list(common_url, 'amd64')
    common_list += get_list(common_url, 'i386')

    for i in common_list:
        get_ubuntu_libc(common_url+i+".deb", i)

    old_list = get_list(old_url, 'amd64')
    old_list += get_list(old_url, 'i386')

    for i in old_list:
        get_ubuntu_libc(old_url+i+".deb", i)

#load_libc_database_dir("libc-db/")
get_ubuntu_all()


conn.close()