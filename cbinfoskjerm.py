import os
import ctypes
os.system('pyuic5 -x adui.ui -o adui.py')
import feedparser
from PyQt5 import QtWidgets,QtGui,QtCore,QtMultimedia
from adui import Ui_MainWindow
import sys
from multiprocessing import freeze_support
from datetime import datetime
from appdirs import user_data_dir
from shutil import copyfile
import requests
from bs4 import BeautifulSoup

app_path = user_data_dir()+'\\CBInfoSystem\\'
video_path = app_path+'videos\\'
config_file = app_path+r'config.ini'

if not os.path.exists(app_path):
    os.makedirs(app_path)
if not os.path.exists(video_path):
    os.makedirs(video_path)

#try:
#    copyfile('logo.png', app_path+'\\logo.png'.replace('\\','/'))
#    copyfile('icon.ico', app_path+'\\icon.ico'.replace('\\','/'))
#except Exception as e:
#    print('Err copy file:',e)
import glob

txtfiles = []
for file in glob.glob(video_path+'*'):
    file = file.replace('\\', '/')
    txtfiles.append(file)
full_news=''
global_width = 1600
import time

class weather_update(QtCore.QObject):
    weather_signal = QtCore.pyqtSignal(str,str,str,str,str,str,str,str)
    def __init__(self,weather_url1,weather_url2,parent=None):
        QtCore.QObject.__init__(self,parent)
        self.weather_url1 = weather_url1
        self.weather_url2 = weather_url2

    @QtCore.pyqtSlot()
    def check_weather(self):
        while(1):
            try:
                response = requests.get(self.weather_url1)
                data = response.content
                soup = BeautifulSoup(data)

                location1 = soup.forecast.location['name']
                temp1 = soup.forecast.tabular.findAll('time')[0].temperature['value']
                wtext1 =soup.forecast.tabular.findAll('time')[0].windspeed['name']+' '+soup.forecast.tabular.findAll('time')[0].symbol['name']
                icon1 = soup.forecast.tabular.findAll('time')[0].symbol['var']
                print('ICON1',icon1)


            except Exception as e:
                location1 = 'Err'
                temp1 ='Err'
                self.weather_signal.emit('E','E','Err','Err')
                time.sleep(10)
                return
    
            try:

                response = requests.get(self.weather_url2)
                data = response.content
                soup = BeautifulSoup(data)

                location2 = soup.forecast.location['name']
                temp2 = soup.forecast.tabular.findAll('time')[0].temperature['value']
                wtext2 =soup.forecast.tabular.findAll('time')[0].windspeed['name']+' '+soup.forecast.tabular.findAll('time')[0].symbol['name']
                icon2 = soup.forecast.tabular.findAll('time')[0].symbol['var']
                print('ICON2',icon2)


            except Exception as e:
                location2 = 'Err'
                temp2 ='Err'
                self.weather_signal.emit('E','E','Err','Err')
                time.sleep(10)
                return

            self.weather_signal.emit(temp1+chr(176),temp2+chr(176),location1,location2,icon1,icon2,wtext1,wtext2)
            time.sleep(60*5)


class news_update(QtCore.QObject):
    news_signal = QtCore.pyqtSignal(str)
    def __init__(self,news_url,parent=None):
        QtCore.QObject.__init__(self,parent)
        self.news_url = news_url
 
    @QtCore.pyqtSlot()
    def check_news(self):
        global full_news
        while(1):
            try:
                d = feedparser.parse(self.news_url)['entries'][0:9]
                tmp_full_news = ' ';#*int(self.label_summary.width()/2)
                for x in d:
                    title = x['title']
                    summary= x['summary']        
                    if len(summary)==0:
                        summary= title
                    tmp_full_news = tmp_full_news+ '    \u2022'  + summary
                full_news =tmp_full_news
                self.news_signal.emit( 'news udpate success.' )
            except Exception as e:
                full_news = 'Error fetching feed:'+str(e)
                self.news_signal.emit( 'news update failed.' )
            time.sleep(60*5)


