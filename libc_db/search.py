import libc_db


class Searcher:

    def __init__(self, bits=None):
        self.bits = bits
        self.libc_list = None
        self.func_base_addr = None
        self.func_base_name = None

    def add_condition(self, symbol: str, address: int):
        ret = libc_db.detect_libc(symbol, address, bits=self.bits)
        assert ret and len(ret) > 0, "no libc found"
        if self.libc_list is None:
            self.libc_list = set(ret)
            self.func_base_addr = address
            self.func_base_name = symbol
        else:
            self.libc_list = self.libc_list.intersection(ret)
            if len(self.libc_list) <= 0:
                raise RuntimeError("no libc found")
        return len(self.libc_list)

    def find(self, symbol_name: str):
        if not symbol_name:
            return None
        if self.libc_list is None:
            raise RuntimeError("Please add conditions first!")

        if len(self.libc_list) == 1:
            sel_libc = list(self.libc_list)[0]
        else:
            libc_lst = list(self.libc_list)
            print("\033[33m=======PLEASE SELECT A LIBRARY=========\033[0m")
            for i, c in enumerate(libc_lst):
                print(f"\033[32m[{i + 1}]\033[0m\t{c}")
            print("\033[32m[q]\033[0m\t<quit>")
            while True:
                inp = input("you choices:")
                if inp == "q":
                    return None
                if inp.isdigit():
                    inp = int(inp)
                    if inp < 1 or inp > len(libc_lst):
                        print("\033[33minvalid input!\033[0m")
                        continue
                    sel_libc = libc_lst[inp - 1]
                    break

        ret = libc_db.search_symbol(symbol_name, libc_name=sel_libc, bits=self.bits)
        b_ret = libc_db.search_symbol(self.func_base_name, libc_name=sel_libc, bits=self.bits)
        if not ret or not b_ret:
            return None

        base = self.func_base_addr - b_ret[0][0]
        ret_addr = base + ret[0][0]
        print("\033[37m* libc_base:", hex(base), "\033[0m")
        print(f"\033[37m* {symbol_name}:", hex(ret_addr), "\033[0m")
        return ret_addr


if __name__ == "__main__":
    S = Searcher()
    c = S.add_condition("puts", 0x7F758F703640)
    print("found libc count =", c)
    print("__libc_start_main_addr =", hex(S.find("__libc_start_main")))
