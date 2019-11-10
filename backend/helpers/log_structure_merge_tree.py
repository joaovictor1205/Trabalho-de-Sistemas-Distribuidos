import uuid
import os

ARCHIVE_PATH = '../archive/'


class LogStructureMergeTree:
    def __init__(self):
        self.memtable = {}

        if not os.path.exists(ARCHIVE_PATH + 'logs'):
            os.makedirs(ARCHIVE_PATH + 'logs')

        if not os.path.exists(ARCHIVE_PATH + 'snaps'):
            os.makedirs(ARCHIVE_PATH + 'snaps')

    def create(self, data):
        pass

    def update(self):
        pass

    def get(self):
        pass
