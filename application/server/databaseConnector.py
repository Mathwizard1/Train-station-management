import pymysql

class DatabaseConnector:
    def __init__(self):
        self.host = 'localhost'
        self.user = 'root'
        self.password = 'pass@123'
        self.connection = None
        self.dbname=""
        self.tables=[]
        self.triggers=[]
    
    #Connect To Server (OPTIONAL: Connect to Database)
    def connect(self,dbname=""):
        try:
            self.connection=pymysql.connect(host=self.host,
                                            user=self.user,
                                            password=self.password,
                                            charset='utf8mb4',
                                            cursorclass= pymysql.cursors.DictCursor)
            self.cursor=self.connection.cursor()
            print(f"Connection Established With Server")
        except:
            print(f"ERROR: Could Not Connect To Server")
            return

        if(dbname!=""):
            self.set_database(dbname=dbname)

    #Select Database And Store Tables
    def set_database(self,dbname):
        try:
            self.connection.select_db(dbname)
            self.dbname=dbname
            self.get_tables(store=True)
            print(f"Connected To Database {dbname}")
        except:
            print(f"ERROR: Could Not Connect To Database {dbname}")
            return

    #Retrieve Tables
    def get_tables(self,store=False):
        if(self.dbname==""):
            print("ERROR: Database Not Set")
            return

        try:
            self.execute_query("SHOW TABLES;")
            tabledicts=self.cursor.fetchall()
            tables=[]
            for dict in tabledicts:
                tables.append(list(dict.values())[0])
            
            if(store):
                self.tables=tables
                return
            else:
                return tables

        except:
            print("ERROR: Could Not Retrieve Tables")
            return


    #Execute Query
    def execute_query(self,query):
        try:
            self.cursor.execute(query=query)
        except:
            print(f"ERROR: Could Not Execute Query '{query}'")




if __name__=="__main__":
    connector=DatabaseConnector()
    connector.connect("trainmanagement")
