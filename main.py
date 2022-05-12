import subprocess
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QSize, Qt, QUrl, QLocale
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
import minecraft_launcher_lib
import os
import json

CLIENT_ID = "2407b523-e1ab-4a9e-b9eb-e95ca4ea571b"
SECRET = "XpL8Q~pRHvxk5oGM8l3~_hXnQqicIJJJHi~UIbUK"
REDIRECT_URL = "https://api.glacierclient.net/login/microsoft"


minecraft_directory = os.path.join(os.path.dirname(__file__), ".minecraft")


class LoginWindow(QWebEngineView):
    global login_data
    def __init__(self, parentnew):
        super().__init__()
        global parent
        self.parent = parentnew
        self.setWindowTitle("Login Window")

        # Set the path where the refresh token is saved
        self.refresh_token_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "refresh_token.json")

        # Login with refresh token, if it exists
        if os.path.isfile(self.refresh_token_file):
            with open(self.refresh_token_file, "r", encoding="utf-8") as f:
                refresh_token = json.load(f)
                # Do the login with refresh token
                try:
                    account_informaton = minecraft_launcher_lib.microsoft_account.complete_refresh(CLIENT_ID, SECRET, REDIRECT_URL, refresh_token)
                    self.show_account_information(account_informaton, self.parent)
                    return
                # Show the window if the refresh token is invalid
                except minecraft_launcher_lib.exceptions.InvalidRefreshToken:
                    pass

        # Open the login url
        self.load(QUrl(minecraft_launcher_lib.microsoft_account.get_login_url(CLIENT_ID, REDIRECT_URL)))

        # Connects a function that is called when the url changed
        self.urlChanged.connect(self.new_url)

        self.show()

    def new_url(self, url: QUrl):
        # Check if the url contains the code
        if minecraft_launcher_lib.microsoft_account.url_contains_auth_code(url.toString()):
            # Get the code from the url
            auth_code = minecraft_launcher_lib.microsoft_account.get_auth_code_from_url(url.toString())
            # Do the login
            account_informaton = minecraft_launcher_lib.microsoft_account.complete_login(CLIENT_ID, SECRET, REDIRECT_URL, auth_code)
            self.login_data = account_informaton
            # Show the login information
            self.show_account_information(account_informaton, self.parent)

    def show_account_information(self, information_dict, parent):
        information_string = f'Username: {information_dict["name"]}<br>'
        information_string += f'UUID: {information_dict["id"]}<br>'
        information_string += f'Token: {information_dict["access_token"]}<br>'

        # Save the refresh token in a file
        with open(self.refresh_token_file, "w", encoding="utf-8") as f:
            json.dump(information_dict["refresh_token"], f, ensure_ascii=False, indent=4)

        message_box = QMessageBox()
        message_box.setWindowTitle("Account information")
        message_box.setText(information_string)
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        message_box.exec()
        parent.loginSuccess(information_dict)
        self.close()





class LoadingWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()

        loadinPageStyleSheet = "background-image : url(background.png);"

        self.setWindowTitle("Glacier Client - Launcher")
        self.setWindowIcon(QtGui.QIcon("logo.png"))
        self.setFixedSize(QSize(400, 600))
        self.setStyleSheet(loadinPageStyleSheet)
        self.UiComponents(parent)
        self.show()

    def UiComponents(self, parent):
        loginPageStyleSheet = "background-image : url(Login.png); background-color: rgba(255, 255, 255, 0);"
        button = QPushButton(self)
        button.setGeometry(50, 300, 302, 122)
        button.setStyleSheet(loginPageStyleSheet)
        button.clicked.connect(lambda: self.mclogin(parent))

    def mclogin(self, parent):
        self.close()
        parent.loginWindow = LoginWindow(parent)
        


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        global login_data
        launchPageStyleSheet = "background-image : url(bg.png);"
        self.setWindowTitle("Glacier Client - Launcher")
        self.setWindowIcon(QtGui.QIcon("logo.png"))
        self.setFixedSize(QSize(800, 400))
        self.setStyleSheet(launchPageStyleSheet)
        self.UiComponents()
        self.show()

    def UiComponents(self):
        ##loginPageStyleSheet = "background-image : url(Login.png); background-color: rgba(255, 255, 255, 0);"
        global playbutton 
        playbutton = QPushButton("play", self)
        playbutton.setGeometry(50, 300, 302, 122)
        playbutton.hide()
        #playbutton.setStyleSheet("background-image : url(play.png);")
        playbutton.clicked.connect(lambda: self.play())
        global loginbutton
        loginbutton = QPushButton("Login", self)
        loginbutton.setGeometry(50, 300, 302, 122)
        #loginbutton.setStyleSheet("background-image : url(play.png);")
        loginbutton.clicked.connect(lambda: self.showLogin())

    def play(self):
        print("Install")
        minecraft_launcher_lib.install.install_minecraft_version("1.8.9", minecraft_directory)
        print("Play")
        print(self.login_data)
        options = {
            "username": self.login_data["name"],
            "uuid": self.login_data["id"],
            "token": self.login_data["access_token"]
        }
        minecraft_command = minecraft_launcher_lib.command.get_minecraft_command("1.8.9", minecraft_directory, options)
        subprocess.call(minecraft_command)
        self.close()

    def showLogin(self):
        global lodingWindow
        lodingWindow = LoadingWindow(self)

    def loginSuccess(self, logindata):
        playbutton.show()
        loginbutton.hide()
        self.login_data = logindata


def main():
    app = QApplication(sys.argv)
    QWebEngineProfile.defaultProfile().setHttpAcceptLanguage(QLocale.system().name().split("_")[0])
    w = MainWindow()
    #lodingWindow = LoadingWindow()
    app.exec_()



if __name__ == '__main__':
    main()