class MainWindow_exec(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
#        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        
#        self.label_logo.setStyleSheet('border:1px solid')

        self.settings = QtCore.QSettings(config_file, QtCore.QSettings.IniFormat)
        self.news_url = self.settings.value('news_rss_feed_link','https://www.nrk.no/rogaland/siste.rss')
        self.weather_url1 = self.settings.value('weather_url1','https://www.yr.no/sted/Norge/Rogaland/Karm%C3%B8y/Kopervik/varsel.xml')
        self.weather_url2 = self.settings.value('weather_url2','https://www.yr.no/sted/Norge/Rogaland/Stavanger/Stavanger/varsel.xml')
        self.speed_event = float(self.settings.value('speed_event',3))

        self.settings.setValue('news_rss_feed_link',self.news_url)
        self.settings.setValue('weather_url1',self.weather_url1)
        self.settings.setValue('weather_url2',self.weather_url2)
        self.settings.sync()

        self.mediaPlayer = QtMultimedia.QMediaPlayer(self)
        self.mediaPlayer.setVideoOutput(self.video_player)
        self.curr_media_cnt=0

        try:
            url = QtCore.QUrl(txtfiles[self.curr_media_cnt])
            self.mediaPlayer.setMedia(QtMultimedia.QMediaContent(url))
        except:
            None
        self.mediaPlayer.play()
        self.mediaPlayer.mediaStatusChanged.connect(self.handleMediaStateChanged)

        self.clock_timer = QtCore.QTimer()
        self.clock_timer.timeout.connect(self.call_clock_update)
        self.clock_timer.start(1000)
        self.news_offset = 0

        global full_news

        full_news='Initializing...'
        
        self.uiResize()
        self.signalUpdateUI()

        self.news_obj = news_update(self.news_url)
        self.news_thread = QtCore.QThread()
        self.news_obj.news_signal.connect(self.set_news)
        self.news_obj.moveToThread(self.news_thread)
        self.news_thread.started.connect(self.news_obj.check_news)
        self.news_thread.start()

        self.weather_obj = weather_update(self.weather_url1,self.weather_url2)
        self.weather_thread = QtCore.QThread()
        self.weather_obj.weather_signal.connect(self.set_weather)
        self.weather_obj.moveToThread(self.weather_thread)
        self.weather_thread.started.connect(self.weather_obj.check_weather)
        self.weather_thread.start()
        self.resizeEvent(self.speed_event)
        self.label_logo.setPixmap(QtGui.QPixmap(app_path+'\\logo.png'.replace('\\','/')))
        self.label_logo.setScaledContents(True)



    def set_weather(self,temp1=None,temp2=None,location1=None,location2=None,icon1=None,icon2=None,wtext1=None,wtext2=None):
        self.label_location1.setText(location1)
        self.label_temp1.setText(temp1)
        self.label_location2.setText(location2)
        self.label_temp2.setText(temp2)
        print(icon1,icon2)
        self.label_6.setPixmap(QtGui.QPixmap(icon1+".png"))
        self.label_6.setScaledContents(True)
        self.label_7.setPixmap(QtGui.QPixmap(icon2+".png"))
        self.label_7.setScaledContents(True)
        self.label_text1.setText(wtext1)
        self.label_text2.setText(wtext2)
        
        print(icon1,icon2)
        
        if self.label_6.pixmap.isNull() == True:
            self.label_6.setPixmap(QtGui.QPixmap('0'+icon1+".png"))
            self.label_6.setScaledContents(True)
        if self.label_7.pixmap.isNull() == True:
            self.label_7.setPixmap(QtGui.QPixmap('0'+icon1+".png"))
            self.label_7.setScaledContents(True)
        if self.label_6.pixmap.isNull() == True:
            self.label_6.setPixmap(QtGui.QPixmap( icon1.lstrip('0')+".png"))
            self.label_6.setScaledContents(True)
        if self.label_7.pixmap.isNull() == True:
            self.label_7.setPixmap(QtGui.QPixmap(icon1.lstrip('0')+".png"))
            self.label_7.setScaledContents(True)

            
        print('pixmap1:',self.label_6.pixmap.isNull() )
        print('pixmap2:',self.label_7.pixmap.isNull() )

    def set_news(self,news):
        print('Updating news',news)

    def resizeEvent(self,event=None):
        wid = self.width()/1600
#        self.label_logo.resize(100*wid,100)
        self.label_summary._speed = self.speed_event*wid
        
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(20*wid)
        self.label_summary.setFont(font)
        self.label_summary.set_height()

        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(30*wid)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_location1.setFont(font)
        self.label_location2.setFont(font)

        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(18*wid)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_temp1.setFont(font)
        self.label_temp2.setFont(font)

        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(15*wid)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_clock.setFont(font)




    def signalUpdateUI(self):
        timer = QtCore.QTimer(self, interval=100)
        timer.timeout.connect(self.updateUI)
        timer.start()
        self.updateUI()

    def updateUI(self):
        #update some text color and contents
        #update marquee label contents
        global full_news

#        print( full_news)
        self.label_summary.setText( full_news)
        self.label_summary.updateCoordinates()
        self.update()

    def uiResize(self):
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(int(self.settings.value('video_widget_h_stretch',80)))
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.video_widget.sizePolicy().hasHeightForWidth())
        self.video_widget.setSizePolicy(sizePolicy)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(int(self.settings.value('news_widget_h_stretch',80)))
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.news_widget.sizePolicy().hasHeightForWidth())
        self.news_widget.setSizePolicy(sizePolicy)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(int(self.settings.value('clock_widget_h_stretch',18)))
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.clock_widget.sizePolicy().hasHeightForWidth())
        self.clock_widget.setSizePolicy(sizePolicy)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(int(self.settings.value('weather_widget_h_stretch',18)))
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.weather_widget.sizePolicy().hasHeightForWidth())
        self.weather_widget.setSizePolicy(sizePolicy)
        
        
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(int(self.settings.value('upper_widget_v_stretch',90)))
        sizePolicy.setHeightForWidth(self.upper_widget.sizePolicy().hasHeightForWidth())
        self.upper_widget.setSizePolicy(sizePolicy)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(int(self.settings.value('bottom_widget_v_stretch',10)))
        sizePolicy.setHeightForWidth(self.bottom_widget.sizePolicy().hasHeightForWidth())
        self.bottom_widget.setSizePolicy(sizePolicy)
        
    def call_clock_update(self):
        self.label_clock.setText( datetime.now().strftime('%H:%M:%S \n %d-%m-%Y') )
