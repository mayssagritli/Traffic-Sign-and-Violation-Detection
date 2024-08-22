import mysql.connector
from datetime import datetime

class CarControl:
    def __init__(self, frames_to_check=10, threshold=0.01, db_config=None):
        self.frames_to_check = frames_to_check
        self.threshold = threshold
        
        self.history = []
        for i in range(frames_to_check):
            self.history.append(["none", 0, 0])
        
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
        
    def check_violation(self, speed, detection_id, image_path, video_path):
        violation_type = None
        confidence_score = 0

        if self.in_stop and speed > 5:
            violation_type = "STOP VIOLATION"
            confidence_score = max([i[2] for i in self.history if i[0] == "Stop"])

        if speed > self.curr_speed_lim:
            violation_type = "SPEED LIMIT EXCEEDED"
            confidence_score = 1.0  # Assuming 100% confidence for speed violations

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
            self.save_violation(detection_id, violation_type, speed, image_path, video_path, confidence_score)

    def save_violation(self, detection_id, violation_type, speed, image_path, video_path, confidence_score):
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
            image_path,
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

if __name__ == "__main__":
    db_config = mysql.connector.connect(
                host='sql7.freemysqlhosting.net',
                database='sql7720134',
                user='sql7720134',
                password='3b6uDHWTa3'
                )
    car_control = CarControl(db_config=db_config)
