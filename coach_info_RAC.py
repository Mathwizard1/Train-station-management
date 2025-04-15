import random
from application.server.databaseConnector import DatabaseConnector

coach_data = (
        ("SLR", 80),  # Seating cum Luggage Rake
        ("GS", 90),   # General Second Class
        ("A1", 24),   # AC First Class
        ("A2", 48),   # AC Two Tier
        ("A3", 64),   # AC Three Tier
        ("B1", 72),   # AC Three Tier (older type)
        ("S1", 72),   # Sleeper Class
        ("PC", 80),   # Pantry Car
        ("HCPV", 26), # High Capacity Parcel Van
    )
train_data = (
        (123, "Rajdhani Express", "Departed"),
        (456, "Shatabdi Exp", "Stationed"),
        (789, "Duronto Express", "Incoming"),
        (234, "Kerala Express", "Departed"),
        (567, "Tamil Nadu Exp", "Stationed"),
        (890, "Karnataka Exp", "Incoming"),
        (345, "Andhra Pradesh", "Departed"),
        (678, "Gujarat Mail", "Stationed"),
        (901, "Mumbai Rajdhani", "Incoming"),
        (457, "Howrah Mail", "Departed"),
        (780, "Coromandel Exp", "Stationed"),
        (129, "Ganga Sagar Exp", "Incoming"),
        (561, "Godavari Exp", "Departed"),
        (893, "Telangana Exp", "Stationed"),
        (235, "Himachal Exp", "Incoming"),
        (679, "Deccan Queen", "Departed"),
        (902, "Konark Express", "Stationed"),
        (346, "Udyan Express", "Incoming"),
        (781, "Falaknuma Exp", "Departed"),
        (124, "Brindavan Exp", "Stationed")
    )

def create_coach_info():
    coach_info_data=[]
    for i in range(len(train_data)):
        num=random.randint(4,9)
        coaches=random.sample(coach_data, num)
        for j in range(num):
            cin=[]
            cin.append(train_data[i][0])
            cin.append(coaches[j][0])
            cin.append(0)
            cin.append(coaches[j][1])
            cin.append(int(coaches[j][1]*0.1))
            cin.append(int(coaches[j][1]*0.1))
            coach_info_data.append(cin)
    
    return coach_info_data

def Create_Coach_RAC_Info():
    connector=DatabaseConnector()
    connector.connect("trainmanagement")

    new_infos=create_coach_info()
    connector.clear_table("rac")
    connector.clear_table("coach_infos")
    
    for info in new_infos:
        connector.insert_entry("coach_infos",info)
    
    for info in new_infos:
        totalracseats=info[5]
        totalseats=info[3]

        racseats=random.sample(range(1,totalseats+1),totalracseats)
        
        for seat in racseats:
            connector.insert_entry("rac",[info[0],info[1],seat,0])

    print("Coach Infos Updated")
