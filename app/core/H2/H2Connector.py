import time
import jaydebeapi
import os

try:
    os.makedirs('datas/sql')
except Exception as e:
    pass


class H2Connector():
    def __init__(self, user_name, password, host, db_name):
        self.user_name = user_name
        self.password = password
        self.db_name = db_name
        self.jar_path = 'static/h2-2.1.214.jar'
        self.url = f'jdbc:h2:tcp://{host}/{db_name};MODE=MYSQL;FILE_LOCK=SOCKET'

    def get_connection(self):
        conn = jaydebeapi.connect('org.h2.Driver',
                                  self.url,
                                  [self.user_name, self.password],
                                  self.jar_path)
        return conn

    def execute_sql(self, sql):
        """
        执行sql语句,返回执行结果
        :param sql:
        :return:
        """
        conn = self.get_connection()
        curs = conn.cursor()
        result = ['执行成功']
        try:
            curs.execute(sql)
            conn.commit()
        except Exception as e:
            return [str(e)]
        finally:
            curs.close()
            conn.close()
        time.sleep(1)
        return result
