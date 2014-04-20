#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from lxml import etree
import ConfigParser
import wmi
from socket_handler import *
import loggers
from structures import *
from wx.lib.embeddedimage import PyEmbeddedImage

rlc_icon = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAABK1J"
    "REFUWIXNl01vE1cUhh87M4wT27Ed2wHTaWInkRLh0EW8wKgKXbCoUKKKUhZIILHgJ/A7WLBA"
    "YhGWsGKRbZFYNFKQJWIordEkBEFT20kUW9jjr/HHeNzFuC4udkha2vCu5tw559xnZs69544F"
    "aHGEsh7l5J8FgPC+EYlEiEajSJLU5bS+vk4sFuPdu3cABINBzp49i67rxGIxkslkz+TDw8NE"
    "o1FmZ2cBqNVqxGIx4vF4b4BoNMrNmzdxuVxdiR4+fMjr1687AFNTU1y/fp1qtcrOzk5fAJfL"
    "xcLCAteuXQNAVVVu3brVH8Bms+F2u0kmk6ytrVGpVDqBCwsLTExMsLa2hiiKOJ1ORFFEFMUP"
    "JvZ4PEQiEcLhMIVCgQcPHgCgaRqKonT5Ch9EA/F4nNu3b7O3twfAhQsXuHHjBoqikEqlej7t"
    "+/L5fFy8eJEzZ86wtLTEnTt3ADAMg3K5/HGA8fFxzp8/j6qqnYTPnj1DURQKhcJHAQRBwO12"
    "4/V6aTQa7O7u9vftNRiJRJicnKTZbALw+PFj7t+/j6Io5PN5wuHwRyEOqp4Au7u7JBIJNE0D"
    "IJfLMT09jWEYJBKJTzZ5X4B4PM7du3fJZDIAzM/Pc/nyZRRFIZvN/vcAuVyOzc3Nzrebm5tD"
    "lmWKxSI2m63j5/P5mJ+fx+PxAJDP51lfX6dQKPD06VN0XWdkZIRLly4BUK/X2djYYHNzc3+A"
    "gyoYDHL16lWKxSIAGxsb3Lt3j9XVVZaXl3n58iWLi4tcuXIFgFKpxNLSUn+AN2/e8OjRIxKJ"
    "BLVarTOeTqdZWVkhmUyiqipWq5UnT56Qy+W6gLLZLNVqlVqtxtbWFpqmcerUKaampjoAf1+G"
    "Ft7rhoFAAFmWyWazpFIpGo0GYL5qWZapVCqk02lEUUSWZZxOZ1eycrlMKpXq7JiSJCHLMqOj"
    "owDouk4qlWJnZ6c3wGFlt9vx+/04HA7A3OkymcyB9oo/9a9qwO/3c+7cOYLBIGAu35WVlX8O"
    "YBs8zqD9JBbLAAC1ahatvI1h1HsGOxwOQqEQp0+f7tgvXrw41EN0AYz45/gy9D0DwiAAe9s/"
    "kXy7TK36add+XwC7c5zjJ7/hmGS245qWYTv5Y+e+02LBJwjYLBYAxgSBofZ1Tw1YEIYlrPZ2"
    "x2y10NU6RumvN3qoGgiJIt/a7ciCGSY5HDiE/imsgyJDs34Gp70AGPUm5ee7VH7NHAxAGLIz"
    "dCKAtWra4xb42mplxmqe5Eo2G3sDA1T6AUgDSGMuHHMnAGhWGtTTReCAAK7QBKHwIrrVrOpA"
    "OoW0sQ4Fdb+wQ2lfAHsggDQTxWI3NyTvz885tp3uC3BsAEadEPS2BzxgkXq6HgzgsDoxDD/M"
    "wXcB01YlWP0Cfvm/ALwOmJkBedK0ky3IGPsDfF7/Bc1mjXpdpdUy24OhFWiWi2CYNVDVNIq6"
    "jqrrAJQbDUqaRrndjq1NDVXTGTLdUWlRNZrorXo7n06r0ewC6GpGbu9XeP0RrFazclrDGsZI"
    "CUQDAF9mj/Gt33C0J2y43VTGxmi0DySSoTKiv8LRNA8yJQSet1y8wuyaLd2g+jZP/fdCb4Cj"
    "0JHXwJED/AHCo/cJTXmxVAAAAABJRU5ErkJggg==")


