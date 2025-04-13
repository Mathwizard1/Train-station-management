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

    #Add Entry
    def insert_entry(self,table,entry):
        try:
            query=f"INSERT INTO {table} VALUES ("
            for idx,value in enumerate(entry):

                if(type(value)==str):
                    if(value=='NULL'):
                        query+=f"{value}"
                    else:
                        query+=f"'{value}'"
                else:
                    query+=f"{value}"

                if(idx!=len(entry)-1):
                    query+=","

            query+=");"
            self.execute_query(query=query)
            
        except:
            print(f"ERROR: Could Not Add Entry Into {table}")
            return
    
    def clear_table(self,table):
        query=f"DELETE FROM {table};"
        self.execute_query(query=query)

    #Execute Query
    def execute_query(self,query,commit=True):
        try:
            self.cursor.execute(query=query)
            if(commit):
                self.connection.commit()
        except:
            print(f"ERROR: Could Not Execute Query '{query}'")

    #COMMANDS

    #Retrieve ALL values
    def retrieve_values(self,table):
        query=f"SELECT * FROM {table};"
        self.execute_query(query=query)
        rows=self.cursor.fetchall()
        output=[]
        for row in rows:
            out=[]
            for entry in row:
                out.append(row[entry])
            output.append(out)
        return output
    
    #Check Ticket Availability in Coach
    def check_ticket_availability(self,train,coach):
        if(type(train)==str):
            query=f"SELECT * FROM coach_infos as coi inner join trains as tr on coi.CiTrid=tr.Trid where CiConame='{coach}' and Trname='{train}';"
        else:
            query=f"SELECT * FROM coach_infos where CiConame='{coach}' and CiTrid={train};"
        self.execute_query(query=query)
        row=self.cursor.fetchone()
        if(row['Cisize']<row['CiComaxsize']):
            return True
        else:
            return False
    
    def add_customer(self,info):
        query=f"INSERT INTO customers VALUES ({info[0]},'{info[1]}',{info[2]},'{info[3]}')"
        self.execute_query(query=query)
        


if __name__=="__main__":

    connector=DatabaseConnector()
    connector.connect("trainmanagement")
    connector.clear_table('customers')
    connector.add_customer([1,'Tejeshwar',20,'M'])
    print(connector.retrieve_values('customers'))