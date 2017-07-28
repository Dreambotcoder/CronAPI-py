def get_database_uri():
    db_connection = "%s://%s:%s@%s:%s/%s" % ('mysql',
                                             'root',
                                             '',
                                             '127.0.0.1',
                                             '3306',
                                             'cronapi'
                                             )
    return db_connection