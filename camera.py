from threading import Thread
import cv2
import time
import datetime
from PyMata.pymata import PyMata
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
subject = "WEBCAM VIDEO ALERT"
body = "Here is the video that was just taken with your camera"
sender_email = "testwaltertr@gmail.com"
receiver_email = "whftruitt@gmail.com"
password = "***************"
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message["Bcc"] = receiver_email
message.attach(MIMEText(body, "plain"))

def showCam(out, frame):
    out.write(frame)
def alarm():
    board.digital_write(7, 1)
    board.play_tone(4, board.TONE_TONE, 2000, 0)
    time.sleep(0.05)
    board.digital_write(7, 0)
    
   
def alarm2():
    
    board.digital_write(6, 1)
    time.sleep(0.05)
    board.digital_write(6, 0)
    


board = PyMata('COM4')
board.set_pin_mode(7, board.OUTPUT, board.DIGITAL)
board.set_pin_mode(6, board.OUTPUT, board.DIGITAL)

cap = cv2.VideoCapture(0)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
body_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_fullbody.xml')

detection = False
detectionStoppedTime = None
timer_started = False
SECONDS_TO_RECORD_AFTER_DETECTION = 5


frame_size = int(cap.get(3)), int(cap.get(4))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

count = 0
while True:
    _, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    bodies = body_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) + len(bodies) > 0:
        if detection:
            timer_started = False
        else:
            detection = True
            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            out = cv2.VideoWriter(f'{current_time}.mp4', fourcc, 20, frame_size)
    elif detection:
        if timer_started:
            if time.time() - detectionStoppedTime >= SECONDS_TO_RECORD_AFTER_DETECTION:
                detection = False
                timer_started = False
                out.release()
                filename = f'{current_time}.mp4'
                attachment = open(filename, 'rb')
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-Disposition', f'attachment; filename= {filename}') 
                message.attach(p)
                text = message.as_string()
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
                    
                    s.login(sender_email, password)
                    s.sendmail(sender_email, receiver_email, text)
                    

        else:       
            timer_started = True
            detectionStoppedTime = time.time()

    if detection:

        
        showCam(out, frame)
        

        if count % 2 == 0:
            alarm()
        else:
            alarm2()
        count += 1
        



    for (x, y, width, height) in faces:
        cv2.rectangle(frame, (x, y), (x + width, y+height), (255, 0, 0), 3)
    for (x, y, width, height) in bodies:
        cv2.rectangle(frame, (x, y), (x + width, y+height), (0, 0, 255), 3)

    cv2.imshow('CAM1', frame)

    if cv2.waitKey(1) == ord('p'):
        password = input('ENTER PASSKEY: ')
        if password == "walt17":
            print('~~~~~~~ACCESS GRANTED~~~~~~~')
            board.play_tone(4, board.TONE_NO_TONE, 1000, 0)
            break
        else:
            print('~~~~~~~INCORRECT~~~~~~~')
            pass
out.release()
cap.release()
cv2.destroyAllWindows()
