import cv2
import numpy as np
import math


def _get_center_coordinates(mask):
    kernel_erode = np.ones((4,4), np.uint8)
    eroded_mask = cv2.erode(mask, kernel_erode, iterations=1)
    kernel_dilate = np.ones((6,6),np.uint8)
    dilated_mask = cv2.dilate(eroded_mask, kernel_dilate, iterations=1)

    contours, _ = cv2.findContours(dilated_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]
    if len(contours) > 0:
        M = cv2.moments(contours[0])

        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        return np.array([cx, cy])
    else:
        return np.array([0, 0])


def _angle_between_segments(a1, a2, b1, b2):
    # Векторы отрезков
    ax = a2[0] - a1[0]
    ay = a2[1] - a1[1]
    bx = b2[0] - b1[0]
    by = b2[1] - b1[1]
    
    # Скалярное произведение и длины векторов
    dot = ax * bx + ay * by
    len_a = math.hypot(ax, ay)
    len_b = math.hypot(bx, by)
    
    # Косинус угла
    cos = dot / (len_a * len_b)
    
    # Вычисляем угол через арккосинус (в радианах)
    angle = math.acos(max(-1, min(1, cos)))  # Ограничение значения косинуса в диапазоне [-1, 1]
    
    # Векторное произведение для определения ориентации
    cross = ax * by - ay * bx
    
    # Если векторное произведение отрицательное, угол считается отрицательным
    if cross > 0:
        angle = -angle
    
    # Переводим угол в градусы
    return math.degrees(angle)
                        

def _read_video(path: str) -> float:
    cap = cv2.VideoCapture(2)
    
    window_name = "frame"
    
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    _, frame = cap.read()
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    try:
        lower_blue = np.array([90, 150, 0]) 
        upper_blue = np.array([150, 255, 255]) 

        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue) 
        mask_blue_center_coords = _get_center_coordinates(mask_blue)
        
        lower_pink = np.array([130, 150, 0])
        upper_pink = np.array([180, 255, 255])
        
        mask_pink = cv2.inRange(hsv, lower_pink, upper_pink) 
        mask_pink_center_coords = _get_center_coordinates(mask_pink)
        
        lower_green = np.array([30, 70, 0]) 
        upper_green = np.array([100, 255, 255])

        mask_green = cv2.inRange(hsv, lower_green, upper_green) 
        mask_green_center_coords = _get_center_coordinates(mask_green)

        result_blue = cv2.bitwise_and(frame, frame, mask = mask_blue)
        result_pink = cv2.bitwise_and(frame, frame, mask = mask_pink)
        result_green = cv2.bitwise_and(frame, frame, mask = mask_green)

        result = cv2.bitwise_or(result_blue, result_green)
        result = cv2.bitwise_or(result_pink, result)

        result = cv2.circle(result, mask_blue_center_coords, radius=20, color=(0, 0, 255), thickness=-1)
        result = cv2.circle(result, mask_pink_center_coords, radius=20, color=(0, 0, 255), thickness=-1)
        result = cv2.circle(result, mask_green_center_coords, radius=20, color=(0, 0, 255), thickness=-1)
        
        result = cv2.line(result, mask_blue_center_coords, mask_pink_center_coords, (255, 255, 255), 10)
        
        line_center_coords = (
            (mask_blue_center_coords[0] + mask_pink_center_coords[0]) // 2,
            (mask_blue_center_coords[1] + mask_pink_center_coords[1]) // 2,
        )
        
        result = cv2.circle(result, line_center_coords, radius=20, color=(0, 0, 255), thickness=-1)
        result = cv2.line(result, line_center_coords, mask_green_center_coords, (255, 255, 255), 10)
        
        angle = _angle_between_segments(
            (mask_blue_center_coords[0], mask_blue_center_coords[1]),
            (line_center_coords[0], line_center_coords[1]),
            (mask_green_center_coords[0], mask_green_center_coords[1]),
            (line_center_coords[0], line_center_coords[1]),
        )
        
        cv2.putText(result, str(int(angle)), (line_center_coords[0], line_center_coords[1] + 50), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 5)
        
        cv2.imshow(window_name, result)

        # while cap.isOpened():
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break
        
        cap.release()  
        cv2.destroyAllWindows()
        
        if mask_green_center_coords[0] == 0 and mask_green_center_coords[1] == 0:            
            return -360
        
        
    except Exception as err:
        print(err)
        angle = 0
    
    return angle
    

def get_angle():
    # return -10
    return _read_video("1")
    
    


# _read_video(r"../video/example.mp4")
