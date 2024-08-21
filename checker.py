class CarControl:
    def __init__(self, frames_to_check=10,threshold=0.01):
        self.frames_to_check = frames_to_check
        self.threshold = threshold
        
        self.history = []
        for i in range(frames_to_check):
            self.history.append(["none",0])
        
        self.in_red = False
    
        self.passed = True
        
        self.in_stop = False
        
        self.curr_speed_lim = 50
        
    def update(self, sign_class_name, ratio):
        self.history.append([sign_class_name,ratio])
        if len(self.history) > self.frames_to_check:
            self.sign_history.pop(0)
            
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
        for i in speed_limit_class_names and i[1] >= self.threshold:
            self.curr_speed_lim = int(i[0].split()[-1])        
    
    def check_violation(self,speed):
        if self.in_stop and speed > 5:
            print("STOP VIOLATION")
        if speed > self.curr_speed_lim:
            print("SPEED LIMIT EXCEEDED")
        a = 0
        for i in self.history:
            if i[1] < self.threshold:
                a += 1
        if a == self.frames_to_check:
            self.in_stop = False
            if self.in_red:
                print("RED LIGHT VIOLATION")
            self.in_red = False