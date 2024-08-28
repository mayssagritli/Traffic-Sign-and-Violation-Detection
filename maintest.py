# main.py

import cv2
from yolo_detector import YOLODetector
from checker import CarControl
#hedhi nchoufou beha l size bch n9arnou bl sign ratio w naarfou l car taht l sign wale
def sign_size(image_width, image_height,x1,x2,y1,y2):
        max_sign_area = 0
        sign_center = None
        total_image_area = image_width * image_height

        sign_area = (x2 - x1) * (y2 - y1)
        if sign_area > max_sign_area:
            max_sign_area = sign_area
            sign_center = ((x1 + x2) / 2, (y1 + y2)/2)

        sign_area_ratio = max_sign_area / total_image_area
        return sign_area_ratio
    #lhne yekhdem weldi modeli l7abib eli jeb 96% accuracy
def run(video_path):
    detector = YOLODetector('best.pt')   
    cap = cv2.VideoCapture(video_path)
      # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    control = CarControl(fps,width,height)
    # hedhi temporarly trecordi video men awl matethal l cam /yabda l vid just hachti beha baad tetbadl ywali yrecordi ken ki tsir violation
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, fps, (width, height))
    car_speed = 0  #Car Speed Placeholder (manaarach kifeh nekhdhou speed ml hardware taa lkarhba)
#lhne nekhdhou l frames w nhezouhom lel carcontrol nental9ou f khedmet l checker    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
     
        image_height, image_width = frame.shape[:2]
        detections = detector.detect(frame)
        speed_limit_class_names = ["Speed Limit 10", "Speed Limit 20", "Speed Limit 30", "Speed Limit 40",
                               "Speed Limit 50", "Speed Limit 60", "Speed Limit 70", "Speed Limit 80",
                               "Speed Limit 90", "Speed Limit 100", "Speed Limit 110", "Speed Limit 120"]
        for_check=False
        
        for i, det in enumerate(detections, 1):
            class_name = det['class_name']
            x1, y1, x2, y2 = det['bounding_box']
            confidence = det['confidence']
            print(f"  Detection {i}:")
            print(f"  Class Name: {class_name}")
            print(f"  Bounding Box: (x1={x1}, y1={y1}, x2={x2}, y2={y2})")
            print(f"  Confidence: {confidence:.2f}")
            print()
            print(control.history)       
            if confidence >= 0.5:
                for_check=True
                control.update(class_name,sign_size(image_width,image_height,x1,x2,y1,y2),confidence)
                print(control.history)
                if class_name in speed_limit_class_names:
                    control.update_speed()
                if class_name == "Red Light":
                    control.check_red()
                if class_name == "Green Light":
                    control.check_green()
                if class_name == "Stop":
                    control.check_stop()
        if not for_check:
            control.update("none",0,0)
        
        control.check_violation(car_speed)
        
        frame = detector.draw_detections(frame, detections)
        control.update_rec(frame)
        out.write(frame)
        
        cv2.imshow("Traffic Sign Detection", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    video_path = "testvid.mp4"
    run(video_path)