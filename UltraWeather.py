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

app_path = user_data_dir()+'\\CBInfoSystem\\'
video_path = app_path+'videos\\'
config_file = app_path+r'config.ini'

if not os.path.exists(app_path):
    os.makedirs(app_path)
if not os.path.exists(video_path):
    os.makedirs(video_path)

print('###',app_path)
print('###',video_path)
print('###',config_file)

import glob

txtfiles = []
for file in glob.glob(video_path+'*'):
    file = file.replace('\\', '/')
    txtfiles.append(file)

class MainWindow_exec(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        self.settings = QtCore.QSettings(config_file, QtCore.QSettings.IniFormat)
        self.news_url = self.settings.value('news_rss_feed_link','https://www.nrk.no/rogaland/siste.rss')
        self.weather1_url = self.settings.value('weather1_url','https://www.yr.no/sted/Norge/Rogaland/Karm%C3%B8y/Kopervik/varsel.xml')
        self.weather2_url = self.settings.value('weather2_url','https://www.yr.no/sted/Norge/Rogaland/Stavanger/Stavanger/varsel.xml')
        self.settings.sync()
        
        font_name = self.settings.value('summary_font_name','Arial')
        font_size = self.settings.value('summary_font_size',50)
        font_bold = int(self.settings.value('summary_font_bold',1))
        font_italic = int(self.settings.value('summary_font_italic',1))
        is_fullscreen = self.settings.value('full_screen','Arial')

        if is_fullscreen == 'yes':
            self.showFullScreen()
        
        print(font_bold,font_italic)
        #self.label_summary.setNewFont(font_name,int(font_size),font_bold,font_italic)

        print(self.weather1_url)
        print(self.weather2_url)

        self.news_timer = QtCore.QTimer()
        self.news_timer.timeout.connect(self.call_news_update)
        self.news_timer.start(60000)

        self.weather_timer = QtCore.QTimer()
        self.weather_timer.timeout.connect(self.call_news_update)
        self.weather_timer.start(600000)

        self.mediaPlayer = QtMultimedia.QMediaPlayer(self)
        self.mediaPlayer.setVideoOutput(self.video_player)
        # fileName = "/path/of/your/local_file"
        # url = QtCore.QUrl.fromLocalFile(fileName)
        
        self.curr_media_cnt=0

        try:
            url = QtCore.QUrl(txtfiles[self.curr_media_cnt])
            self.mediaPlayer.setMedia(QtMultimedia.QMediaContent(url))
        except:
            None

        self.mediaPlayer.play()
        self.label_temp1.setText("97"+chr(176))
        self.label_temp2.setText("79"+chr(176))

        self.call_news_update()
        self.call_weather_update()

        self.label_logo.setPixmap(QtGui.QPixmap(app_path+r"logo.png"))
        self.label_logo.setScaledContents(True)
        self.mediaPlayer.mediaStatusChanged.connect(self.handleMediaStateChanged)

        self.clock_timer = QtCore.QTimer()
        self.clock_timer.timeout.connect(self.call_clock_update)
        self.clock_timer.start(1000)
        self.news_offset = 0
        self.full_news=''
        
#        self.label_summary.setPointSize(20)

        self.news_offset = int(self.settings.value('news_offset',0))
        self.resizeEvent()

        t_font_name =   self.settings.value('label_location1_fname','Arial')
        t_font_size =   int(self.settings.value('label_location1_fsize',20))
        t_font_bold =   int(self.settings.value('label_location1_fbold',0))
        t_font_italic = int(self.settings.value('label_location1_italic',0))

        font = QtGui.QFont()
        font.setFamily( t_font_name )
        font.setPointSize( t_font_size )
        if t_font_bold==True:
            font.setBold(True)
        if t_font_italic==True:
            font.setItalic(True)
        self.label_location1.setFont(font)

        t_font_name =   self.settings.value('label_temp1_fname','Arial')
        t_font_size =   int(self.settings.value('label_temp1_fsize',20))
        t_font_bold =   int(self.settings.value('label_temp1_fbold',0))
        t_font_italic = int(self.settings.value('label_temp1_italic',0))

        font = QtGui.QFont()
        font.setFamily( t_font_name )
        font.setPointSize( t_font_size )
        if t_font_bold==True:
            font.setBold(True)
        if t_font_italic==True:
            font.setItalic(True)
        self.label_temp1.setFont(font)

        t_font_name =   self.settings.value('label_location2_fname','Arial')
        t_font_size =   int(self.settings.value('label_location2_fsize',20))
        t_font_bold =   int(self.settings.value('label_location2_fbold',0))
        t_font_italic = int(self.settings.value('label_location2_italic',0))

        font = QtGui.QFont()
        font.setFamily( t_font_name )
        font.setPointSize( t_font_size )
        if t_font_bold==True:
            font.setBold(True)
        if t_font_italic==True:
            font.setItalic(True)
        self.label_location2.setFont(font)


        t_font_name =   self.settings.value('label_temp2_fname','Arial')
        t_font_size =   int(self.settings.value('label_temp2_fsize',20))
        t_font_bold =   int(self.settings.value('label_temp2_fbold',0))
        t_font_italic = int(self.settings.value('label_temp2_italic',0))

        font = QtGui.QFont()
        font.setFamily( t_font_name )
        font.setPointSize( t_font_size )
        if t_font_bold==True:
            font.setBold(True)
        if t_font_italic==True:
            font.setItalic(True)
        self.label_temp2.setFont(font)



        t_font_name =   self.settings.value('label_clock_fname','Arial')
        t_font_size =   int(self.settings.value('label_clock_fsize',20))
        t_font_bold =   int(self.settings.value('label_clock_fbold',0))
        t_font_italic = int(self.settings.value('label_clock_italic',0))

        font = QtGui.QFont()
        font.setFamily( t_font_name )
        font.setPointSize( t_font_size )
        if t_font_bold==True:
            font.setBold(True)
        if t_font_italic==True:
            font.setItalic(True)
        self.label_clock.setFont(font)

        self.uiResize()


    def uiResize(self):
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(int(self.settings.value('video_widget_h_stretch',70)))
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.video_widget.sizePolicy().hasHeightForWidth())
        self.video_widget.setSizePolicy(sizePolicy)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(int(self.settings.value('news_widget_h_stretch',70)))
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.news_widget.sizePolicy().hasHeightForWidth())
        self.news_widget.setSizePolicy(sizePolicy)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(int(self.settings.value('clock_widget_h_stretch',28)))
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.clock_widget.sizePolicy().hasHeightForWidth())
        self.clock_widget.setSizePolicy(sizePolicy)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(int(self.settings.value('weather_widget_h_stretch',28)))
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
        self.label_clock.setText( datetime.now().strftime('%I:%M:%S %p \n %d-%b-%Y') )
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
            self.news_offset = self.news_offset+1
            self.settings.setValue('news_offset',self.news_offset)
            self.settings.sync()
            self.resizeEvent()
        elif event.key() == QtCore.Qt.Key_Q:
            self.news_offset = self.news_offset-1
            self.settings.setValue('news_offset',self.news_offset)
            self.settings.sync()
            self.resizeEvent()
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
            font_bold = int(self.settings.value('summary_font_bold',True))
            font_italic = int(self.settings.value('summary_font_italic',True))

            font_temp=QtGui.QFont( font_name, int(font_size)) 
            if font_bold ==True:
                font_temp.setBold(True)
            if font_italic==True:
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
                #self.label_summary.setNewFont(fnt[0],int(fnt[1]), 1 if font_bold_italic in (1,3) else 0, 1 if font_bold_italic in (2,3) else 0)
            self.settings.setValue('summary_font_name', fnt[0])
            self.settings.setValue('summary_font_size', fnt[1])
            self.settings.setValue('summary_font_bold',  1 if font_bold_italic in (1,3) else 0)
            self.settings.setValue('summary_font_italic',1 if font_bold_italic in (2,3) else 0)
            self.settings.sync()
        elif event.key() == QtCore.Qt.Key_O:
            os.startfile(app_path)


    def closeEvent(self,event):
        sys.exit(0)

    def call_weather_update(self):
        try:
            d = feedparser.parse(self.weather1_url)['feed']
            location = d['location']['name']+', Norway'
            temp = d['temperature']['value']
            self.label_location1.setText(location)
            self.label_temp1.setText(temp+chr(176))
        except Exception as e:
            print('Weather 1 forcase error: ',e)
            self.label_location1.setText('Error')
            self.label_temp1.setText('Err')

        try:
            d = feedparser.parse(self.weather2_url)['feed']
            location = d['location']['name']+', Norway'
            temp = d['temperature']['value']
            self.label_location2.setText(location)
            self.label_temp2.setText(temp+chr(176))
        except Exception as e:
            print('Weather 2 forcase error: ',e)
            self.label_location2.setText('Error')
            self.label_temp2.setText('Err')

    def resizeEvent(self,event=None):
        print('event')
        #self.label_summary.setLen( int(self.news_widget.height()/2)+self.news_offset )
    def call_news_update(self):
        try:
            d = feedparser.parse(self.news_url)['entries'][0:9]
            
            self.full_news = ' '*self.news_widget.width()
            for x in d:
                title = x['title']
                summary= x['summary']        
                if len(summary)==0:
                    summary= title
                print('^^^^^^^',summary,title)
                
                self.full_news = self.full_news+ '    \u2022'  + summary
            self.label_summary.setText(self.full_news)
            font_name = self.settings.value('summary_font_name','Arial')
            font_size = self.settings.value('summary_font_size',50)
            font_bold = int(self.settings.value('summary_font_bold',1))
            font_italic = int(self.settings.value('summary_font_italic',1))
            
            print(font_bold,font_italic)
            #self.label_summary.setNewFont(font_name,int(font_size),font_bold,font_italic)

        except Exception as e:
            print(e)




if __name__ == '__main__':
    freeze_support()

    app = QtWidgets.QApplication(sys.argv)
    s = QtWidgets.QStyleFactory.create('Windows')
    app.setStyle(s)
#    app.setOverrideCursor(Qt.BlankCursor);
    app_icon = QtGui.QIcon()
    app_icon.addFile('icon.ico', QtCore.QSize(16,16))
    app_icon.addFile('icon.ico', QtCore.QSize(24,24))
    app_icon.addFile('icon.ico', QtCore.QSize(32,32))
    app_icon.addFile('icon.ico', QtCore.QSize(48,48))
    app_icon.addFile('icon.ico', QtCore.QSize(256,256))
    app.setWindowIcon(app_icon)


	# Set application style. Styles: WindowsVista,Windows,Fusion
    s = QtWidgets.QStyleFactory.create('Windows')
    app.setStyle(s)

	# Set application id and icon for taskbar
    myappid = 'mycompany.myproduct.subproduct.version998' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


    MainWindow1 = MainWindow_exec()
    MainWindow1.show()
    # MainWindow1.showFullScreen()
    sys.exit(app.exec_())








