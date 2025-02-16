import apsw
import apsw.bestpractice

apsw.bestpractice.apply(
    {
        practice
        for practice in apsw.bestpractice.recommended
        if practice.__name__.startswith("library_")
    }
)


class connectMySql:
    def __init__(self):
        self.user = "root"

    def apply_best_practice(self):
        for practice in apsw.bestpractice.recommended:
            if practice.__name__.startswith("connection_"):
                practice(self.my_connector)

    def apply_encryption(self, db, **kwargs):
        """You must include an argument for keying, and optional cipher configurations"""

        if db.in_transaction:
            raise Exception("Won't update encryption while in a transaction")

        def pragma_order(item):
            pragma = item[0].lower()
            if pragma == "cipher":
                return 1
            if pragma == "legacy":
                return 2
            if "legacy" in pragma:
                return 3
            if pragma not in {"key", "hexkey", "rekey", "hexrekey"}:
                return 3
            return 100

        if 1 != sum(1 if pragma_order(item) == 100 else 0 for item in kwargs.items()):
            raise ValueError("Exactly one key must be provided")

        for pragma, value in sorted(kwargs.items(), key=pragma_order):
            expected = "ok" if pragma_order((pragma, value)) == 100 else str(value)
            if db.pragma(pragma, value) != expected:
                raise ValueError(f"Failed to configure {pragma=}")

        db.pragma("user_version")

        try:
            with db:
                db.pragma("user_version", db.pragma("user_version"))
        except apsw.ReadOnlyError:
            pass

    def connect(self, dbname):
        self.my_connector = apsw.Connection(f"{dbname}")
        print("NAZWA:" + dbname)
        self.apply_encryption(self.my_connector, key="secret", kdf_iter=1000)
        self.apply_best_practice()
        self.my_cursor = self.my_connector.cursor()
        self.my_connector.execute(
            """ CREATE TABLE IF NOT EXISTS configuration_table (
        user_id INT,
        lowercase VARCHAR(45),
        uppercase VARCHAR(45),
        numbers VARCHAR(45),
        special_characters VARCHAR(45))   """
        )
        self.my_connector.execute(
            """ CREATE TABLE IF NOT EXISTS haslo_table (
        haslo VARCHAR(255),
        id INT,
        nazwa_uzytkownika VARCHAR(45),
        strona VARCHAR(45),
        user_id INT) """
        )
        self.my_connector.execute(
            """ CREATE TABLE IF NOT EXISTS user_table (
        user_id INT,
        initial_id INT,
        user_name VARCHAR(45),
        password VARCHAR(255) )"""
        )

    def getting_data(self, sql, dbname, parameters):
        self.connect(dbname=dbname)

        try:
            result = self.my_cursor.execute(sql, parameters)
            result1 = result.fetchone()
            return result1
        except Exception as E:
            print(E)
            return
        finally:
            if self.my_connector:
                self.my_cursor.close()

    def getting_more_data(self, sql, dbname, parameters):
        self.connect(dbname=dbname)

        try:
            result = self.my_cursor.execute(sql, parameters)
            result1 = result.fetchall()
            return result1
        except Exception as E:
            print(E)
            return
        finally:
            if self.my_connector:
                self.my_cursor.close()

    def updating_data(self, sql, dbname, parameters):
        self.connect(dbname=dbname)
        try:
            self.my_cursor.execute(sql, parameters)

        except Exception as E:
            self.my_connector.__exit__()
            return E
        finally:
            if self.my_connector:
                self.my_cursor.close()

    def getting_id(self, name_db):
        sql = """SELECT initial_id FROM user_table"""
        result = self.getting_data(dbname=name_db, sql=sql, parameters=())
        return result[0]

    def increase_id(self, name_db):
        value_id = self.getting_id(name_db=name_db)
        return value_id

    def increase_global_id(self, name_db):
        sql = f"""UPDATE user_table SET initial_id=initial_id+1 """
        result = self.updating_data(sql=sql, dbname=name_db, parameters=())
        return result

    def create_db(self, name_db, password, user_name, user_id):
        self.my_connector = apsw.Connection(f"{name_db}")
        self.apply_encryption(self.my_connector, key="secret", kdf_iter=1000)
        self.my_cursor = self.my_connector.cursor()
        initial_id = 0
        self.my_connector.execute(
            """ CREATE TABLE IF NOT EXISTS configuration_table (
        user_id INT,
        lowercase VARCHAR(45),
        uppercase VARCHAR(45),
        numbers VARCHAR(45),
        special_characters VARCHAR(45))   """
        )
        self.my_connector.execute(
            """ CREATE TABLE IF NOT EXISTS haslo_table (
        haslo VARCHAR(255),
        id INT,
        nazwa_uzytkownika VARCHAR(45),
        strona VARCHAR(45),
        user_id INT) """
        )
        self.my_connector.execute(
            """ CREATE TABLE IF NOT EXISTS user_table (
        user_id INT,
        initial_id INT,
        user_name VARCHAR(45),
        password VARCHAR(255) )"""
        )
        parameters = (f"{initial_id}", f"{user_name}", f"{password}", f"{user_id}")
        self.my_connector.execute(
            f"""INSERT INTO user_table (initial_id, user_name,password,user_id) VALUES (?,?,?,?)""",
            parameters,
        )
        self.my_cursor.close()

        return False

    def check_username(self, username, dbname):
        sql = f"SELECT password FROM user_table WHERE user_name=?"
        parameters = (f"{username}",)
        result = self.getting_data(sql=sql, dbname=dbname, parameters=parameters)
        return result[0]

    def get_passwords(self, user_id, search_username, search_website, dbname):
        sql = f"""
            SELECT * FROM haslo_table
                WHERE user_id =?
                    AND nazwa_uzytkownika LIKE ?
                    AND strona LIKE ?
        """
        parameters = (user_id, f"%{search_username}%", f"%{search_website}%")
        result = self.getting_more_data(sql=sql, dbname=dbname, parameters=parameters)
        return result

    def get_password(self, user_id, dbname):
        sql = f"SELECT haslo FROM haslo_table WHERE id=?"
        parameters = (user_id,)
        result = self.getting_data(sql=sql, dbname=dbname, parameters=parameters)
        return result

    def delete_passwords(self, id, dbname):
        sql = f"DELETE FROM haslo_table WHERE id=?"
        parameters = (id,)
        result = self.updating_data(sql=sql, dbname=dbname, parameters=parameters)
        return result

    def add_new_password(self, user_id, user_name, website, password, dbname):
        id = self.increase_id(name_db=dbname)
        self.increase_global_id(name_db=dbname)
        sql = f"""INSERT INTO haslo_table (user_id,id, nazwa_uzytkownika,strona,haslo) VALUES (?,?,?,?,?)"""
        parameters = (user_id, id, f"{user_name}", f"{website}", f"{password}")
        result = self.updating_data(sql=sql, dbname=dbname, parameters=parameters)
        return result

    def create_config(
        self, user_id, dbname, lowercase, uppercase, numbers, special_characters
    ):
        sql1 = f"""INSERT INTO configuration_table (user_id,lowercase,uppercase,numbers,special_characters) VALUES (?,?,?,?,?)"""
        parameters = (
            user_id,
            f"{lowercase}",
            f"{uppercase}",
            f"{numbers}",
            f"{special_characters}",
        )
        result1 = self.updating_data(sql=sql1, dbname=dbname, parameters=parameters)

        return result1

    def check_config(self, user_id, dbname):
        sql = f"SELECT * FROM configuration_table WHERE user_id=?"
        parameters = (user_id,)
        result = self.getting_data(sql=sql, dbname=dbname, parameters=parameters)
        return result

    def update_config(
        self, dbname, user_id, lowercase, uppercase, numbers, special_characters
    ):
        sql = f"""UPDATE configuration_table
                    SET lowercase=?,uppercase=?,numbers=?,special_characters=?
                    WHERE user_id=?
        """
        parameters = (
            f"{lowercase}",
            f"{uppercase}",
            f"{numbers}",
            f"{special_characters}",
            user_id,
        )
        result = self.updating_data(sql=sql, dbname=dbname, parameters=parameters)

        return result
#SIEMA