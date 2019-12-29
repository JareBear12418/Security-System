#!/usr/bin/env python3
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import *
import sys, os, shutil, json, multiprocessing, cv2, atexit, threading, re, time
from functools import partial
from os import listdir
from os.path import isfile, join

# sudo python3 -m pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org [NAME]

# CAMERA SCRIPT
import camera
settings_file = os.path.dirname(os.path.realpath(__file__)) + '/settings.json'
settings_json = []

cascade_files_dir = os.path.dirname(os.path.realpath(__file__)) + '/Data Models'
cascade_files = [f for f in listdir(cascade_files_dir) if isfile(join(cascade_files_dir, f))]
isActive = False

saved_color = []
send_email = []
cap_screen = []
record_video = []
smiley_face = []
dark_mode = []
face_detect = []

email_address = []

email_delay = []
picture_delay = []
selected_data_index = []
button_css = ''
frame = ''

cycles_file = os.path.dirname(os.path.realpath(__file__)) + '/cycles.json'
cycles_json = []

OnToList = []
OnFromList = []
OffToList = []
OffFromList = []
alwaysOn = []

running = True

framesPerSecond = 0
class MainMenu(QMainWindow):
    def __init__(self, parent = None):
        super(MainMenu, self).__init__(parent)
        self.menu()
        mainlay = QWidget(self)
        mainlay.setContentsMargins(5, 5, 5, 5)
        lay = QVBoxLayout()
        top = QHBoxLayout()
        bottom = QHBoxLayout()
        
        self.setWindowTitle('J-Detection - Main Menu')
        self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))
        self.cameraScreen = QLabel(self)
        self.cameraScreen.setStyleSheet('border-radius: 3px; border-style: none; border: 1px solid black; background-color: rgb(10,10,10);')
        self.cameraScreen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cameraScreen.setAlignment(Qt.AlignCenter)
        top.addWidget(self.cameraScreen)
        self.grid = QGridLayout()
        self.grid.setRowStretch(0, 1)
        self.grid.addWidget(self.ComboBox(), 1, 0)
        bottom.addLayout(self.grid)
        lay.addLayout(top)
        lay.addLayout(bottom)
        mainlay.setLayout(lay)
        self.setCentralWidget(mainlay)
        
        # cap = cv2.VideoCapture(0)
        # if camera.cap is None or not cap.isOpened():
        #     QMessageBox.critical(self, 'Camera Error!', 'Can\'t find a camera, or camera is already running in an other program.', QMessageBox.Ok, QMessageBox.Ok)
        th = Thread(self)
        th.changePixmap.connect(self.setImage)
        camera.start_cam()
        th.start()
    def open_cycle_menu(self):
        self.c = CycleMenu()
        self.c.show()
    def closeEvent(self, event):
        exit_handler()
    @pyqtSlot(QImage)
    def setImage(self, image):
        self.setWindowTitle("J-Detection - Main Menu - {0:.2f} FPS".format(round(framesPerSecond,2)))
        self.cameraScreen.setPixmap(QPixmap.fromImage(image))
    def menu(self):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, selected_data_index, face_detect, email_address
        self.menubar = self.menuBar()
        self.statusbar = self.statusBar()
        viewMenu = QMenu('View', self)
        
        darkmode = QAction('Dark mode', self, checkable=True)
        darkmode.setStatusTip('enable/disable Dark mode')
        darkmode.setChecked(True if dark_mode[0] == 'True' else False)
        darkmode.triggered.connect(partial(self.checkboxClicked, darkmode, 'Dark mode'))
        viewMenu.addAction(darkmode)

        settingsMenu = QMenu('Configuration', self)
        self.email = QAction(f'Set Email - {email_address[0]}', self)
        self.email.triggered.connect(partial(self.verifyEmailAddress, ''))
        if email_address[0] == '':
            self.email.setStatusTip('Your email address is currently set too: None')
        else:
            self.email.setStatusTip(f'Your email address is currently set too: {email_address[0]}')
            
        self.emailDelay = QAction(f'Set Email send delay - {email_delay[0]}')
        self.emailDelay.triggered.connect(partial(self.verifyEmailDelay))
        if email_delay[0] == '':
            self.emailDelay.setStatusTip('Your email send delay is currently set too: None')
        else:
            self.emailDelay.setStatusTip(f'Your email send delay is currently set too: {email_delay[0]}')
            
        self.colorMenu = QAction(f'Color')
        self.colorMenu.triggered.connect(partial(self.Open_Color_Dialog))
        self.colorMenu.setStatusTip('Change the color of the bounding boxes in program.')
        
        self.cycleMenu = QAction(f'Cycle Menu')
        self.cycleMenu.triggered.connect(partial(self.open_cycle_menu))
        self.cycleMenu.setStatusTip('Custimze when the program is active.')
        
        
        
        
        recordvideo = QAction('Record Video', self, checkable=True)
        recordvideo.setChecked(True if record_video[0] == 'True' else False)
        recordvideo.triggered.connect(partial(self.checkboxClicked, recordvideo, 'Record Video'))
        recordvideo.setStatusTip('Record footage of the webcam.')
        
        captureScreen = QAction('Record Screen', self, checkable=True)
        captureScreen.setChecked(True if cap_screen[0] == 'True' else False)
        captureScreen.triggered.connect(partial(self.checkboxClicked, captureScreen, 'Capture Screen'))
        captureScreen.setStatusTip('Record footage of the screen.')
        
        sendEmails = QAction('Send Emails', self, checkable=True)
        sendEmails.setChecked(True if send_email[0] == 'True' else False)
        sendEmails.triggered.connect(partial(self.checkboxClicked, sendEmails, 'Send Emails'))
        sendEmails.setStatusTip('Send emails when Motion/Face detected.')
        
        smileyFace = QAction('Smiley Face Addon', self, checkable=True)
        smileyFace.setChecked(True if smiley_face[0] == 'True' else False)
        smileyFace.triggered.connect(partial(self.checkboxClicked, smileyFace, 'Smiley Face Addon'))
        smileyFace.setStatusTip('Make smiley face when *Face detected.')
        
        self.faceDetection = QAction('Face Detection', self, checkable=True)
        self.faceDetection.setChecked(True if face_detect[0] == 'True' else False)
        self.faceDetection.triggered.connect(partial(self.checkboxClicked, self.faceDetection, 'Face Detection'))
        self.faceDetection.setStatusTip('Enabled: Face detection. Disabled: Motion detection.')
        
        
        settingsMenu.addAction(self.email)
        settingsMenu.addAction(self.emailDelay)
        settingsMenu.addAction(self.colorMenu)
        settingsMenu.addAction(self.cycleMenu)
        # settingsMenu.addAction(recordvideo)
        # settingsMenu.addAction(captureScreen)
        settingsMenu.addAction(sendEmails)
        settingsMenu.addAction(smileyFace)
        settingsMenu.addAction(self.faceDetection)

        self.menubar.addMenu(viewMenu)
        self.menubar.addMenu(settingsMenu)
    def resizeEvent(self, event):
        super(MainMenu, self).resizeEvent(event)
        self.menubar.resize(self.width(), self.menubar.height())
    def verifyEmailAddress(self, s):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, button_css, selected_data_index, face_detect, email_address
        rx = re.compile(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$")
        email, done1 = QInputDialog.getText(self, 'Email Verification', 'Email Address:', echo=QLineEdit.Normal, text=s)
        if done1:
            if rx.match(email):
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [int(self.cascadeList.currentIndex())],
                    "face detect":[face_detect[0]],
                    "email address": [email]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
                with open(settings_file) as file:
                    saved_color.clear()
                    send_email.clear()
                    cap_screen.clear()
                    record_video.clear()
                    smiley_face.clear()
                    dark_mode.clear()
                    email_delay.clear()
                    picture_delay.clear()
                    face_detect.clear()
                    email_address.clear()
                    settings_json = json.load(file)
                    for info in settings_json:
                        for color in info['saved color']:
                            saved_color.append(color)
                        for screen in info['capture screen']:
                            cap_screen.append(screen)
                        for video in info['record video']:
                            record_video.append(video)
                        for email_b in info['send email']:
                            send_email.append(email_b)
                        for smile in info['smiley face']:
                            smiley_face.append(smile)
                        for dark in info['dark mode']:
                            dark_mode.append(dark)
                        for email_d in info['email delay']:
                            email_delay.append(email_d)
                        for picture in info['picture delay']:
                            picture_delay.append(picture)
                        for ind in info['selected data index']:
                            selected_data_index.append(ind)
                        for face in info['face detect']:
                            face_detect.append(face)
                        for email in info['email address']:
                            email_address.append(email)
                button = QMessageBox.information(self, "Success", f"The email: \"{email}\" has been successfully saved!", QMessageBox.Ok, QMessageBox.Ok)
                self.email.setText(f'Set Email - {email_address[0]}')
                self.email.setStatusTip(f'Your email address is currently set too: {email_address[0]}')
            else:
                button = QMessageBox.critical(self, "Wrong Email address.", f"\"{email}\" is an Invalid email address, please try again.", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if button == QMessageBox.Yes:
                    self.verifyEmailAddress(email)
                else:
                    return
    def ComboBox(self):
        global selected_data_index
        groupBox = QGroupBox("Recognition type")

        self.cascadeList = QComboBox()
        for i, j in enumerate(cascade_files):
            j = j.replace('haarcascade_', '')
            j = j.replace('.xml', '')
            j = j.replace('_', ' ')
            self.cascadeList.addItem(j)
        self.cascadeList.setCurrentIndex(int(selected_data_index[0]))
        self.cascadeList.setToolTip('A list of diffrent recognition types.')
        self.cascadeList.currentTextChanged.connect(self.comboBoxChanged)
        # self.cascadeList.setStyleSheet('color: white')
        vbox = QVBoxLayout()
        vbox.addWidget(self.cascadeList)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox
    def comboBoxChanged(self):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, button_css, selected_data_index, face_detect, email_address
        settings_json.pop(0)
        settings_json.append({
            "saved color": [saved_color[0], saved_color[1], saved_color[2]],
            "capture screen": [cap_screen[0]],
            "record video": [record_video[0]],
            "smiley face": [smiley_face[0]],
            "dark mode": [dark_mode[0]],
            "send email": [send_email[0]],
            "email delay": [email_delay[0]],
            "picture delay": [picture_delay[0]],
            "selected data index": [int(self.cascadeList.currentIndex())],
            "face detect":[face_detect[0]],
            "email address": [email_address[0]]
        })
        with open(settings_file, mode='w+', encoding='utf-8') as file:
            json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        with open(settings_file) as file:
            saved_color.clear()
            send_email.clear()
            cap_screen.clear()
            record_video.clear()
            smiley_face.clear()
            dark_mode.clear()
            email_delay.clear()
            picture_delay.clear()
            selected_data_index.clear()
            face_detect.clear()
            email_address.clear()
            settings_json = json.load(file)
            for info in settings_json:
                for color in info['saved color']:
                    saved_color.append(color)
                for screen in info['capture screen']:
                    cap_screen.append(screen)
                for video in info['record video']:
                    record_video.append(video)
                for email_b in info['send email']:
                    send_email.append(email_b)
                for smile in info['smiley face']:
                    smiley_face.append(smile)
                for dark in info['dark mode']:
                    dark_mode.append(dark)
                for email_d in info['email delay']:
                    email_delay.append(email_d)
                for picture in info['picture delay']:
                    picture_delay.append(picture)
                for ind in info['selected data index']:
                    selected_data_index.append(ind)
                for face in info['face detect']:
                    face_detect.append(face)
                for email in info['email address']:
                    email_address.append(email)
    def verifyEmailDelay(self):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, button_css, selected_data_index, face_detect, email_address
        delay, done1 = QInputDialog.getDouble(self, "Get double","Value:", 10, 0, 999999, 0)
        if done1:
            if delay >= 10:
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [delay],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [int(self.cascadeList.currentIndex())],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
                with open(settings_file) as file:
                    saved_color.clear()
                    send_email.clear()
                    cap_screen.clear()
                    record_video.clear()
                    smiley_face.clear()
                    dark_mode.clear()
                    email_delay.clear()
                    picture_delay.clear()
                    face_detect.clear()
                    email_address.clear()
                    settings_json = json.load(file)
                    for info in settings_json:
                        for color in info['saved color']:
                            saved_color.append(color)
                        for screen in info['capture screen']:
                            cap_screen.append(screen)
                        for video in info['record video']:
                            record_video.append(video)
                        for email_b in info['send email']:
                            send_email.append(email_b)
                        for smile in info['smiley face']:
                            smiley_face.append(smile)
                        for dark in info['dark mode']:
                            dark_mode.append(dark)
                        for email_d in info['email delay']:
                            email_delay.append(email_d)
                        for picture in info['picture delay']:
                            picture_delay.append(picture)
                        for ind in info['selected data index']:
                            selected_data_index.append(ind)
                        for face in info['face detect']:
                            face_detect.append(face)
                        for email in info['email address']:
                            email_address.append(email)
                # button = QMessageBox.information(self, "Success", f"The email: \"{email}\" has been successfully saved!", QMessageBox.Ok, QMessageBox.Ok)
                self.emailDelay.setText(f'Set Email send delay - {email_delay[0]}')
                self.emailDelay.setStatusTip(f'Your email send delay is currently set too: {email_delay[0]}')
    @pyqtSlot()
    def Open_Color_Dialog(self):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, button_css, selected_data_index, face_detect, email_address
        color = QColorDialog.getColor()
        if color.isValid():
            settings_json.pop(0)
            settings_json.append({
                "saved color": [color.red(), color.green(), color.blue()],
                "capture screen": [cap_screen[0]],
                "record video": [record_video[0]],
                "smiley face": [smiley_face[0]],
                "dark mode": [dark_mode[0]],
                "send email": [send_email[0]],
                "email delay": [email_delay[0]],
                "picture delay": [picture_delay[0]],
                "selected data index": [selected_data_index[0]],
                "face detect":[face_detect[0]],
                "email address": [email_address[0]]
            })
            with open(settings_file, mode='w+', encoding='utf-8') as file:
                json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            with open(settings_file) as file:
                saved_color.clear()
                send_email.clear()
                cap_screen.clear()
                record_video.clear()
                smiley_face.clear()
                dark_mode.clear()
                email_delay.clear()
                picture_delay.clear()
                selected_data_index.clear()
                face_detect.clear()
                email_address.clear()
                settings_json = json.load(file)
                for info in settings_json:
                    for color in info['saved color']:
                        saved_color.append(color)
                    for screen in info['capture screen']:
                        cap_screen.append(screen)
                    for video in info['record video']:
                        record_video.append(video)
                    for email_b in info['send email']:
                        send_email.append(email_b)
                    for smile in info['smiley face']:
                        smiley_face.append(smile)
                    for dark in info['dark mode']:
                        dark_mode.append(dark)
                    for email_d in info['email delay']:
                        email_delay.append(email_d)
                    for picture in info['picture delay']:
                        picture_delay.append(picture)
                    for ind in info['selected data index']:
                        selected_data_index.append(ind)
                    for face in info['face detect']:
                        face_detect.append(face)
                    for email in info['email address']:
                        email_address.append(email)

        button_css = 'background-color: rgb(' + str(saved_color[0]) + ', ' + str(saved_color[1]) + ', ' + str(saved_color[2]) + ');'
        # self.ColorDialog.setStyleSheet(button_css)
        # self.colorMenu.setStyleSheet(button_css)
    def checkboxClicked(self, b, name, m):
        print(b.isChecked())
        print(name)
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, selected_data_index, face_detect, email_address
        # b.setStyleSheet('background-color: hsl(126, 81%, 29%)') if b.isChecked() == True else b.setStyleSheet('background-color: rgb(106, 11, 11)')
        if name == "Capture Screen":
            if b.isChecked() == True:
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": ["True"],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": ["False"],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == "Record Video":
            if b.isChecked() == True:
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": ['True'],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": ['False'],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == "Send Emails":
            if b.isChecked() == True:
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": ['True'],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": ['False'],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == "Smiley Face Addon":
            if b.isChecked() == True:
                if face_detect[0] == 'False' or not self.cascadeList.currentIndex() == 7 and not self.cascadeList.currentIndex() == 6 and not self.cascadeList.currentIndex() == 5 and not self.cascadeList.currentIndex() == 4:
                    buttonReply = QMessageBox.question(self, "Enable 'face detection'", "You currently do not have 'face detection' enabled, if you want to get the best result, I would suggest you enable it.\nDo you want to enable 'face detection'?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    if buttonReply == QMessageBox.Yes:
                        self.cascadeList.setCurrentIndex(7)
                        self.faceDetection.setChecked(True)
                        self.checkboxClicked(self.faceDetection, 'Face Detection', '')
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": ['True'],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": ['False'],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == "Dark mode" or name == 'Light mode':
            if b.isChecked() == True:
                b.setText('Dark mode')
                app.setStyle("Fusion")
                palette = QPalette()
                gradient = QLinearGradient(0, 0, 0, 400)
                gradient.setColorAt(0.0, QColor(40, 40, 40))
                gradient.setColorAt(1.0, QColor(30, 30, 30))
                palette.setBrush(QPalette.Window, QBrush(gradient))
                palette.setColor(QPalette.WindowText, Qt.white)
                palette.setColor(QPalette.Base, QColor(25, 25, 25))
                palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
                palette.setColor(QPalette.ToolTipBase, Qt.white)
                palette.setColor(QPalette.ToolTipText, Qt.white)
                palette.setColor(QPalette.Text, Qt.white)
                palette.setColor(QPalette.Button, QColor(30, 30, 30))
                palette.setColor(QPalette.ButtonText, Qt.white)
                palette.setColor(QPalette.BrightText, Qt.red)
                palette.setColor(QPalette.Link, QColor(42, 130, 218))
                palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
                palette.setColor(QPalette.HighlightedText, Qt.black)
                app.setPalette(palette)
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": ['True'],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                b.setText('Light mode')
                app.setStyle("Fusion")
                app.setPalette(QApplication.style().standardPalette())
                palette = QPalette()
                gradient = QLinearGradient(0, 0, 0, 400)
                gradient.setColorAt(0.0, QColor(240, 240, 240))
                gradient.setColorAt(1.0, QColor(215, 215, 215))
                palette.setColor(QPalette.ButtonText, Qt.black)
                palette.setBrush(QPalette.Window, QBrush(gradient))
                app.setPalette(palette)
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": ['False'],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == "Face Detection" or name == 'Motion Detection':
            if b.isChecked() == True:
                b.setText('Face Detection')
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":['True'],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                b.setText('Motion Detection')
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":['False'],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        with open(settings_file) as file:
            saved_color.clear()
            send_email.clear()
            cap_screen.clear()
            record_video.clear()
            smiley_face.clear()
            dark_mode.clear()
            email_delay.clear()
            picture_delay.clear()
            face_detect.clear()
            email_address.clear()
            settings_json = json.load(file)
            for info in settings_json:
                for color in info['saved color']:
                    saved_color.append(color)
                for screen in info['capture screen']:
                    cap_screen.append(screen)
                for video in info['record video']:
                    record_video.append(video)
                for email_b in info['send email']:
                    send_email.append(email_b)
                for smile in info['smiley face']:
                    smiley_face.append(smile)
                for dark in info['dark mode']:
                    dark_mode.append(dark)
                for email_d in info['email delay']:
                    email_delay.append(email_d)
                for picture in info['picture delay']:
                    picture_delay.append(picture)
                for ind in info['selected data index']:
                    selected_data_index.append(ind)
                for face in info['face detect']:
                    face_detect.append(face)
                for email in info['email address']:
                    email_address.append(email)
all_textboxes = []
OnTo_textboxes = []
OnFrom_textboxes = []
OffTo_textboxes = []
OffFrom_textboxes = []
all_avail_times = ['1 AM',
                   '2 AM',
                   '3 AM',
                   '4 AM',
                   '5 AM',
                   '6 AM',
                   '7 AM',
                   '8 AM',
                   '9 AM',
                   '10 AM',
                   '11 AM',
                   '12 AM',
                   '1 PM',
                   '2 PM',
                   '3 PM',
                   '4 PM',
                   '5 PM',
                   '6 PM',
                   '7 PM',
                   '8 PM',
                   '9 PM',
                   '10 PM',
                   '11 PM',
                   '12 PM',]
class Thread(QThread):
    try:
        changePixmap = pyqtSignal(QImage)
        def run(self):
            start_time = time.time()
            x = 1 # displays the frame rate every 1 second
            counter = 0
            n = 0
            while running:
                try:
                    if running: ret, frame = camera.camRun()
                except:
                    n += 1
                    if n >= 2:
                        exit_handler()
                if ret:
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)
                counter+=1
                if (time.time() - start_time) > x :
                    global framesPerSecond
                    framesPerSecond = counter / (time.time() - start_time)
                    counter = 0
                    start_time = time.time()
    except:
        running = False
    finally:
        running = False
class CycleMenu(QMainWindow):
    def __init__(self, parent = None):
        global cycles, alwaysOn, OffFromList, OffToList, OnToList, OnFromList
        OffFromList.clear()
        OffToList.clear()
        OnFromList.clear()
        OnToList.clear()
        alwaysOn.clear()
        if os.path.exists(cycles_file):
            with open(cycles_file) as file:
                cycles_json = json.load(file)
                for info in cycles_json:
                    for c in info['cycles']:
                        cycles = int(c)
                    for on in info['always on']:
                        alwaysOn.append(on)
                    for OnTo in info['OnTo']:
                        OnToList.append(OnTo)
                    for OnFrom in info['OnFrom']:
                        OnFromList.append(OnFrom)
                    for OffTo in info['OffTo']:
                        OffToList.append(OffTo)
                    for OffFrom in info['OffFrom']:
                        OffFromList.append(OffFrom)
        elif not os.path.exists(cycles_file):
            file = open(cycles_file, "w+")
            file.write('''[{
        "cycles": [
            "1"
        ],
        "always on":[
            "False"
        ],
        "OnTo": [
            ""
        ],
        "OnFrom": [
            ""
        ],
        "OffTo": [
            ""
        ],
        "OffFrom": [
            ""
        ]}]''')
            file.close()
            with open(cycles_file) as file:
                cycles_json = json.load(file)
                for info in cycles_json:
                    for c in info['cycles']:
                        cycles = int(c)
                    for on in info['always on']:
                        alwaysOn.append(on)
                    for OnTo in info['OnTo']:
                        OnToList.append(OnTo)
                    for OnFrom in info['OnFrom']:
                        OnFromList.append(OnFrom)
                    for OffTo in info['OffTo']:
                        OffToList.append(OffTo)
                    for OffFrom in info['OffFrom']:
                        OffFromList.append(OffFrom)
        # regexp = QtCore.QRegExp('[0,1][0-9][:][0-5][0-9][a,p][m]')
        regexp = QtCore.QRegExp('[a-z-A-Z-0-9-:_]{0,7}')
        self.validator = QtGui.QRegExpValidator(regexp)
        super(CycleMenu, self).__init__(parent)
        self.setWindowTitle('J-Detection - Cycle Menu')
        self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))
        mainlay = QWidget(self)
        mainlay.setContentsMargins(5, 5, 5, 5)
        # self.clock = QLabel(self)
        self.currentTime = str(QTime.currentTime().toString(Qt.DefaultLocaleLongDate))
        self.grid = QGridLayout()
        # self.grid.setRowStretch(0, 1)
        # self.grid.addWidget(self.clock, 0, 0)
        self.grid.addWidget(self.lay(), 1, 0)
        # mainlay.addLayout(self.grid)
        mainlay.setLayout(self.grid)
    
        self.setCentralWidget(mainlay)
        # threading.Thread(target=self.updateClock).start()
    # def updateClock(self):
    #     while running:
    #         self.currentTime = str(QTime.currentTime().toString(Qt.DefaultLocaleLongDate))
    #         self.clock.setText('Current time: ' + self.currentTime)
            
    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())
    def lay(self):
        global selected_data_index, cycles, all_textboxes, OnTo_textboxes, OnFrom_textboxes, OffTo_textboxes, OffFrom_textboxes
        self.scroll = QScrollArea(self)
        self.scroll.move(7, 80)
        self.scroll.setWidgetResizable(True)
        self.content = QWidget()
        self.scroll.setWidget(self.content)
        grid = QGridLayout(self.content)
        self.setWindowTitle(f'J-Detection - Cycle Menu - {cycles} - Cycles')
        # groupBox = QGroupBox(f"{(cycles)} - Cycles")
        
        # grid = QGridLayout(self)
        self.radAlwaysOn = QCheckBox('Always on?')
        # self.radAlwaysOn.stateChanged.connect(self.delete_save_saveCycles)
        self.radAlwaysOn.clicked.connect(self.delete_save_saveCycles)
        self.radAlwaysOn.setChecked(True if alwaysOn[0] == 'True' else False)
        grid.addWidget(self.radAlwaysOn, 0, 0) 
        addCycle = QPushButton('+')
        addCycle.clicked.connect(self.btnAdd)
        btnSubmit = QPushButton()
        btnSubmit.clicked.connect(self.save_cycles)
        btnSubmit.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogApplyButton')))
        btnSubmit.clicked.connect(self.submit)
        all_textboxes.clear()
        OnTo_textboxes.clear()
        OnFrom_textboxes.clear()
        OffTo_textboxes.clear()
        OffFrom_textboxes.clear()
        self.cascadeList = QComboBox()
        for i in range(cycles):
            subCycle = QPushButton('x')
            subCycle.clicked.connect(partial(self.delete_cycle, i))
            
            btnUp = QPushButton()
            btnUp.clicked.connect(partial(self.up_arrow, i))
            btnUp.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_ArrowUp')))
            
            btnDown = QPushButton()
            btnDown.clicked.connect(partial(self.down_arrow, i))
            btnDown.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_ArrowDown')))
            
            OnFrom = QLineEdit(self.currentTime)
            OnTo = QLineEdit(self.currentTime)
            
            OffFrom = QLineEdit(self.currentTime)
            OffTo = QLineEdit(self.currentTime)
            
            # OnFrom = QComboBox()
            # OnTo = QComboBox()
            
            # OffFrom = QComboBox()
            # OffTo = QComboBox()
            # OffTo.addItems(all_avail_times)
            
            lblOnTo = QLabel(f'{i + 1}. On:')
            lblOnFrom = QLabel('to:')
            OnFrom.setValidator(self.validator)
            OnFrom.setText(str(OnFromList[i]))
            OnFrom.textChanged.connect(partial(self.save_cycles))
            OnTo.setValidator(self.validator)
            OnTo.setText(str(OnToList[i]))
            OnTo.textChanged.connect(partial(self.save_cycles))
            
            
            lblOffTo = QLabel('Off:')
            lblOffFrom = QLabel('to:')
            OffFrom.setValidator(self.validator)
            OffFrom.setText(str(OffFromList[i]))
            OffFrom.textChanged.connect(partial(self.save_cycles))
            OffTo.setValidator(self.validator)
            OffTo.setText(str(OffToList[i]))
            OffTo.textChanged.connect(partial(self.save_cycles))
            
            
            grid.addWidget(lblOnTo, i + 1, 0)
            grid.addWidget(lblOnFrom, i + 1, 2)
            grid.addWidget(OnTo, i + 1, 1)
            grid.addWidget(OnFrom, i + 1, 3)
            
            grid.addWidget(lblOffTo, i + 1, 4)
            grid.addWidget(lblOffFrom, i + 1, 6)
            grid.addWidget(OffTo, i + 1, 5)
            grid.addWidget(OffFrom, i + 1, 7)
            
            grid.addWidget(subCycle, i + 1, 8) 
            if not i == 0:
                grid.addWidget(btnUp, i + 1, 9) 
            if not i == cycles - 1:
                grid.addWidget(btnDown, i + 1, 10) 

            OnTo_textboxes.append(OnTo)
            OnFrom_textboxes.append(OnFrom)
            OffTo_textboxes.append(OffTo)
            OffFrom_textboxes.append(OffFrom)
            all_textboxes.append(OnTo)
            all_textboxes.append(OnFrom)
            all_textboxes.append(OffTo)
            all_textboxes.append(OffFrom)
        
        grid.addWidget(addCycle, cycles + 3, 8) 
        grid.addWidget(btnSubmit, cycles + 4, 8) 
        # groupBox.setLayout(grid)

        # return groupBox
        return self.scroll
    def up_arrow(self, key):
        global cycles, OffFromList, OffToList, OnFromList, onToList, OnTo_textboxes, OnFrom_textboxes, OffTo_textboxes, OffFrom_textboxes
        up = key - 1
        OffTo_textboxes[key], OffTo_textboxes[up] = OffTo_textboxes[up], OffTo_textboxes[key]
        OffFrom_textboxes[key], OffFrom_textboxes[up] = OffFrom_textboxes[up], OffFrom_textboxes[key]
        OnTo_textboxes[key], OnTo_textboxes[up] = OnTo_textboxes[up], OnTo_textboxes[key]
        OnFrom_textboxes[key], OnFrom_textboxes[up] = OnFrom_textboxes[up], OnFrom_textboxes[key]
        self.delete_save_saveCycles()
        self.clearLayout(self.grid)
        self.grid.addWidget(self.lay(), 1, 0)
    def down_arrow(self, key):
        global cycles, OffFromList, OffToList, OnFromList, onToList, OnTo_textboxes, OnFrom_textboxes, OffTo_textboxes, OffFrom_textboxes
        down = key + 1
        OffTo_textboxes[key], OffTo_textboxes[down] = OffTo_textboxes[down], OffTo_textboxes[key]
        OffFrom_textboxes[key], OffFrom_textboxes[down] = OffFrom_textboxes[down], OffFrom_textboxes[key]
        OnTo_textboxes[key], OnTo_textboxes[down] = OnTo_textboxes[down], OnTo_textboxes[key]
        OnFrom_textboxes[key], OnFrom_textboxes[down] = OnFrom_textboxes[down], OnFrom_textboxes[key]
        self.delete_save_saveCycles()
        self.clearLayout(self.grid)
        self.grid.addWidget(self.lay(), 1, 0)
    def save_cycles(self):
        global cycles, OffFromList, OffToList, OnFromList, onToList, cycles_json, all_textboxes
        for i, j in enumerate(all_textboxes):
            temp = j.text()
            temp = temp.replace(' ', '')
            temp = temp.lower()
            rx = re.compile(r"[0,1][0-9][:][0-5][0-9][a,p][m]")
            if not rx.match(temp):
                return
        self.delete_save_saveCycles()
    def delete_cycle(self, key):
        global cycles, OnTo_textboxes, OnFrom_textboxes, OffTo_textboxes, OffFrom_textboxes
        cycles -= 1
        
        del OnTo_textboxes[key]
        del OnFrom_textboxes[key]
        del OffTo_textboxes[key]
        del OffFrom_textboxes[key]
        self.delete_save_saveCycles()
                    
        self.clearLayout(self.grid)
        self.grid.addWidget(self.lay(), 1, 0)      
    def delete_save_saveCycles(self):
        global cycles, alwaysOn, OffFromList, OffToList, OnFromList, onToList, OnTo_textboxes, OnFrom_textboxes, OffTo_textboxes, OffFrom_textboxes
        OffFromList.clear()
        OffToList.clear()
        OnFromList.clear()
        OnToList.clear()
        # alwaysOn.clear()
        
        with open(cycles_file) as file:
            cycles_json = json.load(file)
        for i, j in enumerate(OnTo_textboxes):
            temp = j.text()
            temp = temp.replace(' ', '')
            temp = temp.lower()
            OnToList.append(temp)
        for i, j in enumerate(OnFrom_textboxes):
            temp = j.text()
            temp = temp.replace(' ', '')
            temp = temp.lower()
            OnFromList.append(temp)
        for i, j in enumerate(OffTo_textboxes):
            temp = j.text()
            temp = temp.replace(' ', '')
            temp = temp.lower()
            OffToList.append(temp)
        for i, j in enumerate(OffFrom_textboxes):
            temp = j.text()
            temp = temp.replace(' ', '')
            temp = temp.lower()
            OffFromList.append(temp)
                    
        cycles_json.pop(0)
        cycles_json.append({
            "cycles": [str(cycles)],
            "always on": [str(self.radAlwaysOn.isChecked())],
            "OnTo": OnToList,
            "OnFrom": OnFromList,
            "OffTo": OffToList,
            "OffFrom": OffFromList
        })
        with open(cycles_file, mode='w+', encoding='utf-8') as file:
            json.dump(cycles_json, file, ensure_ascii=True, indent=4)
            
        OffFromList.clear()
        OffToList.clear()
        OnFromList.clear()
        OnToList.clear()
        alwaysOn.clear()
        
        with open(cycles_file) as file:
            cycles_json = json.load(file)
            for info in cycles_json:
                for c in info['cycles']:
                    cycles = int(c)
                for on in info['always on']:
                    alwaysOn.append(on)
                for OnTo in info['OnTo']:
                    OnToList.append(OnTo)
                for OnFrom in info['OnFrom']:
                    OnFromList.append(OnFrom)
                for OffTo in info['OffTo']:
                    OffToList.append(OffTo)
                for OffFrom in info['OffFrom']:
                    OffFromList.append(OffFrom)
    def btnAdd(self):
        global cycles, OffFromList, OffToList, OnFromList, cycles_json
        OffFromList.clear()
        OffToList.clear()
        OnFromList.clear()
        OnToList.clear()
        alwaysOn.clear()
        
        with open(cycles_file) as file:
            cycles_json = json.load(file)
            for info in cycles_json:
                for c in info['cycles']:
                    cycles = int(c)
                for on in info['always on']:
                    alwaysOn.append(on)
                for OnTo in info['OnTo']:
                    OnToList.append(OnTo)
                for OnFrom in info['OnFrom']:
                    OnFromList.append(OnFrom)
                for OffTo in info['OffTo']:
                    OffToList.append(OffTo)
                for OffFrom in info['OffFrom']:
                    OffFromList.append(OffFrom)
        cycles_json.pop(0)
        OnToList.append('')
        OnFromList.append('')
        OffToList.append('')
        OffFromList.append('')
        cycles +=1
        cycles_json.append({
            "cycles": [str(cycles)],
            "always on": [alwaysOn[0]],
            "OnTo": OnToList,
            "OnFrom": OnFromList,
            "OffTo": OffToList,
            "OffFrom": OffFromList
        })
        with open(cycles_file, mode='w+', encoding='utf-8') as file:
            json.dump(cycles_json, file, ensure_ascii=True, indent=4)
        OffFromList.clear()
        OffToList.clear()
        OnFromList.clear()
        OnToList.clear()
        alwaysOn.clear()
        
        with open(cycles_file) as file:
            cycles_json = json.load(file)
            for info in cycles_json:
                for c in info['cycles']:
                    cycles = int(c)
                for on in info['always on']:
                    alwaysOn.append(on)
                for OnTo in info['OnTo']:
                    OnToList.append(OnTo)
                for OnFrom in info['OnFrom']:
                    OnFromList.append(OnFrom)
                for OffTo in info['OffTo']:
                    OffToList.append(OffTo)
                for OffFrom in info['OffFrom']:
                    OffFromList.append(OffFrom)
        self.clearLayout(self.grid)
        self.grid.addWidget(self.lay(), 1, 0)
    def submit(self):
        global cycles, OffFromList, OffToList, OnFromList, onToList, cycles_json, all_textboxes
        for i, j in enumerate(all_textboxes):
            temp = j.text()
            temp = temp.replace(' ', '')
            temp = temp.lower()
            print(temp)
            rx = re.compile(r"[0,1][0-9][:][0-5][0-9][a,p][m]")
            if not rx.match(j.text()):
                QMessageBox.warning(self, 'Format error!', f"{j.text()}\n\nYou don't have the correct format!\n\nThe correct format should look like: 02:57am or 11:01pm.", QMessageBox.Ok, QMessageBox.Ok)
                return
        self.delete_save_saveCycles()
        self.close()
