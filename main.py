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

login_data = ""
minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()

def showLogin(self):
    self.close()
    self.loginWindow = LoginWindow()
    self.launcherWindow = Launcher()


class LoginWindow(QWebEngineView):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login Window Example")

        # Set the path where the refresh token is saved
        self.refresh_token_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "refresh_token.json")

        # Login with refresh token, if it exists
        if os.path.isfile(self.refresh_token_file):
            with open(self.refresh_token_file, "r", encoding="utf-8") as f:
                refresh_token = json.load(f)
                # Do the login with refresh token
                try:
                    account_informaton = minecraft_launcher_lib.microsoft_account.complete_refresh(CLIENT_ID, SECRET, REDIRECT_URL, refresh_token)
                    self.show_account_information(account_informaton)
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
            login_data = account_informaton
            # Show the login information
            #self.show_account_information(account_informaton)

    def show_account_information(self, information_dict):
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
    def getaccount_informaton():
        return account_informaton




class LoadingWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        loadinPageStyleSheet = "background-image : url(background.png);"

        self.setWindowTitle("Glacier Client - Launcher")
        self.setWindowIcon(QtGui.QIcon("logo.png"))
        self.setFixedSize(QSize(400, 600))
        self.setStyleSheet(loadinPageStyleSheet)
        self.UiComponents()
        self.show()

    def UiComponents(self):
        loginPageStyleSheet = "background-image : url(Login.png); background-color: rgba(255, 255, 255, 0);"
        button = QPushButton(self)
        button.setGeometry(50, 300, 302, 122)
        button.setStyleSheet(loginPageStyleSheet)
        button.clicked.connect(lambda: showLogin(self))


class Launcher(QMainWindow):
    def __init__(self):
        super().__init__()
        launchPageStyleSheet = "background-image : url(bg.png);"
        self.setWindowTitle("Glacier Client - Launcher")
        self.setWindowIcon(QtGui.QIcon("logo.png"))
        self.setFixedSize(QSize(800, 400))
        self.setStyleSheet(launchPageStyleSheet)
        self.UiComponents()
        self.show()

    def UiComponents(self):
        ##loginPageStyleSheet = "background-image : url(Login.png); background-color: rgba(255, 255, 255, 0);"
        button = QPushButton(self)
        button.setGeometry(50, 300, 302, 122)
        button.setStyleSheet("background-image : url(play.png);")
        button.clicked.connect(self.Play)

    def Play(self):
        print("Play")
        print(login_data)
        options = {
            "username": login_data["selectedProfile"]["name"],
            "uuid": login_data["selectedProfile"]["id"],
            "token": login_data["accessToken"]
        }
        minecraft_command = minecraft_launcher_lib.command.get_minecraft_command("1.8.8", minecraft_directory, options)
        subprocess.call(minecraft_command)


def main():
    app = QApplication(sys.argv)
    QWebEngineProfile.defaultProfile().setHttpAcceptLanguage(QLocale.system().name().split("_")[0])
    lodingWindow = LoadingWindow()
    app.exec_()



if __name__ == '__main__':
    main()

