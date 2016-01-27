# Database routing classes



class Myth_To_Vid_Router(object):
    """
    This one should serve for most apps in this package.
    The default method for assigning a database is to query
    the model itself. If the model returns None or the
    attempt to ask it causes an Exception, use 'default'
    """
    @staticmethod
    def model_db_name(model):
        try:
            db = model.db_name()
            if db is None or db == '':
                db = 'default'
        except AttributeError: # In case model does not define db_name
            db = 'default'
        return db

    def db_for_read(self, model, **hints):
        return Myth_To_Vid_Router.model_db_name(model)
        

    def db_for_write(self, model, **hints):
        return Myth_To_Vid_Router.model_db_name(model)


    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Do not allow migrations for models using 'mythconverg' database.
        For now this is hardcoded. If the project should grow to use more
        databases in the future, maybe this method could check a central
        store in a config file to find a list of databases or models for
        which migration should be blocked.
        """
        if db == 'mythconverg':
            return False
        return None
