import random


class MarioRouter(object):
    def db_for_read(self, model, **hints):
        # print model.__dict__
        if hasattr(model._meta, 'mario'):
            return 'mario'
        return None

    def db_for_write(self, model, **hints):
        if hasattr(model._meta, 'mario'):
            return 'mario'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, model):
        """
        All non-auth models end up in this pool.
        """
        return True