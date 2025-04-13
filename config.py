import pymysql

class TABLE_SQL:
    def __init__(self, name, columns_dict, constraints = {}):
        self.name = name
        self.columns = columns_dict
        self.columns_name = list(columns_dict.keys())

        self.constraints = constraints
        self.fill_query = None

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
        for idx,constraint in enumerate(self.constraints):
            if(constraint not in self.columns_name):
                query_segments.append(",")
                query_segments.append(f"CONSTRAINT {constraint} {self.constraints[constraint]}")

        query_segments.append(");")

        create_query = ''.join(str(query) for query in query_segments)
        return create_query
    
    def _fill_self(self, col_data: tuple):
        query_segments = [f"INSERT INTO {self.name} values"]
        for idx, data in enumerate(col_data):
            query_segments.append(f"{data}")
            if(idx != len(col_data) - 1):
                query_segments.append(",")
            else:
                query_segments.append(";")
        self.fill_query = ''.join(str(query) for query in query_segments)

    def _create_fill(self):
        return self.fill_query

class DATABASE_SQL:
    def __init__(self):
        # Setup configs
        self.host = 'localhost'
        self.name = 'TrainManagement'
        self.user = 'root'
        self.password = 'pass@123'

        self.connection = None
        self.cursor = None

    def database_setup(self, tables_list, triggers_list= []):
        self._connect()
        self.cursor=self.connection.cursor()

        self.cursor.execute(f"DROP DATABASE IF EXISTS {self.name}")
        self.cursor.execute(f"CREATE DATABASE {self.name}")
        print(f"Database {self.name} created.")

        self._set_database()

        try:
            # Create all other objects
            for table in tables_list:
                self.cursor.execute(table._create_self())

            print("Tables Initialized")
        except:
            print("Error in Initialization Table.")
            exit(0)

        try:
            # Create all other objects
            for trigger in triggers_list:
                self.cursor.execute(trigger._create_self())

            print("Triggers Initialized")
        except:
            print("Error in Initialization Trigger.")
            exit(0)

        print("database Initialised.")

        # End connection
        self.connection.commit()
        self._disconnect()

    def database_fillup(self, tables_list):
        self._connect()
        self.cursor = self.connection.cursor()

        self._set_database()
        
        try:
            # Fill all tables
            for table in tables_list:
                self.cursor.execute(table._create_fill())

            print("Tables Filled")
        except:
            print("Error in Filling Tables.")
            exit(0)

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
        # End connection
        self.cursor = None
        self.connection.close()


