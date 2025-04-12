import pymysql

class TABLE_SQL:
    def __init__(self, name, columns_dict, constraints = {}):
        self.name = name
        self.columns = columns_dict
        self.columns_name = list(columns_dict.keys())

        self.constraints = constraints

    def _create_self(self):
        query_segments = [f"CREATE TABLE {self.name}("]
        constraint = ""

        # Table columns
        for idx,column in enumerate(self.columns):
            if(column in self.constraints):
                constraint = self.constraints[column]

            query_segments.append(f"{column} {self.columns[column]} {constraint}")
            if(idx!=len(self.columns)-1):
                query_segments.append(",")
            constraint = ""

        # Table constraints
        for constraint in self.constraints:
            if(constraint not in self.columns_name):
                query_segments.append(f"CONSTRAINT {constraint} {self.constraints[constraint]},")

        query_segments.append(");")

        create_query = ''.join(str(query) for query in query_segments)
        return create_query

class DATABASE_SQL:
    def __init__(self):
        # Setup configs
        self.host = 'localhost'
        self.name = 'TrainManagement'
        self.user = 'root'
        self.password = 'pass@123'

        self.connection = None

    def database_setup(self, tables_list, triggers_list= []):
        self._connect()
        self.cursor=self.connection.cursor()

        self.cursor.execute(f"DROP DATABASE IF EXISTS {self.name}")
        self.cursor.execute(f"CREATE DATABASE {self.name}")
        print(f"Database {self.name} created.")

        self._set_database()

        # Create all other objects
        for table in tables_list:
            self.cursor.execute(table._create_self())

        for trigger in triggers_list:
            self.cursor.execute(trigger._create_self())

        print("Database Initialized")

        # End connection
        self.connection.commit()

        self._disconnect()

    def _connect(self):
        try:
            # Connect to MySQL server (without specifying DB)
            self.connection = pymysql.connect(
                host= self.host,
                user= self.user,
                password= self.password,
                charset='utf8mb4',
                # autocommit=True,
                cursorclass= pymysql.cursors.DictCursor
            )
        except Exception as e:
            print("Error:", e)
            exit()

    def _set_database(self):
        # Connect to the database
        self.connection.select_db(self.name)
        print(f"Database set to {self.name}")

    def _disconnect(self):
        self.connection.close()


if(__name__ == "__main__"):

    student_table = TABLE_SQL(
        "Students",
        columns_dict= {
            "Stid": "INT(5)",
            "Stname": "VARCHAR(20)",
        },
        constraints= {
            "Stid": "AUTO_INCREMENT PRIMARY KEY",
        }
    )


    train_table = TABLE_SQL(
        "Trains",
        columns_dict= {
            "Trid": "INT(5)",
            "Trname": "VARCHAR(20)",
            "Trstatus": r"ENUM('Departed','Stationed','Incoming')"
        },
        constraints= {
            "Trid": "AUTO_INCREMENT PRIMARY KEY",
        }
    )

    station_table = TABLE_SQL(
        "Stations",
        columns_dict= {
            "Sid": "INT(5)",
            "Sname": "VARCHAR(20)",
        },
        constraints= {
            "Sid": "AUTO_INCREMENT PRIMARY KEY",
        }
    )

    #print(station_table._create_self())

    TABLES_table = [
        student_table,
        train_table,
        station_table,
    ]


    db_interface = DATABASE_SQL()
    db_interface.database_setup(tables_list= TABLES_table)