import dbm.gnu as gdbm
import json


class Storage:
    def __init__(self, path: str):
        self.__path = path

    def restore(self, feed: str) -> StorageData:
        try:
            with gdbm.open(self.__path, 'c') as db:
                result = StorageData(json.loads(db[feed]))
                print(f'restored: {len(result.guids)} guids')
                return result
        except Exception:
            pass
        return StorageData()

    def store(self, feed: str, data: StorageData) -> None:
        try:
            with gdbm.open(self.__path, 'c') as db:
                writer = json.dumps({'guids': data.guids, 'links': data.links,
                                     'last_updated': str(data.last_updated)})
                print(f'storing {len(data.guids)} guids: {writer}')
                db[feed] = writer
        except Exception as e:
            print(f'Unable to write to storage: {self.__path} feed: {feed}: {str(e)}')