class RLCGui(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=title,
                          pos=wx.DefaultPosition, size=wx.Size(300, 200),
                          style=wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.TAB_TRAVERSAL)

        self.version = "0.9.5"
        self.SetIcon(rlc_icon.GetIcon())

        self.logger = None
        self.thread = None

        self.config = {
            'game_host': '127.0.0.1',
            'game_port': 20777,
            'name': None,
            'local_enabled': False,
            'forwarding_enabled': False,
            'forwarding_host': 'localhost',
            'forwarding_port': '20776',
            'game_running': False,
            'game_config_missing': False
        }

        self.app_config_path = 'config.ini'
        self.app_config = ConfigParser.SafeConfigParser()
        self.app_config.read(self.app_config_path)

        try:
            self.config['name'] = self.app_config.get('general', 'name')
            self.config['local_enabled'] = self.app_config.get('local', 'enabled') == 'true'
            self.config['forwarding_enabled'] = self.app_config.get('forwarding', 'enabled') == 'true'
            self.config['forwarding_host'] = self.app_config.get('forwarding', 'host')
            self.config['forwarding_port'] = self.app_config.get('forwarding', 'port')
        except ConfigParser.NoSectionError:
            self.create_app_config()

        self.game_config_path = os.path.join(
            os.path.expandvars("%userprofile%"), 
            "Documents\\my games\\formulaone2013\\hardwaresettings\\hardware_settings_config.xml"
        )
        if os.path.isfile(self.game_config_path):
            tree = etree.parse(self.game_config_path)
            self.motion = tree.xpath('motion')[0]
            self.config['game_enabled'] = (self.motion.get('enabled') == 'true' and self.motion.get('extradata') == '3')

            self.config['game_port'] = self.motion.get('port')
            self.config['game_host'] = self.motion.get('ip')
        else:
            self.config['game_config_missing'] = True

        processes = wmi.WMI().Win32_Process(name='F1_2013.exe')
        self.config['game_running'] = (len(processes) != 0)

        # Start Menu bar
        menu_bar = wx.MenuBar()

        # Start File
        menu_file = wx.Menu()
        
        file_settings = wx.MenuItem(menu_file, wx.ID_SETUP, '&Settings')
        menu_file.AppendItem(file_settings)
        self.Bind(wx.EVT_MENU, self.show_settings, file_settings)

        menu_file.AppendSeparator()

        file_exit = wx.MenuItem(menu_file, wx.ID_EXIT, "&Exit")
        menu_file.AppendItem(file_exit)
        self.Bind(wx.EVT_MENU, self.quit_app, file_exit)

        menu_bar.Append(menu_file, "&File")
        # End File

        # Start Help
        menu_help = wx.Menu()
        
        help_instructions = wx.MenuItem(menu_help, wx.ID_HELP_PROCEDURES, "&Instructions")
        menu_help.AppendItem(help_instructions)
        self.Bind(wx.EVT_MENU, self.menu_instructions, help_instructions)

        menu_help.AppendSeparator()
        
        help_about = wx.MenuItem(menu_help, wx.ID_ABOUT, "&About")
        menu_help.AppendItem(help_about)
        self.Bind(wx.EVT_MENU, self.menu_about, help_about)
        
        menu_bar.Append(menu_help, "&Help")
        # End Help

        self.SetMenuBar(menu_bar)
        # End Menu bar

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Buttons
        buttons = wx.BoxSizer(wx.HORIZONTAL)

        self.settings_button = wx.Button(self, wx.ID_ANY, u"Se&ttings", wx.DefaultPosition, wx.DefaultSize, 0)
        self.settings_button.Bind(wx.EVT_BUTTON, self.show_settings)
        buttons.Add(self.settings_button, 0, wx.ALL, 5)

        self.log_button = wx.Button(self, wx.ID_ANY, u"Show &Log", wx.DefaultPosition, wx.DefaultSize, 0)
        self.log_button.Bind(wx.EVT_BUTTON, self.show_log)
        buttons.Add(self.log_button, 0, wx.ALL, 5)

        self.start_button = wx.Button(self, wx.ID_ANY, u"&Start", wx.DefaultPosition, wx.DefaultSize, 0)
        self.start_button.Bind(wx.EVT_BUTTON, self.start_logging)
        if not self.config['game_enabled']:
            self.start_button.Disable()
        buttons.Add(self.start_button, 0, wx.ALL, 5)

        sizer.Add(buttons, 1, wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.race_options = []
        self.races = self.get_races()
        for race in self.races:
            self.race_options.append(race[1])
        race_chooser = wx.BoxSizer(wx.HORIZONTAL)
        race_chooser_label = wx.StaticText(self, wx.ID_ANY, u"Race:", wx.DefaultPosition, wx.DefaultSize, 0)
        race_chooser_label.Wrap(-1)
        race_chooser.Add(race_chooser_label, 0, wx.ALL, 5)

        self.race_combo = PromptingComboBox(self, u"No Race", self.race_options, style=wx.CB_SORT)
        race_chooser.Add(self.race_combo, 1, wx.ALL, 0)

        refresh_image = wx.Image("refresh.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        refresh_size = (refresh_image.GetWidth() + 10, refresh_image.GetHeight() + 10)
        race_refresh = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=refresh_image, size=refresh_size)
        race_refresh.Bind(wx.EVT_BUTTON, self.refresh_race_list)
        race_chooser.Add(race_refresh, 0, wx.LEFT, 5)
        sizer.Add(race_chooser, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 5)

        font = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        self.session_id = wx.StaticText(self, wx.ID_ANY, u"Session:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.session_id.SetFont(font)
        sizer.Add(self.session_id, flag=wx.LEFT, border=5)

        self.last_lap = wx.StaticText(self, wx.ID_ANY, u"Last Lap:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.last_lap.SetFont(font)
        sizer.Add(self.last_lap, flag=wx.LEFT, border=5)

        self.SetSizer(sizer)
        self.Layout()
        self.status_bar = self.CreateStatusBar(1, wx.ST_SIZEGRIP, wx.ID_ANY)

        self.Show()

    def refresh_race_list(self, event):
        self.race_options = []
        races = self.get_races()
        for race in races:
            self.race_options.append(race[1])
        self.race_combo.SetItems(self.race_options)
        self.race_combo.SetLabelText(u'No Race')
        self.status_bar.SetStatusText(u'Race list refreshed.')

    def get_races(self):
        try:
            req = requests.get('https://racingleaguecharts.com/races/without_sessions.json', verify=False)
            if req.status_code == 200:
                return req.json()
            else:
                raise requests.exceptions.RequestException
        except requests.exceptions.RequestException:
            return []


    def show_settings(self, event):
        settings = SettingsDialog(None)
        settings.update_ui(self.config)
        result = settings.ShowModal()
        if result == wx.ID_OK:
            self.save_config(settings)
        settings.Destroy()

    def show_log(self, event):
        log = ShowLogDialog(None)
        if self.logger:
            log.set_content(self.logger.log)
        log.ShowModal()
        log.Destroy()

    def create_app_config(self):
        if not self.app_config.has_section('general'):
            self.app_config.add_section('general')
        if not self.app_config.has_option('general', 'name'):
            self.app_config.set('general', 'name', '')

        if not self.app_config.has_section('local'):
            self.app_config.add_section('local')
        if not self.app_config.has_option('local', 'enabled'):
            self.app_config.set('local', 'enabled', 'false')

        if not self.app_config.has_section('forwarding'):
            self.app_config.add_section('forwarding')
        if not self.app_config.has_option('forwarding', 'enabled'):
            self.app_config.set('forwarding', 'enabled', 'false')
        if not self.app_config.has_option('forwarding', 'host'):
            self.app_config.set('forwarding', 'host', 'localhost')
        if not self.app_config.has_option('forwarding', 'port'):
            self.app_config.set('forwarding', 'port', '20776')

        with open(self.app_config_path, 'w') as config:
            self.app_config.write(config)

    def save_config(self, settings):
        self.config['game_enabled'] = settings.enable_general.IsChecked()
        self.config['game_port'] = settings.general_port_text.GetValue()
        self.config['name'] = settings.general_name_combo.GetValue()

        self.config['local_enabled'] = settings.enable_local_mode.IsChecked()

        self.config['forwarding_enabled'] = settings.enable_forwarding.IsChecked()
        self.config['forwarding_host'] = settings.forwarding_host_text.GetValue()
        self.config['forwarding_port'] = settings.forwarding_port_text.GetValue()

        self.motion.set('enabled', str(self.config['game_enabled']).lower())
        self.motion.set('ip', self.config['game_host'])
        self.motion.set('port', self.config['game_port'])

        with open(self.game_config_path, 'w') as config:
            config.write(etree.tostring(self.motion.getparent(), encoding='utf-8', xml_declaration=True))

        self.app_config.set('general', 'name', self.config['name'])
        self.app_config.set('local', 'enabled', str(self.config['local_enabled']).lower())
        self.app_config.set('forwarding', 'enabled', str(self.config['forwarding_enabled']).lower())
        self.app_config.set('forwarding', 'host', self.config['forwarding_host'])
        self.app_config.set('forwarding', 'port', self.config['forwarding_port'])

        with open(self.app_config_path, 'w') as config:
            self.app_config.write(config)

        return True

    def start_logging(self, event):
        if self.thread is not None:
            self.thread.close()
            self.start_button.SetLabel('&Start')
            self.thread = None
        else:
            if not self.config['game_enabled']:
                wx.MessageBox('You must check the enable box to use the logger', 'Info', wx.OK | wx.ICON_INFORMATION)
                self.show_settings(event)
                return False
            if self.config['name'] == "":
                wx.MessageBox('You must enter a name to start the logger', 'Info', wx.OK | wx.ICON_INFORMATION)
                self.show_settings(event)
                return False

            try:
                self.race_id = next(race for race in self.races if race[1] == self.race_combo.GetValue())[0]
            except:
                self.race_id = None

            self.start_button.SetLabel('&Stop')
            self.logger = loggers.RacingLeagueCharts(self)
            session = Session(self.logger)
            self.thread = SocketThread(session, self.config['game_port'], self.status_bar,
                                       self.config['forwarding_host'], self.config['forwarding_port']
            )

    def quit_app(self, event):
        if self.thread is not None:
            self.thread.close()
        self.Destroy()

    # Menu items
    def menu_about(self, event):
        description = "An F1 telemetry logging application."

        info = wx.AboutDialogInfo()
        info.SetName('Racing League Charts Logger')
        info.SetVersion(self.version)
        info.SetWebSite('https://racingleaguecharts.com')
        info.SetDescription(description)
        
        #info.SetIcon(wx.Icon('logo', wx.BITMAP_TYPE_PNG))
        #info.SetCopyright('')
        #info.SetLicence(licence)
        #info.AddDeveloper('Lordp')
        
        wx.AboutBox(info)

    def menu_instructions(self, event):
        frame = Instructions(None, -1, 'Instructions')
        frame.Show(True)

if __name__ == '__main__':

    app = wx.App()
    RLCGui(None, title='Racing League Charts Logger')
    app.MainLoop()