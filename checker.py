import mysql.connector
import cv2
import os
from datetime import datetime
'''
class hedhi tekhou 5 frames t9ayadhom each time , l threshold howa 9adeh lezm l ratio mtaa l sign fl whole image yfout 
bch tthseb lkarhba taht lblaka '''
class CarControl:
    def __init__(self,fps,width,height, frames_to_check=5, threshold=0.003,rec_size=100):
        self.frames_to_check = frames_to_check
        self.fps = fps
        self.width = width
        self.height = height
        self.threshold = threshold
#history fih l frames l 5 eli n9aydou fehom esm lclasse taa sign si famech none , l ratio eli lezm akber mel threshold w l confidence  
        self.history = []
        for i in range(frames_to_check):
            self.history.append(["none", 0, 0])
        #last 10 secs Window
        self.record = []
        self.max_rec_size = rec_size
        self.id = 0

        self.recent_red_conf=0
        self.in_red = False
        self.passed = True
        
        self.in_stop = False
        self.curr_speed_lim = 50
        #details l db eli bch n9aydou feha l violations 
        #Database connection
        self.db_config= {
                            'host': 'sql7.freemysqlhosting.net',
                            'user': 'sql7720134',
                            'database': 'sql7720134',
                            'password': '3b6uDHWTa3',
                            'port' : '3306'
                        }
        self.db_connection = None
        self.db_cursor = None
        self.connect_to_db()
      
        if self.db_config:
            self.connect_to_db()
#log nhebou nchoufou y9ayed wale (just testing)            
    def log_viol(self, violID, type):
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{violID}_{type}_{time}\n"
        log_file = open("log.txt", "a")
        log_file.write(log_entry)
        log_file.close()       
        
    def update_rec(self,frame):
        self.record.append(frame)
        if(len(self.record) > self.max_rec_size):
            self.record.pop(0)
#db error and exception handling 
    def connect_to_db(self):
        try:
            self.db_connection = mysql.connector.connect(**self.db_config)
            self.db_cursor = self.db_connection.cursor()
            print("Successfully connected to the database")
        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL database: {err}")
#lhne naabiw l list taa l history chykoun feha list mtaa 5 frames kol frame aandou [calssname,ratio,confidence]
    def update(self, sign_class_name, ratio,conf):
        self.history.append([sign_class_name, ratio, conf])
        if len(self.history) > self.frames_to_check:
            self.history.pop(0)
#lhne check ken l sign red wale        
    def check_red(self):
        for i in self.history:
            if i[0] == "Red Light" and i[1] >= self.threshold:
                self.recent_red_conf =i[2]
                self.in_red = True
 #check ken l sign green detected               
    def check_green(self):
        for i in self.history:
            if i[0] == "Green Light" and i[1] >= self.threshold:
                self.in_red = False
#check ken l sign Stop        
    def check_stop(self):
        for i in self.history:
            if i[0] == "Stop" and i[1] >= self.threshold:
                self.in_stop = True
 #check for which speed limit detected              
    def update_speed(self):
        speed_limit_class_names = ["Speed Limit 10", "Speed Limit 20", "Speed Limit 30", "Speed Limit 40",
                           "Speed Limit 50", "Speed Limit 60", "Speed Limit 70", "Speed Limit 80",
                           "Speed Limit 90", "Speed Limit 100", "Speed Limit 110", "Speed Limit 120"]
        for i in self.history:
            if i[0] in speed_limit_class_names and i[1] >= self.threshold:
                self.curr_speed_lim = int(i[0].split()[-1])
   
        
    def record_write(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(path, fourcc, self.fps, (self.width, self.height))
        if not out.isOpened():
            print(f"Error: Could not open video writer for {path}")
            return
        try:
            for f in self.record:
                if f.shape != (self.height, self.width, 3):
                    f = cv2.resize(f, (self.width, self.height))
                if len(f.shape) == 2:  
                    f = cv2.cvtColor(f, cv2.COLOR_GRAY2BGR)
                out.write(f)
            print(f"Video successfully written to {path}")
        except Exception as e:
            print(f"Error while writing video: {str(e)}")
        finally:
            out.release()

        if os.path.exists(path) and os.path.getsize(path) > 0:
            print(f"Video file created successfully: {path}")
        else:
            print(f"Error: Video file was not created or is empty: {path}")
    
        out.release()
#lhne lkhedma taa violations        
    def check_violation(self, speed):
        violation_type = None
        confidence_score = 0

        if self.in_stop and speed > 5:
            violation_type = "STOP VIOLATION"
            confidence_score = max([i[2] for i in self.history if i[0] == "Stop"])

        if speed > self.curr_speed_lim:
            violation_type = "SPEED LIMIT EXCEEDED"
            confidence_score = 0.8

        a = 0
        b = 0
        for i in self.history:
            if  i[1] < self.threshold or i[0] != "Stop":
                b += 1
            if  i[1] < self.threshold or i[0] != "Red Light":
                a += 1
        if b == self.frames_to_check:
            self.in_stop = False
        if a == self.frames_to_check:
            if self.in_red:
                confidence_score = self.recent_red_conf
                violation_type = "RED LIGHT VIOLATION"
            self.in_red = False

        if violation_type:
            print(violation_type)
            if violation_type == "RED LIGHT VIOLATION":
                type = 'RD'
            elif violation_type == "SPEED LIMIT EXCEEDED":
                type = "SP"
            else:
                type = 'ST'
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT MAX(DetectionID) FROM Results")
            newID = cursor.fetchone()[0]
            if newID is None:
                newID = 1
            else:
                newID = newID + 1
            script_dir = os.path.dirname(os.path.abspath(__file__))
            violations_dir = os.path.join(script_dir, "violations")
            os.makedirs(violations_dir, exist_ok=True)
            p = os.path.join(violations_dir, f"VIOLATION#{type}{newID}.avi")
            print(f"Video will be saved to: {p}")
            self.record_write(p)
            cursor.close()
            self.save_violation(newID, violation_type, speed, p, confidence_score)
            self.log_viol(newID, violation_type)
  #lhne nsavi l results fl db           
    def save_violation(self, DetectionID, violation_type, speed, video_path, confidence_score):
        if not self.db_connection:
            print("Database connection not established. Cannot save violation.")
            return

        timestamp = datetime.now()
        
        insert_query = """
        INSERT INTO Results 
        (DetectionID, Timestamp, ViolationType, Speed, Speed_Limit, Video_Path, Confidence_Score)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        violation_data = (
            DetectionID,
            timestamp,
            violation_type,
            speed,
            self.curr_speed_lim,
            video_path,
            confidence_score
        )

        try:
            self.db_cursor.execute(insert_query, violation_data)
            self.db_connection.commit()
            print(f"Violation saved: {violation_type}")
        except mysql.connector.Error as err:
            print(f"Error saving violation to database: {err}")

    def __del__(self):
        if self.db_connection:
            self.db_cursor.close()
            self.db_connection.close()