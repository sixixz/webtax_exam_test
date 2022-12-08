# encoding:utf8
import pymysql


class webtaxMysql(object):
    # Mysqldb 提供了connect 方法来与数据库的连接
    # 开发环境： host='192.168.43.202', user="root", port=3306, password="123456789", dbName='webtax_local_3_x'
    # 测试环境： host='120.78.124.90', user='root', port=4406, password='mysql@webtax', dbName='webtax_test'
    # 生产环境： host='192.168.1.122', user="tm", port=3306, password="XkT644OxgZJK$AA!", dbName='webtax'
    def __init__(self, host='120.78.124.90', user='root', port=4406, password='mysql@webtax', dbName='webtax_test'):
        self.db = pymysql.connect(host=host, port=port, user=user, passwd=password, db=dbName, charset='utf8')
        # 创建一个游标对象，通过游标对象来进行数据的增删改查。
        self.cursor = self.db.cursor()
        print('数据库已连接...')

    # 调用该对象的close() 方法来关闭数据库。
    def __del__(self):
        self.db.close()
        print('数据库已关闭...')

    # 对于不需要提交commit操作使用该方法，eg：查询
    def execute_select(self, sql):
        self.cursor.execute(sql)

    # 获取全部查询结果
    def fetchall(self):
        return self.cursor.fetchall()

    # 获取多行查询结果
    def fetchmany(self, size):
        return self.cursor.fetchmany(size)

    # 获取查询结果一行数据
    def fetchone(self):
        return self.cursor.fetchone()

    # 对于需要提交commit操作使用该方法，eg：插入，修改，删除
    def execute_commit(self, sql):
        # noinspection PyBroadException
        try:
            # 执行sql语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
        except:
            # 发生错误时回滚
            self.db.rollback()

    def commit(self):
        self.db.commit()


if __name__ == '__main__':
    sq = webtaxMysql()
    title = '下列关于房地产开发企业成本费用扣除的企业所得税处理中，正确的有（ ）。'
    sql = 'SELECT option_content FROM wt_exam_question_option WHERE question_id = (SELECT id FROM wt_exam_question WHERE question LIKE \'{}\' AND is_delete = 0 AND is_enable = 1 AND review = 1) AND is_right = 1'.format(
        title)
    sq.execute_select(sql)
    options = sq.fetchall()
    for option in options:
        print(option[0])
