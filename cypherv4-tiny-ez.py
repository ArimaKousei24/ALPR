import cv2
import easyocr
import time
import pymysql


net = cv2.dnn.readNet("yolov4-tiny-custom_1000.weights", "yolov4-tiny-custom.cfg")
model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(320, 320), scale =1/255)

classes = []
with open("classes.txt", "r") as file_object:
    for class_name in file_object.readlines():
        class_name = class_name.strip()
        classes.append(class_name)

print("Object list")
print(classes)

cap = cv2.VideoCapture(0)
reader = easyocr.Reader(['en'], gpu=False)

def ocr(img):
    
    
    #Easyocr Extraction
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    result = reader.readtext(gray)
    text = ""
    
   
    for plate in result:
        text += plate[1] + ""
        text = text.replace(" ", "").upper()
    text = text[:7]
    cv2.putText(frame, text, (50,70), cv2.FONT_HERSHEY_PLAIN,2,(0,0,0),2)
    print(text)


    con=pymysql.connect(host="localhost", user="root", password="", database="datetry")
    cursor = con.cursor()
        
        # Check if the characters is already in the table
    query = "SELECT * FROM defense WHERE chars = %s ORDER BY curr_date_time_in DESC"
    cursor.execute(query, (text,))
    result = cursor.fetchone()
    


    if result:
            # If characters have a time_out value, insert a new row with same characters and new time_in
        if result[3]:
            sql = "INSERT INTO defense (chars, curr_date_time_in) VALUES (%s, NOW())"
            val = (text,)
            cursor.execute(sql, val)
            con.commit()
            #time.sleep(15)
            print("chars and time-in saved again in the database")
            time.sleep(8)
                
            # If characters do not have a time_out value, update existing row with current time as time_out
        else:
            sql = "UPDATE defense SET curr_date_time_out = NOW() WHERE id = %s"
            val = (result[0],)
            cursor.execute(sql, val)
            con.commit()
            #time.sleep(15)
            print("chars and time-out updated in the database")
            time.sleep(8)
                
    else:
                # If characters are not yet in table, insert new row with characters and current time as time_in
        sql = "INSERT INTO defense (chars, curr_date_time_in) VALUES (%s, NOW())"
        val = (text,)
        cursor.execute(sql, val)
        con.commit()
        #time.sleep(15)
        print("characters and time-in saved in the database")
        time.sleep(8)
            

    # Close the cursor and connection
        cursor.close()
        con.close()


    

while True:
    ret, frame = cap.read()
    (class_ids, scores, bboxes)= model.detect(frame)
    for class_id, score, bbox in zip(class_ids, scores, bboxes):
        (x,y,w,h) = bbox
        class_name = classes[class_id]
        object_img = frame[int(y):int(y+h), int(x):int(x+w)]
        ocr(object_img)
        



    
        cv2.putText(frame, class_name, (x, y-5), cv2.FONT_HERSHEY_PLAIN, 1, (200,0,50),2)
        cv2.rectangle(frame, (x,y), (x+w, y+h), (200,0,50), 3)
        cv2.putText(frame, str(score), (x+w, y-5), cv2.FONT_HERSHEY_PLAIN, 1, (200,0,50),2) 
        


    # print("class ids", class_ids)
    # print("scores", scores)
    # print("bboxes", bboxes)
   
    cv2.imshow("Cypher View", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break



cap.release()
cv2.destroyAllWindows()



    


