import pymysql
import numpy as np
import datetime

class DatabaseConnector:
    def __init__(self):
        self.host = 'localhost'
        self.user = 'root'
        self.password = 'pass@123'
        self.connection = None
        self.dbname=""
        self.tables=[]
        self.triggers=[]
        self.errorflag=False
    
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
            self.errorflag=True

        if(dbname!=""):
            return self.set_database(dbname=dbname)

    #Select Database And Store Tables
    def set_database(self,dbname):
        try:
            self.connection.select_db(dbname)
            self.dbname=dbname
            self.get_tables(store=True)
            print(f"Connected To Database {dbname}")
        except:
            print(f"ERROR: Could Not Connect To Database {dbname}")
            self.errorflag=True

    #Retrieve Tables
    def get_tables(self,store=False):
        if(self.dbname==""):
            print("ERROR: Database Not Set")
            self.errorflag=True

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
            self.errorflag=True

    #Add Entry
    def insert_entry(self,table,entry):
        try:
            query=f"INSERT INTO {table} VALUES ("
            for idx,value in enumerate(entry):

                if(type(value)==str or type(value)==datetime.datetime):
                    if(value=='NULL'):
                        query+=f"{value}"
                    else:
                        query+=f"'{value}'"
                else:
                    query+=f"{value}"

                if(idx!=len(entry)-1):
                    query+=","

            query+=");"
            self.execute_query(query=query,commit=True)
        except:
            print(f"ERROR: Could Not Add Entry Into {table}")
            self.errorflag=True
    
    def clear_table(self,table):
        query=f"DELETE FROM {table};"
        self.execute_query(query=query,commit=True)

    #Execute Query
    def execute_query(self,query,commit=False):
        try:
            self.cursor.execute(query=query)
            if(commit):
                self.connection.commit()
        except:
            print(f"ERROR: Could Not Execute Query '{query}'")
            self.errorflag=True


    ##########
    #COMMANDS#
    ##########

    # gets row count
    def get_row_count(self, table):
        query = f"SELECT COUNT(*) FROM {table};"
        self.execute_query(query=query, commit= False)
        row_count = self.cursor.fetchone()
        return row_count['COUNT(*)']

    #Retrieve ALL values
    def retrieve_values(self,table,column="*", where=""):
        query=f"SELECT {column} FROM {table} {where};"
        self.execute_query(query=query,commit=False)
        rows=self.cursor.fetchall()
        output=[]
        for row in rows:
            out=[]
            for entry in row:
                out.append(row[entry])
            output.append(out)

        return output
    
    def retrieve_schedules(self,dept="All",arr="All",where=""):
        rows=self.retrieve_values("schedules",where=where)

        query=f"SELECT Trid,Trname from trains;"
        self.execute_query(query)
        traindata=self.cursor.fetchall()

        traindict={}
        for data in traindata:
            traindict[data["Trid"]]=data["Trname"]
        
        query=f"SELECT Stid,Stname from stations;"
        self.execute_query(query)
        stationdata=self.cursor.fetchall()

        stationdict={}
        for data in stationdata:
            stationdict[data["Stid"]]=data["Stname"]
        
        arv_stat = set()
        dep_stat = set()

        for row in rows:
            row[1]=traindict[row[1]]
            row[2]=stationdict[row[2]]
            row[3]=row[3].strftime('%I:%M:%S %p %d/%m/%Y')
            row[4]=stationdict[row[4]]
            row[5]=row[5].strftime('%I:%M:%S %p %d/%m/%Y')

            arv_stat.add(row[2])
            dep_stat.add(row[4])
        
        if(dept!="All" or arr!="All"):
            temprows=[]
            for row in rows:
                if(dept!="All" and arr!="All"):
                    if(row[2]==arr and row[4]==dept):
                        temprows.append(row)
                elif(row[2]==arr or row[4]==dept):
                    temprows.append(row)
            rows=temprows 

        return rows, tuple(arv_stat), tuple(dep_stat)
    
    #Convert Train Name to Train ID
    def train_id_retriever(self,train_name):
        query=f"SELECT tr.Trid FROM coach_infos as coi inner join trains as tr on coi.CiTrid=tr.Trid where tr.Trname='{train_name}';"
        self.execute_query(query)
        row=self.cursor.fetchone()
        if(row==None):
            print("ERROR: No Such Train")
        else:
            return row["Trid"]

    def train_coach_retriver(self,train_id):
        query=f"SELECT CiConame FROM coach_infos WHERE CiTrid= {train_id};"
        self.execute_query(query)
        rows=self.cursor.fetchall()
        output=[]
        for row in rows:
            out=[]
            for entry in row:
                out.append(row[entry])
            output.append(out)

        return output
    
    def get_customer_data(self, customer_id):
        query=f"SELECT Cuname,Cuage,Cugender FROM Customers WHERE Cuid= {customer_id};"
        self.execute_query(query=query,commit=False)
        row = self.cursor.fetchone()
        return row

    #Check Ticket Availability in Coach
    def check_ticket_availability(self,train,coach):
        if(type(train)==str):
            train=self.train_id_retriever(train)
            if(train==True):
                return True

        query=f"SELECT * FROM coach_infos where CiConame='{coach}' and CiTrid={train};"
        self.execute_query(query=query)
        row=self.cursor.fetchone()
        if(row==None):
            return "No Such Coach"
        if(row['Cisize']<row['CiComaxsize']):
            return True
        else:
            return False
        
    #Create Ticket
    def create_ticket(self,train,coach,custid,check_available=False):
        if isinstance(train,str):
            train=self.train_id_retriever(train)
            if(train==True):
                return True
        
        if(check_available):
            if(not self.check_ticket_availability(train,coach)):
                print("Ticket Not Available")
                return True
        
        query=f"SELECT CiComaxsize from coach_infos where CiTrid={train} and CiConame='{coach}';"
        self.execute_query(query)
        row=self.cursor.fetchone()
        maxsize=row["CiComaxsize"]

        all_seats=[i for i in range(1,maxsize+1)]
        
        query=f"SELECT Tiseatnum FROM tickets where TiTrid={train} and TiConame='{coach}';"
        self.execute_query(query)
        rows=self.cursor.fetchall()
        taken_seats=[]
        for row in rows:
            taken_seats.append(row["Tiseatnum"])
        
        available_seats=list(set(all_seats)-set(taken_seats))

        if(len(available_seats)==0):
            print("No Seats Available")
            return True

        query=f"select sysdate();"
        self.execute_query(query)
        row=self.cursor.fetchone()
        
        bookingtime=row['sysdate()']
        seatnum=available_seats[np.random.randint(0,len(available_seats))]
        ticketid=np.random.randint(10000,100000)

        self.insert_entry(table="tickets",entry=[ticketid,train,coach,custid,seatnum,bookingtime])

        query=f"UPDATE coach_infos SET Cisize=Cisize+1 where CiTrid={train} and CiConame='{coach}';"
        self.execute_query(query,commit=True)

    #Create Waiting
    def create_waiting(self,train,coach,custid):
        if(type(train)==str):
            train=self.train_id_retriever(train)

        query=f"select sysdate();"
        self.execute_query(query)
        row=self.cursor.fetchone()
        
        waittime=row['sysdate()']
        waitid=np.random.randint(10000,100000)

        self.insert_entry(table='waitings',entry=[waitid,waittime,custid,train,coach])

    #Cancel Ticket
    def cancel_ticket(self,custid,train,coach,autoupgrade=True):
        if(type(train)==str):
            train=self.train_id_retriever(train)

        query=f"SELECT Tiseatnum from tickets where TiTrid={train} and TiConame='{coach}' and TiCuid={custid};"
        self.execute_query(query)
        row=self.cursor.fetchone()

        seatnum=row['Tiseatnum']

        query=f"DELETE FROM tickets where TiTrid={train} and TiConame='{coach}' and TiCuid={custid};"
        self.execute_query(query,commit=True)

        query=f"UPDATE coach_infos SET Cisize=Cisize-1 where CiTrid={train} and CiConame='{coach}'"
        self.execute_query(query,commit=True)
        
        if(autoupgrade):
            query=f"SELECT * FROM waitings where Watime=(select min(Watime) from waitings);"
            self.execute_query(query)
            row=self.cursor.fetchone()

            if(row==None):
                return

            query=f"select sysdate();"
            self.execute_query(query)
            timerow=self.cursor.fetchone()
        
            bookingtime=timerow['sysdate()']

            self.insert_entry(table="tickets",entry=[row["Waid"],train,coach,row["WaCuid"],seatnum,bookingtime])
            query=f"UPDATE coach_infos SET Cisize=Cisize+1 where CiTrid={train} and CiConame='{coach}'"
            self.execute_query(query,commit=True)

            query=f"DELETE FROM waitings where Waid={row["Waid"]}"
            self.execute_query(query,commit=True)
        
        return
    
    #Update Train Status
    def update_train_status(self,train,newstatus):
        if(type(train)==str):
            train=self.train_id_retriever(train)
            if(train==True):
                return train

        query=f"UPDATE trains SET Trstatus='{newstatus}' where Trid={train};"
        self.execute_query(query,commit=True)

        if(newstatus=="Stationed"):
            query=f"DELETE FROM tickets where TiTrid={train};"
            self.execute_query(query,commit=True)
            query=f"UPDATE coach_infos SET Cisize=0 where CiTrid={train};"
            self.execute_query(query,commit=True)

        return

    #Add Customer
    def add_customer(self,info):
        query=f"SELECT * FROM customers where Cuid={info[0]};"
        self.execute_query(query)
        row=self.cursor.fetchone()
        if(row!=None):
            print(f"ERROR: Duplicate ID '{info[0]}' Found")
            return False

        query=f"INSERT INTO customers VALUES ({info[0]},'{info[1]}',{info[2]},'{info[3]}','{info[4]}');"
        self.execute_query(query,commit=True)
        


if __name__=="__main__":

    connector=DatabaseConnector()
    connector.connect("trainmanagement")