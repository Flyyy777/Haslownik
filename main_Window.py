from PyQt6.QtWidgets import (
    QMessageBox,
    QMainWindow,
    QAbstractItemView,
    QTableWidgetItem,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSlot
from ui.main_ui import Ui_MainWindow
from sql import connectMySql
import random


class MainWindow(QMainWindow):
    def __init__(self, user_id, dbname):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        self.ui.spinBox.setValue(10)
        self.userid = user_id
        self.dbname = dbname
        self.mysql = connectMySql()

        self.menu_hasla = self.ui.listaHasel
        self.menu_generator = self.ui.generator
        self.menu_ustawienia = self.ui.Ustawienia1
        self.strony = self.ui.stackedWidget
        self.strony.setCurrentIndex(0)

        self.wysokie_config = self.ui.lineEdit_7
        self.niskie_config = self.ui.lineEdit_6
        self.cyfry_config = self.ui.lineEdit_5
        self.specjalne_config = self.ui.lineEdit_4

        self.widok_strony = self.ui.lineEdit_9
        self.widok_usera = self.ui.lineEdit_8
        self.tablica = self.ui.tableWidget
        self.on_Odswiez2_clicked()

        self.tablica.setRowCount(0)

        xd = QAbstractItemView.SelectionBehavior.SelectRows
        self.tablica.setSelectionBehavior(xd)
        self.tablica.setColumnWidth(0, 20)
        self.tablica.setColumnWidth(1, 20)

        for i in range(2, 5):
            self.tablica.setColumnWidth(i, 190)

        self.tworzenie_strona = self.ui.lineEdit
        self.tworzenie_usera = self.ui.lineEdit_2
        self.dlugosc = self.ui.spinBox
        self.wysokie_check = self.ui.checkBox_4
        self.niskie_check = self.ui.checkBox_3
        self.specjalne_check = self.ui.checkBox_2
        self.cyfry_check = self.ui.checkBox
        self.ukryj_check = self.ui.Ukryj

        self.ui.tableWidget.clicked.connect(self.on_table_clicked)

        self.wysokie_config.setDisabled(True)
        self.niskie_config.setDisabled(True)
        self.specjalne_config.setDisabled(True)
        self.cyfry_config.setDisabled(True)

        self.widok_usera.textChanged.connect(self.on_wyszukaj_clicked)
        self.widok_strony.textChanged.connect(self.on_wyszukaj_clicked)
        self.on_wyszukaj_clicked()  # <--- wyswietlanie calej bazy przy otwarciu
        self.wysokie_check.setChecked(True)  #
        self.niskie_check.setChecked(True)  #
        self.specjalne_check.setChecked(True)  #
        self.cyfry_check.setChecked(True)  # <------- ustawienie checkboxow na start
        self.ukryj_check.setChecked(True)
        self.on_wyszukaj_clicked()

    @pyqtSlot()
    def on_wyjdz2_clicked(self):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Zamknąć bazę?")
        msgBox.setIcon(QMessageBox.Icon.Question)
        msgBox.setText("Czy na pewno chcesz zamknąć bazę?")

        msgBox.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        odpowiedz = msgBox.exec()
        if odpowiedz == QMessageBox.StandardButton.Yes:
            from login_Window import LoginWindow

            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()

        else:
            return

    @pyqtSlot()
    def on_listaHasel_clicked(self):
        self.strony.setCurrentIndex(0)
        self.on_wyszukaj_clicked()  # <---- wyswietlanie po zmianie strony

    @pyqtSlot()
    def on_generator_clicked(self):
        self.strony.setCurrentIndex(1)

    @pyqtSlot()
    def on_Ustawienia1_clicked(self):
        self.strony.setCurrentIndex(2)

    @pyqtSlot()
    def on_odswiez_clicked(self):
        self.widok_usera.clear()
        self.widok_strony.clear()

    @pyqtSlot()
    def on_ZapiszHaslo_clicked(self):
        strona = self.tworzenie_strona.text().strip()
        user = self.tworzenie_usera.text().strip()
        passwd = self.ui.lineEdit_3.text()
        if strona and user and passwd:
            save_r = self.mysql.add_new_password(
                user_id=self.userid,
                dbname=self.dbname,
                website=strona,
                password=passwd,
                user_name=user,
            )
            if save_r:
                self.warning_msgBox("Błąd")
            else:
                self.warning_msgBox("Pomyślnie utworzono nowy wpis", type="Good")
        else:
            self.warning_msgBox("Proszę wprowadź stronę, użytkownika oraz hasło")

    @pyqtSlot()
    def on_KopiujHaslo_clicked(self):
        try:
            if self.ui.lineEdit_3.text():
                clipboard = QApplication.clipboard()
                clipboard.setText(self.ui.lineEdit_3.text())
                self.warning_msgBox("Pomyślnie skopiowano hasło", type="Good")
            else:
                self.warning_msgBox("Pole z hasłem jest puste")
        except Exception as E:
            self.warning_msgBox("Błąd")

    @pyqtSlot()
    def on_ResetHaslo_clicked(self):
        self.tworzenie_strona.clear()
        self.tworzenie_usera.clear()
        self.ui.lineEdit_3.clear()
        self.dlugosc.setValue(10)
        self.wysokie_check.setChecked(True)
        self.niskie_check.setChecked(True)
        self.specjalne_check.setChecked(True)
        self.cyfry_check.setChecked(True)

    @pyqtSlot()
    def on_GenerujHaslo_clicked(self):

        config = self.mysql.check_config(user_id=self.userid, dbname=self.dbname)
        if not config:
            self.warning_msgBox("Najpierw skonfiguruj aplikację")
            return

        flag = True
        haslo = ""
        while flag:

            haslo = self.create_password(config)
            result = self.verify(haslo, config)

            if result == True:
                flag = False

        self.ui.lineEdit_3.setText(haslo)

    def create_password(self, config):
        new_pass = ""
        chars = []
        flag = False
        pass_len = int(self.dlugosc.text())
        if self.niskie_check.isChecked() == True:
            chars.extend(config[1])
            flag = True
        if self.wysokie_check.isChecked() == True:
            chars.extend(config[2])
            flag = True
        if self.cyfry_check.isChecked() == True:
            chars.extend(config[3])
            flag = True
        if self.specjalne_check.isChecked() == True:
            chars.extend(config[4])
            flag = True

        if flag:
            for i in range(pass_len):
                new_pass += random.choice(chars)

        return new_pass

    def verify(self, haslo, config):

        check_niskie = ["x"]
        check_wysokie = ["x"]
        check_cyfry = ["x"]
        check_specjalne = ["x"]

        if self.niskie_check.isChecked() == True:
            check_niskie = set(config[1]) & set(haslo)
        if self.wysokie_check.isChecked() == True:
            check_wysokie = set(config[2]) & set(haslo)
        if self.cyfry_check.isChecked() == True:
            check_cyfry = set(config[3]) & set(haslo)
        if self.specjalne_check.isChecked() == True:
            check_specjalne = set(config[4]) & set(haslo)

        if check_niskie and check_wysokie and check_cyfry and check_specjalne:
            return True
        else:
            return False

    @pyqtSlot()
    def on_wyszukaj_clicked(self):
        result = list(self.search_data(dbname=self.dbname))
        self.tablica.setRowCount(0)

        if self.ukryj_check.isChecked() == True:
            if result:
                for i in range(len(result)):
                    data = [
                        result[i][3],
                        result[i][2],
                        "●" * len(result[i][0]),
                        result[i][1],
                    ]
                    self.show_passwords(data=data)
        else:
            if result:
                for i in range(len(result)):
                    data = [result[i][3], result[i][2], result[i][0], result[i][1]]
                    self.show_passwords(data=data)

    def show_passwords(self, data):
        count = self.tablica.rowCount() + 1
        self.tablica.setRowCount(count)
        self.tablica.setColumnCount(4)

        self.tablica.setItem(count - 1, 0, QTableWidgetItem(data[0]))
        self.tablica.setItem(count - 1, 1, QTableWidgetItem(data[1]))
        self.tablica.setItem(count - 1, 2, QTableWidgetItem(data[2]))

        id_item = QTableWidgetItem(str(data[3]))
        id_item.setData(Qt.ItemDataRole.UserRole, data[3])
        self.tablica.setItem(count - 1, 3, id_item)
        self.tablica.setColumnHidden(3, True)

    @pyqtSlot()
    def on_usun_clicked(self):
        if self.tablica.selectionModel().hasSelection():
            self.delete(dbname=self.dbname)
        else:
            self.warning_msgBox("Brak zaznaczenia wiersza")

    def delete(self, dbname):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Usunąć?")
        msgBox.setIcon(QMessageBox.Icon.Question)
        msgBox.setText("Na pewno chcesz usunąć ten wpis?")

        msgBox.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        odpowiedz = msgBox.exec()
        if odpowiedz == QMessageBox.StandardButton.Yes:
            klik = self.tablica.selectionModel().hasSelection()
            w = None
            w = self.tablica.currentRow()
            selected_items = self.tablica.selectedItems()
            id = self.tablica.item(selected_items[0].row(), 3).text()
            if klik:
                try:
                    w = self.tablica.currentRow()

                except Exception as E:
                    self.warning_msgBox(content="Wystąpił błąd, spróbuj ponownie")
            if w != None:
                self.mysql.delete_passwords(id=id, dbname=dbname)
                self.on_wyszukaj_clicked()
        else:
            return

    def search_data(self, dbname):
        website = self.widok_strony.text().strip()
        username = self.widok_usera.text().strip()
        result = self.mysql.get_passwords(
            user_id=self.userid,
            search_username=username,
            search_website=website,
            dbname=dbname,
        )
        return result

    @pyqtSlot()
    def on_Edytuj_clicked(self):  # ZMIANA
        self.wysokie_config.setEnabled(True)
        self.niskie_config.setEnabled(True)
        self.specjalne_config.setEnabled(True)
        self.cyfry_config.setEnabled(True)

    @pyqtSlot()
    def on_Odswiez2_clicked(self):
        result = self.mysql.check_config(user_id=self.userid, dbname=self.dbname)

        if result:
            self.niskie_config.setText(result[1])
            self.wysokie_config.setText(result[2])
            self.cyfry_config.setText(result[3])
            self.specjalne_config.setText(result[4])
            self.set_config_off()

    def set_config_off(self):
        self.wysokie_config.setEnabled(True)
        self.niskie_config.setEnabled(True)
        self.specjalne_config.setEnabled(True)
        self.cyfry_config.setEnabled(True)

    def copy(self, dbname, id):
        result = self.mysql.get_password(user_id=id, dbname=dbname)
        return result

    @pyqtSlot()
    def on_Kopiuj_lista_clicked(self):
        selected_items = self.tablica.selectedItems()
        try:
            if selected_items:
                id = int(self.tablica.item(selected_items[0].row(), 3).text())
                result = self.copy(dbname=self.dbname, id=id)[0]
                cb = QApplication.clipboard()
                cb.clear()
                cb.setText(str(result))
                self.warning_msgBox(
                    "Pomyślnie skopiowano hasło do schowka", type="Good"
                )
            else:
                self.warning_msgBox("Brak zaznaczenia wiersza")
        except Exception as E:
            self.warning_msgBox("Błąd")

    @pyqtSlot()
    def on_Zapisz2_clicked(self):
        lower = self.niskie_config.text().strip()
        if not lower:
            lower = self.niskie_config.placeholderText()

        upper = self.wysokie_config.text().strip()
        if not upper:
            upper = self.wysokie_config.placeholderText()

        numbers = self.cyfry_config.text().strip()
        if not numbers:
            numbers = self.cyfry_config.placeholderText()

        specials = self.specjalne_config.text().strip()
        if not specials:
            specials = self.specjalne_config.placeholderText()

        result = self.mysql.check_config(user_id=self.userid, dbname=self.dbname)
        if result:
            save_result = self.mysql.update_config(
                dbname=self.dbname,
                user_id=self.userid,
                lowercase=lower,
                uppercase=upper,
                special_characters=specials,
                numbers=numbers,
            )
        else:
            save_result = self.mysql.create_config(
                dbname=self.dbname,
                user_id=self.userid,
                lowercase=lower,
                uppercase=upper,
                special_characters=specials,
                numbers=numbers,
            )
        if save_result:
            self.warning_msgBox("Błąd")
        else:
            self.warning_msgBox("Zapisano konfiguracje")
            self.on_Odswiez2_clicked

        self.wysokie_config.setDisabled(True)
        self.niskie_config.setDisabled(True)
        self.specjalne_config.setDisabled(True)
        self.cyfry_config.setDisabled(True)
        self.tworzenie_strona.clear()
        self.tworzenie_usera.clear()
        self.ui.lineEdit_3.clear()

    def on_table_clicked(self):
        index = self.ui.tableWidget.selectionModel().currentIndex()
        value = index.sibling(index.row(), 2).data()
        self.current_select = value

    def warning_msgBox(self, content, type=None):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Uwaga!")
        msgBox.setText(content)
        msgBox.setStandardButtons(QMessageBox.StandardButton.Close)
        msgBox.exec()
