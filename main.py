import sys
import json
import requests
import datetime

from os import getenv, path
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import pyqtSlot


# wget --no-check-certificate -O logo_monkeys.png https://www.cpbl.com.tw/files/atts/0L015574823122453305/logo_monkeys.png
# wget --no-check-certificate -O logo_lions.png https://www.cpbl.com.tw/files/atts/0L021496162893869773/logo_lions.png
# wget --no-check-certificate -O logo_brothers.png https://www.cpbl.com.tw//files/atts/0L021497108709222204/logo_brothers.png
# wget --no-check-certificate -O logo_dragon.png https://www.cpbl.com.tw/files/atts/0L021497845061333235/logo_dragon.png
# wget --no-check-certificate -O logo_fubon.png https://www.cpbl.com.tw//files/atts/0L021495969510091777/logo_fubon.png

def renderDoc(widget, doc, pos_y):
   
   textLabel = QLabel(widget)
   textLabel.move(50, pos_y)
   pixmap = QPixmap(imageByTeamCode(doc['VisitingTeamCode']))
   textLabel.setPixmap(pixmap)

   textLabel = QLabel(widget)
   textLabel.setText(str(doc['VisitingTotalScore']))
   textLabel.setFont(QFont('Arial', 60))
   textLabel.move(185, pos_y + 10)

   textLabel = QLabel(widget)
   textLabel.setText('：')
   textLabel.setFont(QFont('Arial', 60))
   textLabel.move(205, pos_y)

   textLabel = QLabel(widget)
   textLabel.setText(str(doc['HomeTotalScore']))
   textLabel.setFont(QFont('Arial', 60))
   textLabel.move(265, pos_y + 10)

   textLabel = QLabel(widget)
   textLabel.move(350, pos_y)
   pixmap = QPixmap(imageByTeamCode(doc['HomeTeamCode']))
   textLabel.setPixmap(pixmap)

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

def window():

   today = datetime.date.today()

   url = "https://www.cpbl.com.tw"
   response = requests.get(url, verify=False)
   soup = BeautifulSoup(response.text, "html.parser")
   requestVerificationToken = soup.find('input', attrs={'name': '__RequestVerificationToken'}).get('value')
   print(requestVerificationToken)

   url = "https://www.cpbl.com.tw/home/getdetaillist"
   data = "__RequestVerificationToken={}&GameDate={}".format(requestVerificationToken, '2022%2F08%2F21') # today.strftime('%Y%2F%m%2F%d')
   headers = {'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': 'application/json'}

   r = requests.post(url, data=data, headers=headers, verify=False)
   print(r.json())

   docs = json.loads(r.json()['GameADetailJson'])

   app = QApplication(sys.argv)
   widget = QWidget()

   for index, doc in enumerate(docs):
      renderDoc(widget, doc, 50 + index * 140)

   widget.setGeometry(50, 50, 480, 320)
   widget.setWindowTitle("PyQt5 Example")
   widget.show()

   sys.exit(app.exec_())

if __name__ == '__main__':
   window()