#        self.label_logo.resize(100,100)

    def handleMediaStateChanged(self,state):
        print('Recall Media',state)
        if state == 7:
            self.curr_media_cnt+=1
            if self.curr_media_cnt == len(txtfiles):
                self.curr_media_cnt=0
            url = QtCore.QUrl(txtfiles[self.curr_media_cnt])
            self.mediaPlayer.setMedia(QtMultimedia.QMediaContent(url))
            self.mediaPlayer.play()

    def keyPressEvent(self,event):
#        print(event.key() )
        if  event.key() ==  QtCore.Qt.Key_F:
            self.showFullScreen()
        if  event.key() ==  QtCore.Qt.Key_M:
            self.showMaximized()
        elif event.key() == QtCore.Qt.Key_Left:
            video_widget_h_stretch =  self.video_widget.sizePolicy().horizontalStretch()-1
            news_widget_h_stretch =  self.news_widget.sizePolicy().horizontalStretch()-1
            weather_widget_h_stretch =  self.weather_widget.sizePolicy().horizontalStretch()+1
            clock_widget_h_stretch =  self.clock_widget.sizePolicy().horizontalStretch()+1

            self.settings.setValue('video_widget_h_stretch',video_widget_h_stretch)
            self.settings.setValue('news_widget_h_stretch',news_widget_h_stretch)
            self.settings.setValue('weather_widget_h_stretch',weather_widget_h_stretch)
            self.settings.setValue('clock_widget_h_stretch',clock_widget_h_stretch)
            self.settings.sync()

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(video_widget_h_stretch)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.video_widget.sizePolicy().hasHeightForWidth())
            self.video_widget.setSizePolicy(sizePolicy)

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(news_widget_h_stretch)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.news_widget.sizePolicy().hasHeightForWidth())
            self.news_widget.setSizePolicy(sizePolicy)

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(weather_widget_h_stretch)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.clock_widget.sizePolicy().hasHeightForWidth())
            self.clock_widget.setSizePolicy(sizePolicy)

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(clock_widget_h_stretch)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.weather_widget.sizePolicy().hasHeightForWidth())
            self.weather_widget.setSizePolicy(sizePolicy)
            
        elif event.key() == QtCore.Qt.Key_Up:
            upper_widget_v_stretch =  self.upper_widget.sizePolicy().verticalStretch()-1
            bottom_widget_v_stretch =  self.bottom_widget.sizePolicy().verticalStretch()+1

            self.settings.setValue('upper_widget_v_stretch',upper_widget_v_stretch)
            self.settings.setValue('bottom_widget_v_stretch',bottom_widget_v_stretch)
            self.settings.sync()

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(upper_widget_v_stretch)
            sizePolicy.setHeightForWidth(self.upper_widget.sizePolicy().hasHeightForWidth())
            self.upper_widget.setSizePolicy(sizePolicy)

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(bottom_widget_v_stretch)
            sizePolicy.setHeightForWidth(self.bottom_widget.sizePolicy().hasHeightForWidth())
            self.bottom_widget.setSizePolicy(sizePolicy)
            self.resizeEvent()

        elif event.key() == QtCore.Qt.Key_Right:
            video_widget_h_stretch =  self.video_widget.sizePolicy().horizontalStretch()+1
            news_widget_h_stretch =  self.news_widget.sizePolicy().horizontalStretch()+1
            weather_widget_h_stretch =  self.weather_widget.sizePolicy().horizontalStretch()-1
            clock_widget_h_stretch =  self.clock_widget.sizePolicy().horizontalStretch()-1

            self.settings.setValue('video_widget_h_stretch',video_widget_h_stretch)
            self.settings.setValue('news_widget_h_stretch',news_widget_h_stretch)
            self.settings.setValue('weather_widget_h_stretch',weather_widget_h_stretch)
            self.settings.setValue('clock_widget_h_stretch',clock_widget_h_stretch)
            self.settings.sync()

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(video_widget_h_stretch)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.video_widget.sizePolicy().hasHeightForWidth())
            self.video_widget.setSizePolicy(sizePolicy)

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(news_widget_h_stretch)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.news_widget.sizePolicy().hasHeightForWidth())
            self.news_widget.setSizePolicy(sizePolicy)

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(weather_widget_h_stretch)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.clock_widget.sizePolicy().hasHeightForWidth())
            self.clock_widget.setSizePolicy(sizePolicy)

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(clock_widget_h_stretch)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.weather_widget.sizePolicy().hasHeightForWidth())
            self.weather_widget.setSizePolicy(sizePolicy)

        elif event.key() == QtCore.Qt.Key_Down:
            upper_widget_v_stretch =  self.upper_widget.sizePolicy().verticalStretch()+1
            bottom_widget_v_stretch =  self.bottom_widget.sizePolicy().verticalStretch()-1

            self.settings.setValue('upper_widget_v_stretch',upper_widget_v_stretch)
            self.settings.setValue('bottom_widget_v_stretch',bottom_widget_v_stretch)
            self.settings.sync()

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(upper_widget_v_stretch)
            sizePolicy.setHeightForWidth(self.upper_widget.sizePolicy().hasHeightForWidth())
            self.upper_widget.setSizePolicy(sizePolicy)

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(bottom_widget_v_stretch)
            sizePolicy.setHeightForWidth(self.bottom_widget.sizePolicy().hasHeightForWidth())
            self.bottom_widget.setSizePolicy(sizePolicy)
            self.resizeEvent()
        elif event.key() == QtCore.Qt.Key_W:
            return
            '''
            self.news_offset = self.news_offset+1
            self.settings.setValue('news_offset',self.news_offset)
            self.settings.sync()
            self.resizeEvent()
            '''
        elif event.key() == QtCore.Qt.Key_Q:
            return
            '''
            self.news_offset = self.news_offset-1
            self.settings.setValue('news_offset',self.news_offset)
            self.settings.sync()
            self.resizeEvent()
            '''
        elif event.key() == QtCore.Qt.Key_E:
            font_temp=QtGui.QFont(self.label_location1.font().family(),self.label_location1.font().pointSize()) 
            if self.label_location1.font().bold()==True:
                font_temp.setBold(True)
            if self.label_location1.font().italic()==True:
                font_temp.setItalic(True)
            font, ok = QtWidgets.QFontDialog.getFont(font_temp)
            if ok:
                fnt = font.toString().split(',')
                print(fnt)
                font = QtGui.QFont()
                font.setFamily( fnt[0] )
                font.setPointSize( int(fnt[1]) )
                if fnt[-1]=='Bold':
                    font.setBold(True)
                elif fnt[-1]=='Italic':
                    font.setItalic(True)
                elif fnt[-1]=='Bold Italic':
                    font.setItalic(True)
                    font.setBold(True)
                self.label_location1.setFont(font)

                self.settings.setValue('label_location1_fname', fnt[0] )
                self.settings.setValue('label_location1_fsize', int(fnt[1]) )
                if fnt[-1]=='Bold':
                    self.settings.setValue('label_location1_fbold', 1 )
                    self.settings.setValue('label_location1_italic', 0)
                elif fnt[-1]=='Italic':
                    self.settings.setValue('label_location1_fbold', 0 )
                    self.settings.setValue('label_location1_italic', 1)
                elif fnt[-1]=='Bold Italic':
                    self.settings.setValue('label_location1_fbold', 1 )
                    self.settings.setValue('label_location1_italic', 1)
                self.settings.sync()

        elif event.key() == QtCore.Qt.Key_R:
            font_temp=QtGui.QFont(self.label_temp1.font().family(),self.label_temp1.font().pointSize()) 
            if self.label_temp1.font().bold()==True:
                font_temp.setBold(True)
            if self.label_temp1.font().italic()==True:
                font_temp.setItalic(True)
            font, ok = QtWidgets.QFontDialog.getFont(font_temp)
            if ok:
                fnt = font.toString().split(',')
                print(fnt)
                font = QtGui.QFont()
                font.setFamily( fnt[0] )
                font.setPointSize( int(fnt[1]) )
                if fnt[-1]=='Bold':
                    font.setBold(True)
                elif fnt[-1]=='Italic':
                    font.setItalic(True)
                elif fnt[-1]=='Bold Italic':
                    font.setItalic(True)
                    font.setBold(True)
                self.label_temp1.setFont(font)


                self.settings.setValue('label_temp1_fname', fnt[0] )
                self.settings.setValue('label_temp1_fsize', int(fnt[1]) )
                if fnt[-1]=='Bold':
                    self.settings.setValue('label_temp1_fbold', 1 )
                    self.settings.setValue('label_temp1_italic', 0)
                elif fnt[-1]=='Italic':
                    self.settings.setValue('label_temp1_fbold', 0 )
                    self.settings.setValue('label_temp1_italic', 1)
                elif fnt[-1]=='Bold Italic':
                    self.settings.setValue('label_temp1_fbold', 1 )
                    self.settings.setValue('label_temp1_italic', 1)
                self.settings.sync()


        elif event.key() == QtCore.Qt.Key_T:
            font_temp=QtGui.QFont(self.label_location2.font().family(),self.label_location2.font().pointSize()) 
            if self.label_location2.font().bold()==True:
                font_temp.setBold(True)
            if self.label_location2.font().italic()==True:
                font_temp.setItalic(True)
            font, ok = QtWidgets.QFontDialog.getFont(font_temp)
            if ok:
                fnt = font.toString().split(',')
                print(fnt)
                font = QtGui.QFont()
                font.setFamily( fnt[0] )
                font.setPointSize( int(fnt[1]) )
                if fnt[-1]=='Bold':
                    font.setBold(True)
                elif fnt[-1]=='Italic':
                    font.setItalic(True)
                elif fnt[-1]=='Bold Italic':
                    font.setItalic(True)
                    font.setBold(True)
                self.label_location2.setFont(font)


                self.settings.setValue('label_location2_fname', fnt[0] )
                self.settings.setValue('label_location2_fsize', int(fnt[1]) )
                if fnt[-1]=='Bold':
                    self.settings.setValue('label_location2_fbold', 1 )
                    self.settings.setValue('label_location2_italic', 0)
                elif fnt[-1]=='Italic':
                    self.settings.setValue('label_location2_fbold', 0 )
                    self.settings.setValue('label_location2_italic', 1)
                elif fnt[-1]=='Bold Italic':
                    self.settings.setValue('label_location2_fbold', 1 )
                    self.settings.setValue('label_location2_italic', 1)
                self.settings.sync()



        elif event.key() == QtCore.Qt.Key_Y:
            font_temp=QtGui.QFont(self.label_temp2.font().family(),self.label_temp2.font().pointSize()) 
            if self.label_temp2.font().bold()==True:
                font_temp.setBold(True)
            if self.label_temp2.font().italic()==True:
                font_temp.setItalic(True)
            font, ok = QtWidgets.QFontDialog.getFont(font_temp)
            if ok:
                fnt = font.toString().split(',')
                print(fnt)
                font = QtGui.QFont()
                font.setFamily( fnt[0] )
                font.setPointSize( int(fnt[1]) )
                if fnt[-1]=='Bold':
                    font.setBold(True)
                elif fnt[-1]=='Italic':
                    font.setItalic(True)
                elif fnt[-1]=='Bold Italic':
                    font.setItalic(True)
                    font.setBold(True)
                self.label_temp2.setFont(font)


                self.settings.setValue('label_temp2_fname', fnt[0] )
                self.settings.setValue('label_temp2_fsize', int(fnt[1]) )
                if fnt[-1]=='Bold':
                    self.settings.setValue('label_temp2_fbold', 1 )
                    self.settings.setValue('label_temp2_italic', 0)
                elif fnt[-1]=='Italic':
                    self.settings.setValue('label_temp2_fbold', 0 )
                    self.settings.setValue('label_temp2_italic', 1)
                elif fnt[-1]=='Bold Italic':
                    self.settings.setValue('label_temp2_fbold', 1 )
                    self.settings.setValue('label_temp2_italic', 1)
                self.settings.sync()



        elif event.key() == QtCore.Qt.Key_U:
            font_temp=QtGui.QFont(self.label_clock.font().family(),self.label_clock.font().pointSize()) 
            if self.label_clock.font().bold()==True:
                font_temp.setBold(True)
            if self.label_clock.font().italic()==True:
                font_temp.setItalic(True)
            font, ok = QtWidgets.QFontDialog.getFont(font_temp)
            if ok:
                fnt = font.toString().split(',')
                print(fnt)
                font = QtGui.QFont()
                font.setFamily( fnt[0] )
                font.setPointSize( int(fnt[1]) )
                if fnt[-1]=='Bold':
                    font.setBold(True)
                elif fnt[-1]=='Italic':
                    font.setItalic(True)
                elif fnt[-1]=='Bold Italic':
                    font.setItalic(True)
                    font.setBold(True)
                self.label_clock.setFont(font)


                self.settings.setValue('label_clock_fname', fnt[0] )
                self.settings.setValue('label_clock_fsize', int(fnt[1]) )
                if fnt[-1]=='Bold':
                    self.settings.setValue('label_clock_fbold', 1 )
                    self.settings.setValue('label_clock_italic', 0)
                elif fnt[-1]=='Italic':
                    self.settings.setValue('label_clock_fbold', 0 )
                    self.settings.setValue('label_clock_italic', 1)
                elif fnt[-1]=='Bold Italic':
                    self.settings.setValue('label_clock_fbold', 1 )
                    self.settings.setValue('label_clock_italic', 1)
                self.settings.sync()




        elif event.key() == QtCore.Qt.Key_I:
            
            font_name = self.settings.value('summary_font_name','Arial')
            font_size = self.settings.value('summary_font_size',50)
            font_bold_italic = int(self.settings.value('summary_font_bold_italic',0))

            font_temp=QtGui.QFont( font_name, int(font_size)) 
            if font_bold_italic ==1:
                font_temp.setBold(True)
            elif font_bold_italic==2:
                font_temp.setItalic(True)
            elif font_bold_italic==3:
                font_temp.setBold(True)
                font_temp.setItalic(True)
            font, ok = QtWidgets.QFontDialog.getFont(font_temp)
            if ok:
                fnt = font.toString().split(',')

                font_bold_italic = 0
                if fnt[-1]=='Bold':
                    font_bold_italic = 1
                elif fnt[-1]=='Italic':
                    font_bold_italic = 2
                elif fnt[-1]=='Bold Italic':
                    font_bold_italic = 3

                font = QtGui.QFont()
                font.setFamily( fnt[0] )
                font.setPointSize( int(fnt[1]) )
                if fnt[-1]=='Bold':
                    font.setBold(True)
                elif fnt[-1]=='Italic':
                    font.setItalic(True)
                elif fnt[-1]=='Bold Italic':
                    font.setItalic(True)
                    font.setBold(True)

                self.label_summary.setFont(font)
            self.settings.setValue('summary_font_name', fnt[0])
            self.settings.setValue('summary_font_size', fnt[1])
            self.settings.setValue('summary_font_bold_italic',  font_bold_italic )
