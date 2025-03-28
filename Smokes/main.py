import kivy
kivy.require('2.3.1')
import configparser
from kivy.logger import Logger,LOG_LEVELS
# import os
import datetime as dt
from datetime import datetime,timedelta
# from kivy.app import App
# from kivy.uix.label import Label
# from kivy.uix.gridlayout import GridLayout
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.textinput import TextInput
# from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from functions import *
from kivy.uix.behaviors import FocusBehavior
from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.theming import ThemeManager,ThemableBehavior
import configparser
import pyotp
import time 
from kivy.clock import Clock

is_login = False
user = ''
access = ''
Logger.setLevel(LOG_LEVELS['debug'])
Logger.info('App started')
Logger.debug('App started debug')
hostOnline=''
storeOnline=''

config=configparser.ConfigParser()
config.read('smokes.ini')
store=config['store']['storeNumber']
key=config['otp']['key']
totp=pyotp.TOTP(key)
unlocked = False


class CustomMDTextField(MDTextField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text_color_normal = (0, 0, 0, 1)  # White text color
        self.text_color_focus = (1, 1, 1, 1)

class LoginScreen(FocusBehavior,Screen):
   
        def __init__(self, **kwargs):
            
            super(LoginScreen, self).__init__(**kwargs)
            Logger.info('Login screen initialized')
            layout = MDGridLayout(cols=2, row_force_default=True, row_default_height=50, spacing=20, padding=20)
            with layout.canvas.before:
                Color(0.1, 0.1, 0.1, 0.2)  # Dark gray color
                self.rect = Rectangle(size=self.size, pos=self.pos)
            layout.bind(size=self._update_rect, pos=self._update_rect)
          
            layout.add_widget(MDLabel(text='User Name',
                # size_hint=(.25, .10), 
                halign="center",
                theme_text_color='Primary',
                font_size='20sp'
                ))
            self.username = CustomMDTextField(multiline=False,input_filter='int',mode="fill",
                line_color_focus=(0, 1, 0, 1),  # Green line when focused
                line_color_normal=(0, 0, 1, 1),  # Blue line when not focused
                )
            
            self.username.fill_color=(0.9, 0.9, 0.9, 1)
            self.username.fill_color_focus=(0,0,1,1) 
            self.username.fill_color_normal=(0.9, 0.9, 0.9, 1)# Light gray background color
            self.username.bind(on_text_validate=self.on_enter_username)
            layout.add_widget(self.username)
            self.username.focus = True

            layout.add_widget(MDLabel(text='Password',
                
                halign="center",
                
                font_size='20sp'
                ))
            
            self.password = CustomMDTextField(password=True, multiline=False,input_filter='int', mode="fill",
                line_color_focus=(0, 1, 0, 1),  # Green line when focused
                line_color_normal=(0, 0, 1, 1),  # Blue line when not focused
                # size_hint=(.10, .5),
                # pos_hint={"center_x": 0.5, "center_y": 0.35},
                )
            self.password.fill_color=(0.9, 0.9, 0.9, 1)  # Light gray background color
           
            self.password.fill_color_focus=(0,0,1,1) 
            self.password.fill_color_normal=(0.9, 0.9, 0.9, 1)# Light gray background color
            self.password.bind(on_text_validate=self.on_enter_password)
            layout.add_widget(self.password)

            btn1 = MDRaisedButton(text='Login',
                size_hint=(0.5,None),
                
                height=50)
            btn1.bind(on_press=self.btn_pressed)
            layout.add_widget(btn1)
            self.add_widget(layout)
            
        
            

        def btn_pressed(self, instance):
            global is_login, user
            print('Username:', self.username.text, 'Password:', self.password.text)
            is_login = Login(self.username.text, self.password.text)
            user = self.username.text
            print(is_login)
            now=dt.datetime.now()
            if is_login:
                
                global access
                access = get_access(self.username.text)
                print('access:', access)

                Logger.info(f'User {self.username.text} logged in @ {now}')
                self.username.text = ''
                self.password.text = ''
                self.manager.current = 'menu'
                
            else:
                
                print('Login failed')
                Logger.error(f'Login failed for user {self.username.text} @ {now}')
                self.username.text = ''
                self.password.text = ''
                self.add_widget(MDLabel(text='Username or Password is incorrect',color=(1,0,0,1)))
                self.username.focus = True

        def on_enter_username(self, instance):
            self.password.focus = True
        def on_enter_password(self, instance):
            self.btn_pressed(self)
        def _update_rect(self, instance, value):
            self.rect.size = instance.size
            self.rect.pos = instance.pos

class StoreOffline(Screen):
    def __init__(self, **kwargs):
        super(StoreOffline, self).__init__(**kwargs)
        self.add_widget(MDLabel(text='Store database is offline Please restart App and try again if Problem presist call Support!!',color=(1,0,0,1),font_size='20sp'))

    
        
            
            

class MainScreen(Screen):
    now = datetime.now().date()

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.layout = MDFloatLayout(size=(600, 600))
        with self.layout.canvas.before:
            Color(0.1, 0.1, 0.1, 0.2)  # Dark gray color
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.layout.bind(size=self._update_rect, pos=self._update_rect)

        self.welcome_label = MDLabel(
            text='Welcome to Smokes!',
            size_hint=(.6, .1),
            pos_hint={'center_x': 0.68, 'y': 0.0},
            font_size='20sp'
        )
        self.layout.add_widget(self.welcome_label)
        self.add_widget(self.layout)

        self.logoutBtn = MDRaisedButton(
            text='Logout',
            size_hint=(.25, .10),
            pos_hint={'center_x': 0.5, 'y': 0.1}
        )
        self.logoutBtn.bind(on_press=self.logoutBtn_pressed)
        self.layout.add_widget(self.logoutBtn)

        self.enterCounts = MDRaisedButton(
            text='Enter Counts',
            size_hint=(.25, .10),
            pos_hint={'center_x': 0.5, 'y': 0.9}
        )
        self.enterCounts.bind(on_press=self.enterCounts_pressed)
        self.layout.add_widget(self.enterCounts)

        self.otpBtn = MDRaisedButton(
            text='Submit Code',
            size_hint=(.25, .10),
            pos_hint={'center_x': 0.5, 'y': 0.79}
        )
        self.otpBtn.bind(on_press=self.otpBtn_pressed)

        self.otpCode = CustomMDTextField(
            multiline=False,
            input_filter='int',
            size_hint=(.25, .10),
            pos_hint={'center_x': 0.5, 'y': 0.9},
            mode="fill",
            line_color_focus=(0, 1, 0, 1),  # Green line when focused
            line_color_normal=(0, 0, 1, 1),  # Blue line when not focused
        )
        self.otpCode.fill_color = (0.9, 0.9, 0.9, 1)  # Light gray background color
        self.otpCode.fill_color_focus = (0, 0, 1, 1)
        self.otpCode.fill_color_normal = (0.9, 0.9, 0.9, 1)
        self.otpCode.bind(on_text_validate=self.on_enter_otp)
        self.layout.add_widget(self.otpBtn)
        self.layout.add_widget(self.otpCode)

    def reset(self):
        """Reset logic and variables for MainScreen."""
        global unlocked
        calculations = Calculations(store)
        self.last_count_date = calculations.get_last_count_date()
        self.current_date = datetime.now().date()
        print('Last count date:', self.last_count_date)
        print('Current date:', self.current_date)
        print('Unlocked:', unlocked)
        self.yesterday = self.current_date - timedelta(days=1)

        # Reset UI and logic based on the unlocked value
        if self.last_count_date < self.current_date and unlocked is False and self.last_count_date != self.yesterday:
            self.layout.clear_widgets()
            self.layout.add_widget(MDLabel(text='Last count was on: {}'.format(self.last_count_date), color=(1, 0, 0, 1), font_size='40sp', pos_hint={'center_x': 0.87, 'y': -.1}, theme_text_color="Custom",text_color=(1, 0, 0, 1)))
            self.layout.add_widget(MDLabel(text='Current Business day is {}'.format(self.current_date), color=(0, 1, 0, 1), font_size='40sp', pos_hint={'center_x': 0.85, 'y': -.15}, theme_text_color="Custom",text_color=(0, 0, 1, 1)))
            self.layout.add_widget(self.welcome_label)
            self.layout.add_widget(MDLabel(
                text='Last count was on: {}'.format(self.last_count_date),
                theme_text_color="Custom",
                text_color=(1, 0, 0, 1),
                font_size='20sp',
                pos_hint={'center_x': 0.5, 'y': 0.8},
            ))
            self.layout.add_widget(MDLabel(text='System has detected that previous days counts are missing and is LOCKED', theme_text_color="Custom",text_color=(1, 0, 0, 1), font_size='20sp', pos_hint={'center_x': 0.7, 'y': 0.16}))
            self.layout.add_widget(MDLabel(text='Contact your DM for  instructions and to unlock system ', theme_text_color="Custom",text_color=(1, 0, 0, 1), font_size='20sp', pos_hint={'center_x': 0.8, 'y': 0.125}))
            self.layout.add_widget(MDLabel(text='Please enter the authorization code to unlock system ', theme_text_color="Custom",text_color=(1, 0, 0, 1), font_size='20sp', pos_hint={'center_x': 0.76, 'y': 0.25}))
            self.otpCode.focus = True
            self.layout.add_widget(self.otpBtn)
            self.layout.add_widget(self.otpCode)
        else:
            self.layout.clear_widgets()
            self.layout.add_widget(self.welcome_label)
            self.layout.add_widget(self.enterCounts)
            self.layout.add_widget(MDLabel(text='Current Business day is {}'.format(self.last_count_date),theme_text_color="Custom", text_color=(0, 0, 1, 1), font_size='20sp', pos_hint={'center_x': 0.85, 'y': 0.16}))
            self.layout.add_widget(MDLabel(text='Last count was on: {}'.format(self.last_count_date), theme_text_color="Custom", text_color=(1, 0, 0, 1), font_size='20sp', pos_hint={'center_x': 0.85, 'y': 0.1}))
            self.enterCounts.focus = True
    def on_pre_enter(self):
        """Reinitialize logic when the screen is about to be displayed."""
        self.reset()

    def logoutBtn_pressed(self, instance):
        self.manager.current = 'login'

    def enterCounts_pressed(self, instance):
        self.manager.current = 'enterCounts'

    def on_enter_otp(self, instance):
        self.otpBtn_pressed(self)

    def otpBtn_pressed(self, instance):
        otpValue = self.otpCode.text
        print('OTP:', otpValue)
        if totp.verify(otpValue):
            global unlocked
            unlocked = True
            self.manager.current = 'enterCounts'
        else:
            self.layout.add_widget(MDLabel(
                text='Invalid OTP',
                theme_text_color="Custom",
                text_color=(1, 0, 0, 1),
                font_size='20sp',
                pos_hint={'center_x': 0.5, 'y': 0.7}
                ))

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
           
class EnterCounts(Screen):
    def __init__(self, **kwargs):
        super(EnterCounts, self).__init__(**kwargs)
        self.businessDay = None
        self.layout = MDGridLayout(cols=2, row_force_default=True, row_default_height=50, spacing=20, padding=20)
        with self.layout.canvas.before:
            Color(0.1, 0.1, 0.1, 0.2)  # Dark gray color
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.layout.bind(size=self._update_rect, pos=self._update_rect)
        self.counts =CustomMDTextField(multiline=False,input_filter='int',mode="fill")
        self.counts.bind(on_text_validate=self.on_enter_counts)
        self.counts.fill_color=(0.9, 0.9, 0.9, 1)  # Light gray background color
        self.counts.fill_color_focus=(0,0,1,1)
        self.counts.fill_color_normal=(0.9, 0.9, 0.9, 1)# Light gray background color
        self.counts.bind(on_text_validate=self.on_enter_counts)
        self.counts.bind(text=self.enforce_character_limit)
        self.shift = CustomMDTextField(multiline=False,input_filter=self.shift_filter,mode="fill",max_text_length=1,
            line_color_focus=(0, 1, 0, 1),  # Green line when focused
            line_color_normal=(0, 0, 1, 1),  # Blue line when not focused
            )
        self.shift.fill_color=(0.9, 0.9, 0.9, 1)  # Light gray background color
        self.shift.fill_color_focus=(0,0,1,1)
        self.shift.fill_color_normal=(0.9, 0.9, 0.9, 1)
        self.shift.bind(on_text_validate=self.on_enter_shift)
        self.shift.bind(text=self.enforce_character_limit)
        self.comments = CustomMDTextField(multiline=True,mode="fill",max_text_length=150,
            line_color_focus=(0, 1, 0, 1),  # Green line when focused
            line_color_normal=(0, 0, 1, 1),  # Blue line when not focused
            )
        self.comments.fill_color=(0.9, 0.9, 0.9, 1)  # Light gray background color
        self.comments.fill_color_focus=(0,0,1,1)
        self.comments.fill_color_normal=(0.9, 0.9, 0.9, 1)
        self.comments.bind(on_text_validate=self.on_enter_counts)
        self.comments.bind(text=self.enforce_character_limit) 
        self.btn1 = MDRaisedButton(text='Submit')
        self.btn1.bind(on_press=self.btn_pressed)
        self.btn2 = MDRaisedButton(text='Main Menu')
        self.btn2.bind(on_press=self.btn2_pressed)
        self.add_widget(self.layout)
        
        

    def reset(self):
        
        self.layout.clear_widgets()
        self.layout.add_widget(MDLabel(text='Enter Counts'))
        self.layout.add_widget(self.counts)
        self.layout.add_widget(MDLabel(text='Enter Shift 1 - 4'))
        self.layout.add_widget(self.shift)
        self.layout.add_widget(MDLabel(text='Enter Comments'))
        self.layout.add_widget(self.comments)
        self.layout.add_widget(self.btn1)
        self.layout.add_widget(MDLabel())
        self.layout.add_widget(self.btn2, index=0)
        calculations = Calculations(store)
        self.last_count_date = calculations.get_last_count_date()
        self.current_date = datetime.now().date()
        print('Last count date:', self.last_count_date)
        print('Current date:', self.current_date)
        self.last_count=calculations.get_last_count()
        if self.last_count_date < self.current_date:
            self.nextDay = self.last_count_date + timedelta(days=1)
            self.bussinessDay = self.nextDay
            self.add_widget(MDLabel(text='Entering Counts for : {}'.format(self.nextDay), theme_text_color="Custom", text_color=(1, 0, 0, 1),halign="center"))
        else :
            self.add_widget(MDLabel(text='Entering Counts for : {}'.format(self.current_date), theme_text_color="Custom", text_color=(0, 1, 0, 1),halign="center"))            
            self.bussinessDay = self.current_date
        self.counts.focus = True

    def shift_filter(self, value, from_undo):
        value=int(value)
        print(value)
        print(type(value))
        
        if value in (1, 2,3,4):
            return str(value)
            
        return ''
    
    def enforce_character_limit(self, instance, value):
        print(instance,value)
        if instance == self.comments:
            # Limit the number of characters to 150
            if len(value) > 150:
                instance.text = value[:150]
        elif instance == self.counts:
            # Limit the number of characters to 4
            if len(value) > 4:
                instance.text = value[:4]
        elif instance == self.shift:
            # Limit the number of characters to 1
            if len(value) > 1:
                instance.text = value[:1]
        

    def on_enter_counts(self, instance):
        self.shift.focus = True
    def on_enter_shift(self, instance):
       self.comments.focus = True
    def on_enter_comments(self, instance):  
        self.btn_pressed(self)
    def btn_pressed(self, instance):
        
        print('Counts:', self.counts.text)
        print('Shift:', self.shift.text)
        print('BusinessDay:',self.bussinessDay)
        print('Comments:', self.comments.text)
        print('User:', user)
        print('Access:', access)
        now = dt.datetime.now()
        update=UpdateSmokes(store)
        update.InsertCounts(self.counts.text, self.bussinessDay,self.shift.text, self.last_count[0][5],self.comments.text,user)
                           
        Logger.info(f'Counts entered: {self.counts.text} for shift {self.shift.text} by user {user} @ {now}')
        if self.current_date == self.bussinessDay:
            Logger.info(f'Counts entered for {self.current_date}')
            self.manager.current = 'menu'
        else:
            Logger.info(f'Counts entered for {self.bussinessDay}')
            self.manager.current = 'menu'
        self.counts.text = ''
        self.shift.text = ''
        self.comments.text = ''

    def btn2_pressed(self, instance):
        self.manager.current = 'menu'

    
    def on_pre_enter(self):
        
        self.reset()
        Clock.schedule_once(self.set_focus, 0.1)  # Delay to ensure the screen is fully loaded

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def set_focus(self, *args):
        self.counts.focus = True
    

class SmokesApp(MDApp):


    def build(self):
        Logger.info('Building app')
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='menu'))
        sm.add_widget(StoreOffline(name='storeoffline'))
        sm.add_widget(EnterCounts(name='enterCounts'))
        sm.username=''
        sm.is_login = False
        print(is_login)
        storedbcheck=checkStoreDb()
        print(storedbcheck)
        print('hostOnline:', hostOnline)
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Red"
        md_bg_color=(0.1, 0.1, 0.1, 1)  # Dark gray
        if not self.is_log_in():
            if storedbcheck is False:
                sm.current = 'storeoffline'
            else:
                sm.current = 'login'
        else:
            sm.current = 'menu'
        return sm
        
    def is_log_in(self):
        print('login yes or no',is_login)
        return is_login
    

if __name__ == '__main__':
   
    SmokesApp().run()