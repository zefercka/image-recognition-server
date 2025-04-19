import cv2
import numpy as np
import math


def get_center_coordinates(mask):
    kernel_erode = np.ones((4,4), np.uint8)
    eroded_mask = cv2.erode(mask, kernel_erode, iterations=1)
    kernel_dilate = np.ones((6,6),np.uint8)
    dilated_mask = cv2.dilate(eroded_mask, kernel_dilate, iterations=1)
    # Find the different contours
    contours, hierarchy = cv2.findContours(dilated_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Sort by area (keep only the biggest one)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]
    if len(contours) > 0:
        M = cv2.moments(contours[0])
        # Centroid
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        return np.array([cx, cy])
    else:
        return np.array([cx, cy])


def angle_between_segments(a1, a2, b1, b2):
    # Векторы отрезков
    ax = a2[0] - a1[0]
    ay = a2[1] - a1[1]
    bx = b2[0] - b1[0]
    by = b2[1] - b1[1]
    
    # Скалярное произведение и длины векторов
    dot = ax * bx + ay * by
    len_a = math.hypot(ax, ay)
    len_b = math.hypot(bx, by)
    
    # Косинус угла и его арккосинус (в градусах)
    cos = dot / (len_a * len_b)
    return math.degrees(math.acos(max(-1, min(1, cos))))
                        

def read_video(path: str):
    cap = cv2.VideoCapture(path)
    
    window_name = "frame"
    
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while cap.isOpened():

        ret, frame = cap.read()
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        lower_blue = np.array([92, 150, 0]) 
        upper_blue = np.array([150, 255, 255]) 

        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue) 
        mask_blue_center_coords = get_center_coordinates(mask_blue)
        
        lower_pink = np.array([135, 100, 0])
        upper_pink = np.array([180, 255, 255])
        
        mask_pink = cv2.inRange(hsv, lower_pink, upper_pink) 
        mask_pink_center_coords = get_center_coordinates(mask_pink)
        
        lower_green = np.array([30, 100, 0]) 
        upper_green = np.array([90, 255, 255])

        mask_green = cv2.inRange(hsv, lower_green, upper_green) 
        mask_green_center_coords = get_center_coordinates(mask_green)
        
        # The black region in the mask has the value of 0, 
        # so when multiplied with original image removes all non-blue regions 
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
        
        a = angle_between_segments(
            (mask_blue_center_coords[0], mask_blue_center_coords[1]),
            (line_center_coords[0], line_center_coords[1]),
            (mask_green_center_coords[0], mask_green_center_coords[1]),
            (line_center_coords[0], line_center_coords[1]),
        )
        
        cv2.putText(result, str(int(a)), (line_center_coords[0], line_center_coords[1] + 50), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 5)
        
        cv2.imshow(window_name, result)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()  
    cv2.destroyAllWindows()


read_video(r"../video/example.mp4")