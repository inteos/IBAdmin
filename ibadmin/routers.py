# -*- coding: UTF-8 -*-

BACAPPS = {
    'clients': ['client'],
    'config': ['version'],
    'jobs': ['fileset', 'status', 'job', 'jobhisto', 'log', 'file', 'filename'],
    'storages': ['pool', 'device', 'storage', 'media', 'jobmedia', 'mediatype'],
}


class BaculaRouter:
    def _check_bacula(self, model):
        app = model._meta.app_label
        tab = model._meta.db_table
        if app in BACAPPS.keys() and tab in BACAPPS[app]:
            return 'bacula'
        return None

    """
    A router to control all database operations on models in the Bacula application.
    """
    def db_for_read(self, model, **hints):
        return self._check_bacula(model)

    def db_for_write(self, model, **hints):
        return self._check_bacula(model)

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label in BACAPPS.keys() and obj2._meta.app_label in BACAPPS.keys():
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        if db == 'bacula':
            return False
        return None