if(__name__ == "__main__"):

    station_table = TABLE_SQL(
        "Stations",
        columns_dict= {
            "Stid": "INT(5)",
            "Stname": "VARCHAR(20)",
            "Stcity": "VARCHAR(20)"
        },
        constraints= {
            "Stid": "AUTO_INCREMENT PRIMARY KEY",
        }
    )
    station_table._fill_self(
        (
            (12, "New Delhi", "Delhi"),
            (56, "Mumbai Central", "Mumbai"),
            (89, "Howrah Junction", "Kolkata"),
            (34, "Chennai Central", "Chennai"),
            (71, "Bangalore City", "Bengaluru"),
            (23, "Secunderabad Jn", "Hyderabad"),
            (95, "Ahmedabad Jn", "Ahmedabad"),
            (47, "Pune Junction", "Pune"),
            (68, "Jaipur Junction", "Jaipur"),
            (19, "Lucknow NR", "Lucknow"),
            (82, "Kanpur Central", "Kanpur"),
            (30, "Nagpur Junction", "Nagpur"),
            (75, "Patna Junction", "Patna"),
            (41, "Vadodara Jn", "Vadodara"),
            (63, "Indore Junction", "Indore"),
            (98, "Bhopal Junction", "Bhopal"),
            (27, "Visakhapatnam", "Visakhapatnam"),
            (50, "Allahabad Jn", "Prayagraj"),
            (78, "Coimbatore Jn", "Coimbatore"),
            (37, "Madurai Junction", "Madurai")
        )
    )

    #print(station_table._create_fill())

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

    customer_table = TABLE_SQL(
        "Customers",
        columns_dict= {
            "Cuid": "INT(5)",
            "Cuname": "VARCHAR(20)",
            "Cuage": "INT(3)",
            "Cugender": "CHAR(1)"   
        },
        constraints= {
            "Cuid": "AUTO_INCREMENT PRIMARY KEY",
        }
    )

    schedule_table = TABLE_SQL(
        "Schedules",
        columns_dict= {
            "Shid": "INT(5)",
            "ShTrid": "INT(5)",
            "SharvStid": "INT(5)",
            "Sharvtime": "DATETIME",
            "ShdepStid": "INT(5)",
            "Shdeptime": "DATETIME",
        },
        constraints= {
            "Shid": "AUTO_INCREMENT PRIMARY KEY",
            "fk_ShTrid": "FOREIGN KEY(ShTrid) REFERENCES Trains(Trid)",
            "fk_SharvStid": "FOREIGN KEY(SharvStid) REFERENCES Stations(Stid)",
            "fk_ShdepStid": "FOREIGN KEY(ShdepStid) REFERENCES Stations(Stid)"
        }
    )

    coach_table = TABLE_SQL(
        "Coachs",
        columns_dict= {
            "Coname": "CHAR(5)",
            "Comaxsize": "INT(5)"
        },
        constraints= {
            "Coname": "PRIMARY KEY",
        }
    )

    coach_info_table = TABLE_SQL(
        "Coach_infos",
        columns_dict= {
            "CiTrid": "INT(5)",
            "CiConame": "CHAR(5)",
            "Cisize": "INT(2)",
            "CiComaxsize": "INT(5)",
            "Cioversize": "INT(2)"
        },
        constraints= {
            "pk_TrCo": "PRIMARY KEY(CiTrid, CiConame)",
            "fk_CiTrid": "FOREIGN KEY(CiTrid) REFERENCES Trains(Trid)",
            "fk_CiConame": "FOREIGN KEY(CiConame) REFERENCES Coachs(Coname)"
        }
    )

    ticket_table = TABLE_SQL(
        "Tickets",
        columns_dict= {
            "Tiid": "CHAR(5)",
            "TiTrid": "INT(5)",
            "TiConame": "CHAR(5)",
            "TiCuid": "INT(5)",
            "Tiseatnum": "INT(3)",
            "Tibooking": "DATETIME"
        },
        constraints= {
            "Tiid": "PRIMARY KEY",
            "fk_TiTrCo": "FOREIGN KEY(TiTrid, TiConame) REFERENCES Coach_infos(CiTrid, CiConame)",
            "fk_TiCuid": "FOREIGN KEY(TiCuid) REFERENCES Customers(Cuid)",
        }
    )

    waiting_table = TABLE_SQL(
        "Waitings",
        columns_dict= {
            "Waid": "INT(5)",
            "Watime": "DATETIME",
            "WaCuid": "INT(5)",
            "WaTrid": "INT(5)",
            "WaConame": "CHAR(5)",
            "Wapref": "CHAR(5)"
        },
        constraints= {
            "Waid": "AUTO_INCREMENT PRIMARY KEY",
            "fk_WaCuid": "FOREIGN KEY(WaCuid) REFERENCES Customers(Cuid)",
            "fk_WaTrCo": "FOREIGN KEY(WaTrid, WaConame) REFERENCES Coach_infos(CiTrid, CiConame)"
        }
    )

    cancellation_table = TABLE_SQL(
        "Cancelletations",
        columns_dict= {
            "Caid": "INT(5)",
            "CaCuid": "INT(5)",
            "CaTrid": "INT(5)",
            "CaConame": "CHAR(5)",
            "Catime": "DATETIME"
        },
        constraints= {
            "Caid": "AUTO_INCREMENT PRIMARY KEY",
            "fk_CaCuid": "FOREIGN KEY(CaCuid) REFERENCES Customers(Cuid)",
            "fk_CaTrCo": "FOREIGN KEY(CaTrid, CaConame) REFERENCES Coach_infos(CiTrid, CiConame)"
        }
    )

    #print(coach_info_table._create_self())

    TABLES_table = [
        station_table,
        train_table,
        customer_table,
        schedule_table,
        coach_table,
        coach_info_table,
        waiting_table,
        cancellation_table
    ]

    FILL_table = [
        station_table
    ]

    db_interface = DATABASE_SQL()
    db_interface.database_setup(tables_list= TABLES_table)
    db_interface.database_fillup(tables_list= FILL_table)