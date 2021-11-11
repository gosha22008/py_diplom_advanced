import sqlalchemy


class DB:

    def connect_db(self):
        db = 'postgresql://data_user:22@localhost:5432/vkinder'
        engine = sqlalchemy.create_engine(db)
        connection = engine.connect()
        return connection

    def create_table(self):
        connection = self.connect_db()
        req = '''
                create table if not exists users (
                id serial primary key,
                user_id varchar(30) unique,
                link_user varchar(30),
                link_photo varchar(100)
              );'''
        connection.execute(req)

    def select_user_id(self):
        connection = self.connect_db()
        req = '''
        SELECT user_id FROM users
        '''
        res = connection.execute(req)
        return res

    def write_user_db(self, link_user, link_photo, user_id):
        connection = self.connect_db()
        req = f'''
        INSERT INTO users (user_id, link_user, link_photo)
            VALUES ('{user_id}' ,'{link_user}', '{link_photo}')
        '''
        connection.execute(req)

    def read_db(self):
        pass


db = DB()
db.create_table()