def exit_handler():
    running = False
    print('Exit pressed')
    camera.end_cam()
    camera.cap.release()
    cv2.destroyAllWindows()
    sys.exit()
# class
if __name__ == '__main__':
    atexit.register(exit_handler)
    if not os.path.exists('Pics'):
        os.mkdir('Pics')
    if os.path.exists(settings_file):
        with open(settings_file) as file:
            settings_json = json.load(file)
            for info in settings_json:
                for color in info['saved color']:
                    saved_color.append(color)
                for screen in info['capture screen']:
                    cap_screen.append(screen)
                for video in info['record video']:
                    record_video.append(video)
                for email_b in info['send email']:
                    send_email.append(email_b)
                for smile in info['smiley face']:
                    smiley_face.append(smile)
                for dark in info['dark mode']:
                    dark_mode.append(dark)
                for email_d in info['email delay']:
                    email_delay.append(email_d)
                for picture in info['picture delay']:
                    picture_delay.append(picture)
                for ind in info['selected data index']:
                    selected_data_index.append(ind)
                for face in info['face detect']:
                    face_detect.append(face)
                for email in info['email address']:
                    email_address.append(email)
    elif not os.path.exists(settings_file):
        file = open(settings_file, "w+")
        file.write(
"""[
    {
        \"saved color\":[\"0\", \"255\", \"0\"],
        \"capture screen\": [\"False\"],
        \"record video\": [\"False\"],
        \"smiley face\": [\"False\"],
        \"dark mode\": [\"True\"],
        \"send email\": [\"True\"],
        \"email delay\": [\"10\"],
        \"picture delay\": [\"5\"],
        \"selected data index\": [\"7\"],
        \"face detect\": [\"True\"],
        \"email address\": [\"\"]
    }
]"""
)
        file.close()
        with open(settings_file) as file:
            settings_json = json.load(file)
            for info in settings_json:
                for color in info['saved color']:
                    saved_color.append(color)
                for screen in info['capture screen']:
                    cap_screen.append(screen)
                for video in info['record video']:
                    record_video.append(video)
                for email in info['send email']:
                    send_email.append(email)
                for smile in info['smiley face']:
                    smiley_face.append(smile)
                for dark in info['dark mode']:
                    dark_mode.append(dark)
                for email_d in info['email delay']:
                    email_delay.append(email_d)
                for picture in info['picture delay']:
                    picture_delay.append(picture)
                for ind in info['selected data index']:
                    selected_data_index.append(ind)
                for face in info['face detect']:
                    face_detect.append(face)
                for email in info['email address']:
                    email_address.append(email)
    button_css = 'background-color: rgb(' + str(saved_color[0]) + ', ' + str(saved_color[1]) + ', ' + str(saved_color[2]) + ')'

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    if dark_mode[0] == 'True':
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0.0, QColor(40, 40, 40))
        gradient.setColorAt(1.0, QColor(30, 30, 30))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(30, 30, 30))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(palette)
    else:
        app.setPalette(QApplication.style().standardPalette())
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0.0, QColor(240, 240, 240))
        gradient.setColorAt(1.0, QColor(215, 215, 215))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setBrush(QPalette.Window, QBrush(gradient))
        app.setPalette(palette)
    main = MainMenu()
    main.show()
    # START_CAMERA = multiprocessing.Process(target=MainMenu)
    sys.exit(app.exec_())
    # START_CAMERA.start()
