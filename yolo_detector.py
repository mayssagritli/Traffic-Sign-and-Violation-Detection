from ultralytics import YOLO
import cv2

class YOLODetector:
    def __init__(self, model_path='best.pt'):
        self.model = YOLO(model_path)
        self.class_names = self.model.names

    def detect(self, frame, conf=0.5):
        results = self.model(frame, conf=conf)
        detections = []

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.class_names[cls]
                detections.append({
                    'class_name': class_name,
                    'bounding_box': (x1, y1, x2, y2),
                    'confidence': conf
                })

        return detections

    def draw_detections(self, frame, detections):
        for det in detections:
            x1, y1, x2, y2 = det['bounding_box']
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{det['class_name']} {det['confidence']:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        return frame