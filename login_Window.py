from PyQt6.QtWidgets import QWidget, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt, QPoint, pyqtSlot
import os
from PyQt6.QtGui import QMouseEvent
from ui.untitled_ui import Ui_Form
from sql import connectMySql
from main_Window import MainWindow
from argon2 import PasswordHasher


class LoginWindow(QWidget):
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.mysql = connectMySql()
        self._startPos = None
        self._endPos = None
        self._tracking = False
        self.ui.funkcjeWidget.setCurrentIndex(0)

        self.ui.zatwierdzHaslo.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.ui.UtworzBaze.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.ui.WybierzBaze.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.ui.Wyjdz.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.ui.cofnij2.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.ui.cofnij1.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.ui.utworzBaze.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        if self._tracking:
            self._endPos = a0.pos() - self._startPos
            self.move(self.pos() + self._endPos)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.MouseButton.LeftButton:
            self._startPos = QPoint(int(a0.position().x()), int(a0.position().y()))
            self._tracking = True

    def mouseReleasEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.MouseButton.LeftButton:
            self._startPos = None
            self._tracking = False
            self._endPos = None

    def wybierzPlik(self):
        PlikName = QFileDialog.getOpenFileName(self, "Wybierz bazę danych", "*.sqlite3")
        self.ui.nazwaBazy.setText(PlikName[0])
        path = PlikName[0]
        return path

    @pyqtSlot()
    def on_Wyjdz_clicked(self):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Wyjść?")
        msgBox.setIcon(QMessageBox.Icon.Question)
        msgBox.setText("Na pewno chcesz wyjść?")

        msgBox.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        odpowiedz = msgBox.exec()
        if odpowiedz == QMessageBox.StandardButton.Yes:
            self.close()
        else:
            return

    @pyqtSlot()
    def on_dokumenty_clicked(self):
        self.wybierzPlik()

    @pyqtSlot()
    def on_WybierzBaze_clicked(self):
        self.ui.funkcjeWidget.setCurrentIndex(1)

    @pyqtSlot()
    def on_UtworzBaze_clicked(self):
        self.ui.funkcjeWidget.setCurrentIndex(2)

    @pyqtSlot()
    def on_cofnij2_clicked(self):
        self.ui.funkcjeWidget.setCurrentIndex(0)
        self.ui.nazwaBazy.clear()
        self.ui.hasloDoBazy.clear()

    @pyqtSlot()
    def on_cofnij1_clicked(self):
        self.ui.funkcjeWidget.setCurrentIndex(0)
        self.ui.NazwaBazy.clear()
        self.ui.hasloBazy.clear()

    @pyqtSlot()
    def on_zatwierdzHaslo_clicked(self):
        ph = PasswordHasher()
        username = "root"
        dbname = self.ui.nazwaBazy.text().strip()
        password = self.ui.hasloDoBazy.text().strip()
        password = password + "p"

        # sprawdzenie czy cokolwiek jest wpisane
        if not dbname and not password:
            self.warning_msgBox("Wprowadź ścieżkę do bazy haseł oraz poprawne hasło")
            self.ui.hasloDoBazy.clear()
            self.ui.nazwaBazy.clear()
            return
        # sprawdzenie czy podana fraza jest sciezka
        if not set(dbname) & set("/"):
            self.warning_msgBox(
                "Wybrana ścieżka jest niepoprawna. Spróbuj podać jeszcze raz"
            )
            self.ui.nazwaBazy.clear()
            return
        # sprawdzenie czy istnieje taka sciezka do bazy danych
        try:
            result = self.mysql.check_username(username=username, dbname=dbname)

        except Exception as E:
            self.warning_msgBox(
                "Wybrana ścieżka jest niepoprawna. Spróbuj podać jeszcze raz"
            )
            self.ui.nazwaBazy.clear()
            return
        # sprawdzenie hasla
        try:
            ph.verify(result, password)
            user_id = 1
            self.main_window = MainWindow(user_id=user_id, dbname=dbname)
            self.main_window.show()
            self.ui.nazwaBazy.clear()
            self.ui.hasloBazy.clear()
            self.close()
        except Exception as E:
            self.warning_msgBox("Wprowadź poprawne hasło")
            self.ui.hasloDoBazy.clear()

    @pyqtSlot()
    def on_utworzBaze_clicked(self):
        ph = PasswordHasher()
        user_name = "root"
        user_id = 1
        db_name = str(self.ui.NazwaBazy.text().strip() + ".sqlite3")
        password_user = self.ui.hasloBazy.text().strip()
        path = f"./{db_name}"
        result = os.path.isfile(path)
        # sprawdzenie czy cos jest wpiasne
        if not password_user and db_name == ".sqlite3":
            self.warning_msgBox(content="Podaj nazwę bazy oraz hasło")
            return
        # sprawdzenie czy podano nazwe bazy
        if db_name and db_name != ".sqlite3":
            if result:
                self.warning_msgBox(
                    content="Taka baza danych już istnieje, wybierz inną nazwę"
                )
                self.ui.NazwaBazy.clear()
                return
        else:
            self.warning_msgBox(content="Podaj nazwę bazy haseł")
            return
        # sprawdzenie czy podane zostalo haslo
        if password_user:
            if not self.issecure(password_user):
                msgBox = QMessageBox(self)
                msgBox.setWindowTitle("Słabe hasło!")
                msgBox.setIcon(QMessageBox.Icon.Question)
                msgBox.setText("Czy na pewno chcesz ustawić słabe hasło?")
                msgBox.setStandardButtons(
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                odpowiedz = msgBox.exec()
                if odpowiedz == QMessageBox.StandardButton.Yes:
                    msgBox.close()
                else:
                    self.ui.hasloBazy.clear()
                    return
            #try:
                # haszowanie
                password_user = password_user + "p"
                hash = ph.hash(str(password_user))
                result = self.mysql.create_db(
                    name_db=db_name, password=hash, user_name=user_name, user_id=user_id
                )
            #except Exception as E:
            #    content = "Nieprawidłowa nazwa dla bazy haseł. Spróbuj ponownie wybierając inną"
            #    self.warning_msgBox(content=content)
            #    self.ui.NazwaBazy.clear()
            #    return

            self.warning_msgBox(content="Pomyślnie stworzono bazę haseł")
            self.ui.hasloBazy.clear()
            self.ui.NazwaBazy.clear()
            self.ui.funkcjeWidget.setCurrentIndex(0)

            result2 = self.mysql.check_config(user_id=user_id, dbname=db_name)
            if not result2:
                result3 = self.mysql.create_config(
                    user_id=user_id,
                    dbname=db_name,
                    lowercase="abcdefghijklmnopqrstuvwxyz",
                    uppercase="ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                    numbers="0123456789",
                    special_characters="!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~",
                )
                if result3:
                    content = "Wystąpił problem. Spróbuj ponownie"
                    self.warning_msgBox(content=content)
        else:
            self.warning_msgBox(content="Podaj hasło do bazy")
            return

    def warning_msgBox(self, content):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Uwaga!")
        msgBox.setText(content)
        msgBox.setStandardButtons(QMessageBox.StandardButton.Close)
        msgBox.exec()

    def issecure(self, password):
        length = False
        content = False
        if len(password) >= 8:
            length = True
        if (
            set(password) & set("abcdefghijklmnopqrstuvwxyz")
            and set(password) & set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            and set(password) & set("0123456789")
            and set(password) & set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
        ):
            content = True
        if length and content:
            return True
        return False
