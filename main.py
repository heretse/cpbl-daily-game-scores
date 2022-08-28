import sys
import json
from time import sleep
from typing import Any
import requests
import datetime

from os import getenv, path
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QGridLayout,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import QObject, QRunnable, Qt, QThread, pyqtSignal

requestVerificationToken = None
my_labels = []
keep_running = True

def imageByTeamCode(teamCode):
   if teamCode == 'ACN011':
      return 'images/logo_brothers.png'
   elif teamCode == 'ADD011':
      return 'images/logo_lions.png'
   elif teamCode == 'AAA011':
      return 'images/logo_dragon.png'
   elif teamCode == 'AJL011':
      return 'images/logo_monkeys.png'
   elif teamCode == 'AEO011':
      return 'images/logo_fubon.png'
   else:
      return ''

class Worker(QObject):
   finished = pyqtSignal()
   progress = pyqtSignal(list)

   def run(self):
      # """Long-running task."""
      global keep_running
      while keep_running:
         try:
            docs = fetchGameDetail()
            self.progress.emit(docs)
            sleep(30)
         except Exception as err:
            print(err)
            break
      self.finished.emit()

def fetchGameDetail():
   today = datetime.date.today()

   global requestVerificationToken
   if requestVerificationToken == None:
      url = "https://www.cpbl.com.tw"
      response = requests.get(url, verify=False)
      soup = BeautifulSoup(response.text, "html.parser")
      
      requestVerificationToken = soup.find('input', attrs={'name': '__RequestVerificationToken'}).get('value')
      print(requestVerificationToken)

   url = "https://www.cpbl.com.tw/home/getdetaillist"
   data = "__RequestVerificationToken={}&GameDate={}".format(requestVerificationToken, today.strftime('%Y/%m/%d')) 
   headers = {'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': 'application/json'}

   r = requests.post(url, data=data, headers=headers, verify=False)
   # print(r.json())

   return json.loads(r.json()['GameADetailJson'])

class Window(QMainWindow):
   def __init__(self, parent=None):
      super().__init__(parent)
      self.setupUi()

   def setupUi(self):
      self.setWindowTitle("CPBL Game Info.")
      self.setGeometry(0, 0, 480, 280)

      self.centralWidget = QWidget()
      self.setCentralWidget(self.centralWidget)
  
      self.gridLayout = QGridLayout(self.centralWidget)

      for index in range(0, 2):
         horLayout = QHBoxLayout()

         visitingTeamLbl = QLabel()
         visitingTeamLbl.setAlignment(Qt.AlignCenter)
         visitingTeamLbl.resize(38, 38)
         horLayout.addWidget(visitingTeamLbl)

         horLayout.addStretch(1)

         totalScoreLbl = QLabel()
         totalScoreLbl.setAlignment(Qt.AlignCenter)
         totalScoreLbl.setText("-：-")
         totalScoreLbl.setFont(QFont('Heiti TC', 60))
         totalScoreLbl.setStyleSheet("color:#333333")
         horLayout.addWidget(totalScoreLbl)

         horLayout.addStretch(1)

         homeTeamLbl = QLabel()
         homeTeamLbl.setAlignment(Qt.AlignCenter)
         homeTeamLbl.resize(38, 38)
         horLayout.addWidget(homeTeamLbl)

         if index == 0:
            self.visitingTeamLbl_0 = visitingTeamLbl
            self.totalScoreLbl_0   = totalScoreLbl
            self.homeTeamLbl_0     = homeTeamLbl
         elif index == 1:
            self.visitingTeamLbl_1 = visitingTeamLbl
            self.totalScoreLbl_1   = totalScoreLbl
            self.homeTeamLbl_1     = homeTeamLbl

         self.gridLayout.addLayout(horLayout, index, 0)
      
      self.startBtn = QPushButton("Start")
      self.startBtn.setToolTip('Clicking it will start to fetch data!') 
      self.startBtn.clicked.connect(self.runTask)

      self.stopBtn = QPushButton("Stop")
      self.stopBtn.setEnabled(False)
      self.stopBtn.setToolTip('Clicking it will stop to fetch data!') 
      self.stopBtn.clicked.connect(self.stopTask)

      horLayout = QHBoxLayout()
      horLayout.addStretch(1)
      horLayout.addWidget(self.startBtn)
      horLayout.addStretch(1)
      horLayout.addWidget(self.stopBtn)
      horLayout.addStretch(1)
      self.gridLayout.addLayout(horLayout, 2, 0)

      self.centralWidget.setLayout(self.gridLayout)

   def refreshUi(self, doc, index):
      pixmap_0 = QPixmap(imageByTeamCode(doc['VisitingTeamCode']))
      textVisitingTotalScore = '-'
      if doc['VisitingTotalScore'] != None:
            textVisitingTotalScore = str(doc['VisitingTotalScore'])
      textHomeTotalScore = '-'
      if doc['HomeTotalScore'] != None:
         textHomeTotalScore = str(doc['HomeTotalScore'])
      pixmap_1 = QPixmap(imageByTeamCode(doc['HomeTeamCode']))

      if index == 0:
         self.visitingTeamLbl_0.setPixmap(pixmap_0)
         self.totalScoreLbl_0.setText("{}：{}".format(textVisitingTotalScore, textHomeTotalScore))
         self.homeTeamLbl_0.setPixmap(pixmap_1)
      elif index == 1:
         self.visitingTeamLbl_1.setPixmap(pixmap_0)
         self.totalScoreLbl_1.setText("{}：{}".format(textVisitingTotalScore, textHomeTotalScore))
         self.homeTeamLbl_1.setPixmap(pixmap_1)
   
   def runTask(self):
      # Create a QThread object
      self.thread = QThread()
      # Create a worker object
      self.worker = Worker()
      # Move worker to the thread
      self.worker.moveToThread(self.thread)
      # Connect signals and slots
      self.thread.started.connect(self.worker.run)
      self.worker.finished.connect(self.thread.quit)
      self.worker.finished.connect(self.worker.deleteLater)
      self.thread.finished.connect(self.thread.deleteLater)
      self.worker.progress.connect(self.updateUi)
      # Start the thread
      self.thread.start()

      # Final resets
      global keep_running
      keep_running = True
      self.startBtn.setEnabled(False)
      self.stopBtn.setEnabled(True)
      self.thread.finished.connect(
         lambda: self.startBtn.setEnabled(True)
      )
      self.thread.finished.connect(
         lambda: self.stopBtn.setEnabled(False)
      )
   
   def stopTask(self):
      global keep_running
      keep_running = False
   
   def updateUi(self, docs):
      for index, doc in enumerate(docs):
         self.refreshUi(doc, index)

if __name__ == '__main__':
   app = QApplication(sys.argv)
   window = Window()
   window.show()
   sys.exit(app.exec_())
