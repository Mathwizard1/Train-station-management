from datetime import date, timedelta, datetime
import time
import random
from config import train_data,station_data
from application.server.databaseConnector import DatabaseConnector

# train_data = (
#         (123, "Rajdhani Express", "Departed"),
#         (456, "Shatabdi Exp", "Stationed"),
#         (789, "Duronto Express", "Incoming"),
#         (234, "Kerala Express", "Departed"),
#         (567, "Tamil Nadu Exp", "Stationed"),
#         (890, "Karnataka Exp", "Incoming"),
#         (345, "Andhra Pradesh", "Departed"),
#         (678, "Gujarat Mail", "Stationed"),
#         (901, "Mumbai Rajdhani", "Incoming"),
#         (457, "Howrah Mail", "Departed"),
#         (780, "Coromandel Exp", "Stationed"),
#         (129, "Ganga Sagar Exp", "Incoming"),
#         (561, "Godavari Exp", "Departed"),
#         (893, "Telangana Exp", "Stationed"),
#         (235, "Himachal Exp", "Incoming"),
#         (679, "Deccan Queen", "Departed"),
#         (902, "Konark Express", "Stationed"),
#         (346, "Udyan Express", "Incoming"),
#         (781, "Falaknuma Exp", "Departed"),
#         (124, "Brindavan Exp", "Stationed")
#     )
# station_data = (
#         (12, "New Delhi", "Delhi"),
#         (56, "Mumbai Central", "Mumbai"),
#         (89, "Howrah Junction", "Kolkata"),
#         (34, "Chennai Central", "Chennai"),
#         (71, "Bangalore City", "Bengaluru"),
#         (23, "Secunderabad Jn", "Hyderabad"),
#         (95, "Ahmedabad Jn", "Ahmedabad"),
#         (47, "Pune Junction", "Pune"),
#         (68, "Jaipur Junction", "Jaipur"),
#         (19, "Lucknow NR", "Lucknow"),
#         (82, "Kanpur Central", "Kanpur"),
#         (30, "Nagpur Junction", "Nagpur"),
#         (75, "Patna Junction", "Patna"),
#         (41, "Vadodara Jn", "Vadodara"),
#         (63, "Indore Junction", "Indore"),
#         (98, "Bhopal Junction", "Bhopal"),
#         (27, "Visakhapatnam", "Visakhapatnam"),
#         (50, "Allahabad Jn", "Prayagraj"),
#         (78, "Coimbatore Jn", "Coimbatore"),
#         (37, "Madurai Junction", "Madurai")
#     )

def create_schedule():
    schedule_data=[]
    st_sample=[]
    timedeltasamples=[10,15,20,25,30,35,40,45,50,55,60]

    for i in range(20):
        for j in range(20):
            if i==j:
                continue
            st_sample.append((station_data[i], station_data[j]))

    start_time = datetime.strptime("00:00:00", "%H:%M:%S")
    day=str(date.today() + timedelta(days=0))
    used=[]
    totaltime=0
    idcounter=0
    prevtrainbuffer=[random.randint(0,len(train_data)-1),random.randint(0,len(train_data)-1)]
    for k in range(len(st_sample)):
        used.append(0)
    while(totaltime<24*60):
        minutes=timedeltasamples[random.randint(0,len(timedeltasamples)-1)]
        interval = timedelta(minutes=minutes)
        totaltime+=minutes
        sch=[]
        sch.append(1000+(i*len(train_data))+idcounter)
        idcounter+=1
        
        trainnum=random.randint(0,len(train_data)-1)
        while(trainnum in prevtrainbuffer):
            trainnum=random.randint(0,len(train_data)-1)
        
        prevtrainbuffer[0]=prevtrainbuffer[1]
        prevtrainbuffer[1]=trainnum
        sch.append(train_data[trainnum][0])
        time_str = (start_time + interval).strftime("%H:%M:%S")
        start_time=start_time+interval
        while True:
            ind=random.randint(0, len(st_sample)-1)
            if used[ind]==0:
                used[ind]=1
                sch.append(st_sample[ind][0][0])
                arrt=day+' '+time_str
                sch.append(arrt)
                sch.append(st_sample[ind][1][0])
                trav=random.randint(2, 12)
                dept=day+' '+(start_time + trav * interval).strftime("%H:%M:%S")
                sch.append(dept)
                schedule_data.append(sch)
                break
    return schedule_data

def scheduler_call():
    connector=DatabaseConnector()
    connector.connect("trainmanagement")
    clock= -1
    update_time=24 * 60 #minutes

    while(True):
        print(f"scheduler {clock}")
        clock+=1

        query=f"Select * from schedules;"
        connector.execute_query(query)
        rows=connector.cursor.fetchall()
        for row in rows:

            if row["Shdeptime"].timestamp()-datetime.now().timestamp()<0:
               query=f"UPDATE trains set Trstatus='Departed' where Trid={row['ShTrid']} and Trstatus!='Departed';"
               connector.execute_query(query,commit=True)

            if row["Sharvtime"].timestamp()-datetime.now().timestamp()<0:
               query=f"UPDATE trains set Trstatus='Stationed' where Trid={row['ShTrid']} and Trstatus!='Stationed';"
               connector.execute_query(query,commit=True)

        if(clock/6%(update_time)==0):
            new_schedules=create_schedule()
            connector.clear_table("schedules")
            for schedule in new_schedules:
                connector.insert_entry("schedules",schedule)
            print("Schedules Updated")

        time.sleep(10)

if __name__=="__main__":
    #scheduler_call()
    pass
    


