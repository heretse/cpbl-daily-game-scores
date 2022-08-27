import sys
import json
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
from PyQt5.QtCore import QRunnable, Qt, QThreadPool, pyqtSignal

def renderDoc(layout, doc, index):

   horLayout = QHBoxLayout()
   
   textLabel = QLabel()
   textLabel.setAlignment(Qt.AlignCenter)
   pixmap = QPixmap(imageByTeamCode(doc['VisitingTeamCode']))
   textLabel.setPixmap(pixmap)
   horLayout.addWidget(textLabel)

   horLayout.addStretch(1)

   textVisitingTotalScore = '-'
   if doc['VisitingTotalScore'] != None:
      textVisitingTotalScore = str(doc['VisitingTotalScore'])

   textHomeTotalScore = '-'
   if doc['HomeTotalScore'] != None:
      textHomeTotalScore = str(doc['HomeTotalScore'])

   textLabel = QLabel()
   textLabel.setAlignment(Qt.AlignCenter)
   textLabel.setText("{}：{}".format(textVisitingTotalScore, textHomeTotalScore))
   textLabel.setFont(QFont('Heiti TC', 60))
   textLabel.setStyleSheet("color:#333333")
   horLayout.addWidget(textLabel)

   horLayout.addStretch(1)

   textLabel = QLabel()
   textLabel.setAlignment(Qt.AlignCenter)
   pixmap = QPixmap(imageByTeamCode(doc['HomeTeamCode']))
   textLabel.setPixmap(pixmap)
   horLayout.addWidget(textLabel)

   layout.addLayout(horLayout, index, 0)

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

def fetchGameDetail():
   today = datetime.date.today()

   url = "https://www.cpbl.com.tw"
   response = requests.get(url, verify=False)
   soup = BeautifulSoup(response.text, "html.parser")
   requestVerificationToken = soup.find('input', attrs={'name': '__RequestVerificationToken'}).get('value')
   print(requestVerificationToken)

   url = "https://www.cpbl.com.tw/home/getdetaillist"
   data = "__RequestVerificationToken={}&GameDate={}".format(requestVerificationToken, today.strftime('%Y/%m/%d')) 
   headers = {'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': 'application/json'}

   r = requests.post(url, data=data, headers=headers, verify=False)
   print(r.json())

   return r.json()

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

      gameDetail = fetchGameDetail()
      docs = json.loads(gameDetail['GameADetailJson'])
      for index, doc in enumerate(docs):
         renderDoc(self.gridLayout, doc, index)
      
      button = QPushButton("Close") 
      button.setToolTip('This is a QPushButton widget. Clicking it will close the program!') 
      button.clicked.connect(app.quit)

      horLayout = QHBoxLayout()
      horLayout.addStretch(1)
      horLayout.addWidget(button)
      horLayout.addStretch(1)
      self.gridLayout.addLayout(horLayout, 2, 0)

      self.centralWidget.setLayout(self.gridLayout)

if __name__ == '__main__':
   app = QApplication(sys.argv)
   window = Window()
   window.show()
   sys.exit(app.exec_())
