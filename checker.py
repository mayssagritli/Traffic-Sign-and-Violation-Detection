import mysql.connector
import cv2
from datetime import datetime

class CarControl:
    def __init__(self,fps,width,height, frames_to_check=5, threshold=0.01, db_config=None,rec_size=100):
        self.frames_to_check = frames_to_check
        self.fps = fps
        self.width = width
        self.height = height
        self.threshold = threshold
        self.history = []
        for i in range(frames_to_check):
            self.history.append(["none", 0, 0])
            
        #last 10 secs Window
        self.record = []
        self.max_rec_size = rec_size
        self.id = 0

        
        self.in_red = False
        self.passed = True
        
        self.in_stop = False
        self.curr_speed_lim = 50

        # Database connection
        self.db_config = db_config
        self.db_connection = None
        self.db_cursor = None
        if self.db_config:
            self.connect_to_db()

    def update_rec(self,frame):
        self.record.append(frame)
        if(len(self.record) > self.max_rec_size):
            self.record.pop(0)

    def connect_to_db(self):
        try:
            self.db_connection = mysql.connector.connect(**self.db_config)
            self.db_cursor = self.db_connection.cursor()
        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL database: {err}")

    def update(self, sign_class_name, ratio,conf):
        self.history.append([sign_class_name, ratio, conf])
        if len(self.history) > self.frames_to_check:
            self.history.pop(0)
        
    def check_red(self):
        for i in self.history:
            if i[0] == "Red Light" and i[1] >= self.threshold:
                self.in_red = True
            
    def check_green(self):
        for i in self.history:
            if i[0] == "Green Light" and i[1] >= self.threshold:
                self.in_red = False
    
    def check_stop(self):
        for i in self.history:
            if i[0] == "Stop" and i[1] >= self.threshold:
                self.in_stop = True
            
    def update_speed(self):
        speed_limit_class_names = ["Speed Limit 10", "Speed Limit 20", "Speed Limit 30", "Speed Limit 40",
                           "Speed Limit 50", "Speed Limit 60", "Speed Limit 70", "Speed Limit 80",
                           "Speed Limit 90", "Speed Limit 100", "Speed Limit 110", "Speed Limit 120"]
        for i in self.history:
            if i[0] in speed_limit_class_names and i[1] >= self.threshold:
                self.curr_speed_lim = int(i[0].split()[-1])
                
    def record_write(self,path):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(path, fourcc, self.fps, (self.width, self.height))
        for f in self.record:
            out.write(f)
    
        out.release()
        
    def check_violation(self, speed):
        violation_type = None
        confidence_score = 0

        if self.in_stop and speed > 5:
            violation_type = "STOP VIOLATION"
            
            confidence_score = max([i[2] for i in self.history if i[0] == "Stop"])

        if speed > self.curr_speed_lim:
            violation_type = "SPEED LIMIT EXCEEDED"
            confidence_score = 1.0 

        a = 0
        for i in self.history:
            if i[1] < self.threshold:
                a += 1
        if a == self.frames_to_check:
            self.in_stop = False
            if self.in_red:
                violation_type = "RED LIGHT VIOLATION"
                confidence_score = max([i[2] for i in self.history if i[0] == "Red Light"])
            self.in_red = False

        if violation_type:
            if violation_type == "RED LIGHT VIOLATION":
                type = 'RD'
            elif violation_type == "SPEED LIMIT EXCEEDED":
                type = "SP"
            else:
                type = 'ST'
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT MAX(DETECTION_ID) FROM Results")
            newID = cursor.fetchone()[0]
            if newID is None:
                newID = 1
            else:
                newID = newID + 1
            p = f'\\violations\\VIOLATION#{type}{newID}.avi'
            self.record_write(p)
            cursor.close()
            self.save_violation(newID, violation_type, speed, p, confidence_score)

    def save_violation(self, detection_id, violation_type, speed, video_path, confidence_score):
        if not self.db_connection:
            print("Database connection not established. Cannot save violation.")
            return

        timestamp = datetime.now()
        
        insert_query = """
        INSERT INTO Results 
        (DetectionID, Timestamp, ViolationType, Speed, Speed_Limit, Image_Path, Video_Path, Confidence_Score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        violation_data = (
            detection_id,
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
