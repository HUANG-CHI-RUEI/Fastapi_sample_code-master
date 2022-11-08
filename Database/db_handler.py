from lib2to3.pgen2 import driver
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import create_session, sessionmaker


class DBHandler():
    def __init__(self, db_app='mysql',drivername='mysql+pymysql', database='', password='',host='127.0.0.1', port='3306'):
        if db_app == 'sql server':
            self.url = URL(drivername=drivername,
                            database=database,
                            username=username,
                            password=password,
                            host=host,
                            port=port,
                            query=dict(driver='FreeTDS'))

        else:
            self.url = URL(drivername=drivername,
                            database=database,
                            username=username,
                            password=password,
                            host=host,
                            port=port)
        self.engine = create_engine(self.url)

        self.session = sessionmaker(bind=self.engine)() 
        self.conn = self.engine.connect()

if __name__=='__main__':
    import pandas as pd

    d = DBHandler(database='', port='')
    #Select
    result = d.conn.execute('SELECT * FROM auth_user')
    df = pd.read_sql(result.statement, d.session.bind)                   