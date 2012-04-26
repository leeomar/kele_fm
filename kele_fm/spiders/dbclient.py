#/bin/python
import MySQLdb

class DBClient(object):
    
    def open(self):
        self.conn = MySQLdb.connect(user='ee', 
            passwd="f5K9ypTS", db="db_for_ee", charset="utf8")
        self.conn.cursor().execute('SET NAMES UTF8')

    def close(self):
        self.conn.close()

    def insert(self, item):
        self.cursor = self.conn.cursor()
        sql = "insert into goods(url, title, price, default_price, img, tag, \
            cat) values ('%s', '%s', %s, %s, '%s', '%s', '%s')" % (item.get('url'),
            item.get('title'),item.get('price'), item.get('default_price', 0), 
            item.get('img'), item.get('tag'), item.get('cat', ''))
        self.cursor.execute(sql)
        self.cursor.close()
        self.conn.commit()
        '''
        self.cursor = self.conn.cursor()
        sql = """insert into goods(url, title, price, default_price, img, tag, \
            cat) values (%s, %s, %s, %s, %s, %s, %s)"""
        self.cursor.execute(sql,
            (item.get('url'),item.get('title'),item.get('price'),
            item.get('default_price', 0), item.get('img'), item.get('tag'),
            item.get('cat', '')))
        self.cursor.close()
        '''
        print "save item: %s" % item.get('url')

if __name__ == '__main__':
    client = DBClient()
    client.open()
