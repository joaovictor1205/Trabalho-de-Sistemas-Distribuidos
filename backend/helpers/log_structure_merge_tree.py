from threading import Lock, Timer
import json
import os

ARCHIVE_PATH = '/code/archive/'
SNAPS_FOLDER_PATH = '/code/archive/snaps/'

lock = Lock()

class LogStructureMergeTree:
    def __init__(self, memtable_limit=15, snapshot_time=300):
        self.memtable = {}
        self.memtable_limit = memtable_limit
        self.snapshot_time = snapshot_time

        if not os.path.exists(SNAPS_FOLDER_PATH):
            os.makedirs(SNAPS_FOLDER_PATH)

        self._recover()

        t = Timer(self.snapshot_time, self._build_snapshot_sched)
        t.start()

    def _get_snapshots(self):
        return os.listdir(SNAPS_FOLDER_PATH)

    def _recover(self):
        snap_files = self._get_snapshots()
        if len(snap_files) > 0:
            with open(f'{SNAPS_FOLDER_PATH}{snap_files[0]}', 'r+') as objs_file:
                objs = json.load(objs_file)
                self.memtable = objs

        if os.path.exists(f'{ARCHIVE_PATH}log'):
            with open(f'{ARCHIVE_PATH}log', 'r+') as log_file:
                logs = log_file.read().splitlines()
                for log in logs:
                    log = json.loads(log)
                    for key in log:
                        self.memtable[key] = log[key]

    def _build_snapshot(self):
        print('Building Snapshot')
        snap_files = self._get_snapshots()
        if len(snap_files) > 0:
            last_snap_id = max([int(snap_file.split('.')[1]) for snap_file in snap_files ])
        else:
            last_snap_id = 0

        with open(f'{SNAPS_FOLDER_PATH}snap.{last_snap_id+1}', 'w+') as snap_file:
            json_snap = json.dumps(self.memtable)
            snap_file.write(json_snap)

        self.memtable = {}
        os.remove(f'{ARCHIVE_PATH}log')

    def _build_snapshot_sched(self):
        if os.path.exists(f'{ARCHIVE_PATH}log'):
            self._build_snapshot()
        t = Timer(self.snapshot_time, self._build_snapshot_sched)
        t.start()


    def create(self, id, data):
        lock.acquire()

        if len(self.memtable) >= self.memtable_limit:
            self._build_snapshot()

        # Add key in log
        with open(f'{ARCHIVE_PATH}log', 'a+') as log_file:
            item = {id: data}
            log_file.write(json.dumps(item))
            log_file.write('\n')

        # Add key in memtable:
        self.memtable[id] = data

        lock.release()

    def search(self, filters={}):
        for key in self.memtable:
            obj = self.memtable[key]

            flag = True
            for key in filters:
                if key not in obj or obj[key] != filters[key]:
                    flag = False

            if flag:
                return obj

        for snap_file in self._get_snapshots():
            with open(f'{SNAPS_FOLDER_PATH}{snap_file}', 'r+') as objs_file:
                objs = json.load(objs_file)
                for key in objs:
                    obj = objs[key]

                    flag = True
                    for key in filters:
                        if key not in obj or obj[key] != filters[key]:
                            flag = False

                    if flag:
                        return obj
        return None

    def search_multiple(self, filters={}):
        ids = []
        res = []

        for key in self.memtable:
            obj = self.memtable[key]
            flag = True
            for key in filters:
                if key not in obj or obj[key] != filters[key]:
                    flag = False


            if flag and obj['id'] not in ids:
                res.append(obj)
                ids.append(obj['id'])

        for snap_file in self._get_snapshots():
            with open(f'{SNAPS_FOLDER_PATH}{snap_file}', 'r+') as objs_file:
                objs = json.load(objs_file)
                for key in objs:
                    obj = objs[key]
                    flag = True
                    for key in filters:
                        if key not in obj or obj[key] != filters[key]:
                            flag = False

                    if flag and obj['id'] not in ids:
                        res.append(obj)
                        ids.append(obj['id'])

        return res
