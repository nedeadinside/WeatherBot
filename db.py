import sqlite3


class Database:
    def __init__(self, db_file):
        self.database_file = db_file
        self.connection = sqlite3.connect(self.database_file)
        self.cursor = self.connection.cursor()

    def user_exist(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE `user_id` = ?", (user_id,)).fetchall()
        return bool(len(result))

    def create_user(self, user_id, user_info: dict):
        lat = round(user_info['lat'], 2)
        lon = round(user_info['lon'], 2)
        time = user_info['time']
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO users (user_id, latitude, longitude, time) VALUES (?, ?, ?, ?)",
                (user_id, lat, lon, time,)).fetchall()

    def get_user_info(self, user_id):
        with self.connection:
            values = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()[0]
            keys = ('user_id', 'latitude', 'longitude', 'time')
            return {keys[i]: values[i] for i in range(len(values))}

    def delete_user(self, user_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,)).fetchall()

    def get_time(self, time):
        with self.connection:
            user_list = []
            users = self.cursor.execute("SELECT * FROM users WHERE time = ?", (time,)).fetchall()
            keys = ('id', 'user_id', 'latitude', 'longitude', 'time')
            for user in users:
                user_list.append({keys[i]: user[i] for i in range(len(user))})
            return user_list

    def rewrite_location(self, user_id, latitude, longitude):
        with self.connection:
            return self.cursor.execute(
                 "UPDATE users SET latitude = ?,  longitude = ? WHERE user_id = ?", (latitude, longitude, user_id,)
            ).fetchall()

    def rewrite_time(self, user_id, time):
        with self.connection:
            return self.cursor.execute(
                "UPDATE users SET time = ? WHERE user_id = ?", (time, user_id,)).fetchall()