#            self.settings.setValue('summary_font_italic',1 if font_bold_italic in (2,3) else 0)
            self.settings.sync()
        elif event.key() == QtCore.Qt.Key_O:
            os.startfile(app_path)
        elif event.key() == QtCore.Qt.Key_S:
            self.speed_event = self.speed_event - 0.1
            self.settings.setValue('speed_event',  self.speed_event)
            self.settings.sync()
            self.resizeEvent(self.speed_event)
            print(self.speed_event)
        elif event.key() == QtCore.Qt.Key_D:
            self.speed_event = self.speed_event + 0.1
            self.settings.setValue('speed_event',  self.speed_event)
            self.settings.sync()
            self.resizeEvent(self.speed_event)
            print(self.speed_event)


    def closeEvent(self,event):
        sys.exit(0)
        #comment


if __name__ == '__main__':
    freeze_support()

    app = QtWidgets.QApplication(sys.argv)
    s = QtWidgets.QStyleFactory.create('Windows')
    app.setStyle(s)
#    app.setOverrideCursor(Qt.BlankCursor);
    app_icon = QtGui.QIcon()
    app_icon.addFile(app_path+'icon.ico', QtCore.QSize(16,16))
    app_icon.addFile(app_path+'icon.ico', QtCore.QSize(24,24))
    app_icon.addFile(app_path+'icon.ico', QtCore.QSize(32,32))
    app_icon.addFile(app_path+'icon.ico', QtCore.QSize(48,48))
    app_icon.addFile(app_path+'icon.ico', QtCore.QSize(256,256))
    app.setWindowIcon(app_icon)


	# Set application style. Styles: WindowsVista,Windows,Fusion
    s = QtWidgets.QStyleFactory.create('Fusion')
    app.setStyle(s)

	# Set application id and icon for taskbar
    myappid = 'mycompany.myproduct.subproduct.version998' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    MainWindow1 = MainWindow_exec()
    MainWindow1.show()
    sys.exit(app.exec_())


