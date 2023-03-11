import dbm.gnu as gdbm


class Storage:
    def __init__(self, path: str):
        self.__path = path

    def restore(self) -> list[tuple[str, str]]:
        try:
            with gdbm.open(self.__path) as db:
                keys: list[str] = []
                key = db.firstkey()
                while key is not None:
                    keys.append(key.decode())
                    key = db.nextkey(key)

                return [(key, db[key].decode()) for key in keys]
        except Exception as e:
            print(f"error opening file {self.__path}: {str(e)}")
        return []

    def store(self, key: str, value: str):
        self.store_all([(key, value)])

    def store_all(self, items: list[tuple[str, str]]):
        try:
            with gdbm.open(self.__path, "c") as db:
                for item in items:
                    db[item[0]] = item[1]
        except Exception as e:
            print(f"error opening file {self.__path}: {str(e)}")
