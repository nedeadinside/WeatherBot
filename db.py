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
            values = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()[0][1:]
            keys = ['user_id', 'latitude', 'longitude', 'time']
            return {keys[i]: values[i] for i in range(len(values))}

    def delete_user(self, user_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,)).fetchall()
