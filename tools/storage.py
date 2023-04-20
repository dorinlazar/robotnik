import logging
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
            logging.log(logging.ERROR, f"error opening file {self.__path}: {str(e)}")
        return []

    def store(self, key: str, value: str):
        self.store_all([(key, value)])

    def delete(self, key: str) -> bool:
        try:
            with gdbm.open(self.__path) as db:
                del db[key]
            return True
        except Exception as e:
            logging.log(logging.ERROR, f"error opening file {self.__path}: {str(e)}")
        return False

    def store_all(self, items: list[tuple[str, str]]):
        try:
            with gdbm.open(self.__path, "c") as db:
                for item in items:
                    db[item[0]] = item[1]
        except Exception as e:
            logging.log(logging.ERROR, f"error opening file {self.__path}: {str(e)}")


if __name__ == "__main__":
    import os

    storage = Storage(os.path.expanduser("~/.robotnik.rss.gdbm"))
    items = storage.restore()
    for x in items:
        print(f"{x[0]}:: {x[1]}")
        print("")
