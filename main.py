import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QListWidgetItem, 
                            QLabel, QMessageBox, QLineEdit, QTableWidgetItem,
                            QTableWidget, QHeaderView)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QSize
from PyQt5.uic import loadUi
import re

from modules.database import DatabaseHandler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Загрузка интерфейса
        loadUi('views/dialog.ui', self)
        
        # Настройка окна
        self.setWindowIcon(QIcon('logo.ico'))
        self.setMinimumSize(800, 600)
        # self.logoLabel.setPixmap(QPixmap('logo.png').scaled(
        #     100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # Инициализация БД
        self.db = DatabaseHandler()
        
        # Начальное состояние
        self.stackedWidget.setCurrentIndex(0)  # Страница авторизации
        self.current_user_role = None
        self.error_style = "border: 2px solid red;"

        # Подключение сигналов
        self.btnLogin.clicked.connect(self.login)
        self.btnLogout.clicked.connect(self.logout)
        self.listWidget.itemDoubleClicked.connect(self.edit_item)
        
        # Скрываем кнопки до авторизации
        self.btnLogout.hide()
        self.btnAdd.hide()
        self.backButton.hide()
        # Подключите кнопки страницы редактирования
        self.backButton.clicked.connect(self.backButtonOpen)
        self.saveStorageButton.clicked.connect(self.save_storage_changes)
        self.savePartnerButton.clicked.connect(self.save_partner_changes)
        self.saveEmployeeButton.clicked.connect(self.save_employee_changes)
        self.btnAdd.clicked.connect(self.on_add_clicked)
        self.saveEmployeeButton.clicked.connect(self.save_employee_changes)
        # В __init__ или setupUi:
        self.deleteEmployeeButton.clicked.connect(self.delete_current_item)
        self.deleteStorageButton.clicked.connect(self.delete_current_item)
        self.deletePartnerButton.clicked.connect(self.delete_current_item)
        # Текущий редактируемый элемент
        self.current_edit_id = None
        self.backButton.hide()
    def login(self):
        """Обработка авторизации пользователя"""
        login = self.loginInput.text().strip()
        password = self.passwordInput.text().strip()
        
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return
            
        try:
            role = self.db.check_login(login, password)
            if role:
                self.current_user_role = role
                self.load_data()
                self.stackedWidget.setCurrentIndex(1)  # Основная страница
                self.btnLogout.show()
                self.btnAdd.show()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверные учетные данные")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def logout(self):
        """Выход из системы"""
        self.current_user_role = None
        self.loginInput.clear()
        self.passwordInput.clear()
        self.stackedWidget.setCurrentIndex(0)
        self.listWidget.clear()
        self.btnLogout.hide()
        self.btnAdd.hide()

    def load_data(self):
        """Загрузка данных в зависимости от роли пользователя"""
        self.listWidget.clear()
        
        try:
            if self.current_user_role == "Менеджер HR":
                employees = self.db.get_employees()
                for emp in employees:
                    self.add_employee_item(emp)
                    
            elif self.current_user_role == "Менеджер Склада":
                storage = self.db.get_storage()
                for item in storage:
                    self.add_storage_item(item)
                    
            elif self.current_user_role == "Менеджер Продаж":
                partners = self.db.get_partners()
                for partner in partners:
                    self.add_partner_item(partner)
            else:
                QMessageBox.warning(self, "Ошибка", "Неизвестная роль пользователя")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_employee_item(self, employee):
        """Добавление сотрудника в список"""
        item = QListWidgetItem()
        item.setData(Qt.UserRole, employee[0])  # Сохраняем ID сотрудника
        
        widget = QLabel(self.format_employee_html(employee))
        widget.setContentsMargins(10, 10, 10, 10)
        widget.setStyleSheet("background-color: white;")
        
        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, widget)
        item.setSizeHint(widget.sizeHint())

    def add_storage_item(self, storage):
        """Добавление товара на склад в список"""
        item = QListWidgetItem()
        item.setData(Qt.UserRole, storage[0])  # Сохраняем ID товара
        
        widget = QLabel(self.format_storage_html(storage))
        widget.setContentsMargins(10, 10, 10, 10)
        widget.setStyleSheet("background-color: white;")
        
        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, widget)
        item.setSizeHint(widget.sizeHint())

    def add_partner_item(self, partner):
        """Добавление партнера в список"""
        item = QListWidgetItem()
        item.setData(Qt.UserRole, partner[0])  # Сохраняем ИНН
        
        widget = QLabel(self.format_partner_html(partner))
        widget.setContentsMargins(10, 10, 10, 10)
        widget.setStyleSheet("background-color: white;")
        
        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, widget)
        item.setSizeHint(widget.sizeHint())

    def format_employee_html(self, employee):
        """Форматирование сотрудника для отображения"""
        return f"""
        <div style='font-family: Arial; padding: 15px; border-bottom: 1px solid #eaeaea; background-color: #f9f9f9; border-radius: 4px; margin-bottom: 8px;'>
            <div style='font-size:17pt; font-weight:600; color:#333; margin-bottom:8px;'>
                {employee[1]}  <!-- full_name -->
                <span style='font-size:12pt; color:#777; font-weight:normal; margin-left:10px;'>ID: {employee[0]}</span>
            </div>
            <div style='font-size:11pt; color:#555; line-height:1.6;'>
                <div style='margin-bottom:4px;'>
                    <span style='display:inline-block; width:100px; color:#777;'>Должность:</span>
                    <span style='font-weight:500;'>{employee[2]}</span>
                </div>
                <div style='margin-bottom:4px;'>
                    <span style='display:inline-block; width:100px; color:#777;'>Отдел:</span>
                    <span style='font-weight:500;'>{employee[3]}</span>
                </div>
                <div style='margin-bottom:4px;'>
                    <span style='display:inline-block; width:100px; color:#777;'>Контакты:</span>
                    <span style='font-weight:500;'>{employee[4]}</span>
                </div>
            </div>
        </div>
        """

    def format_storage_html(self, storage):
        """Форматирование товара на складе для отображения"""
        return f"""
        <div style='font-size:14pt;'>
            <b>{storage[1]}</b> <span style='color:#666; font-size:12pt;'>| {storage[2]}</span>
        </div>
        <div style='font-size:10pt; color:#666; margin-top:6px; line-height:1.4;'>
            <div><span style='color:#333;'>Категория:</span> {storage[3] or 'Не указана'}</div>
            <div><span style='color:#333;'>Место:</span> {storage[4] or 'Не указано'}</div>
            <div><span style='color:#333;'>Остаток:</span> {storage[5] or '0'} ед.</div>
        </div>
        <div style='margin-top:10px;'></div>
        """

    def format_partner_html(self, partner):
        """Форматирование партнера для отображения"""
        return f"""
        <div style='font-size:14pt;'>
            <b>{partner[1]}</b> <span style='color:#666; font-size:12pt;'>| ID: {partner[0]}</span>
        </div>
        <div style='font-size:10pt; color:#666; margin-top:6px; line-height:1.4;'>
            <div><span style='color:#333;'>Контакт:</span> {partner[2] or 'Не указан'}</div>
            <div><span style='color:#333;'>Телефон:</span> {partner[3] or 'Не указан'}</div>
            <div><span style='color:#333;'>Последний заказ:</span> {partner[3] or 'Нет данных'}</div>
        </div>
        <div style='margin-top:10px;'></div>
        """

    def closeEvent(self, event):
        self.db.close()
        event.accept()

    def edit_item(self, item):
        """Переход на страницу редактирования"""
        self.current_edit_id = item.data(Qt.UserRole)
        
        if self.current_user_role == "Менеджер HR":
            # Заполнение формы сотрудника
            self.current_page = self.employeePage
            employee_data = self.db.get_employee_by_id(self.current_edit_id)
            self.employeeNameEdit.setText(employee_data[1])  # ФИО
            self.positionCombo.setCurrentText(employee_data[2])  # Должность
            self.departmentCombo.setCurrentText(employee_data[3])  # Отдел
            self.contactsEdit.setText(employee_data[4])  # Контакты
            self.stackedWidget.setCurrentWidget(self.current_page)
            self.backButton.show()
            
        elif self.current_user_role == "Менеджер Склада":
            # Заполнение формы склада
            self.current_page = self.storagePage
            storage_data = self.db.get_storage_item_by_id(self.current_edit_id)
            self.productNameEdit.setText(storage_data[1])  # Название
            self.articulEdit.setText(storage_data[2])  # Артикул
            self.categoryCombo.setCurrentText(storage_data[3])  # Категория
            self.locationEdit.setText(storage_data[4])  # Место хранения
            self.quantitySpin.setValue(int(storage_data[5]))  # Количество
            self.stackedWidget.setCurrentWidget(self.current_page)
            self.backButton.show()
            
        elif self.current_user_role == "Менеджер Продаж":
            # Заполнение формы партнера
            self.current_page = self.partnerPage
            partner_data = self.db.get_partner_by_id(self.current_edit_id)
            self.companyNameEdit.setText(partner_data[1])  # Название компании
            self.directorEdit.setText(partner_data[2])  # Контактное лицо
            self.partnerPhoneEdit.setText(partner_data[3])  # Телефон
            self.stackedWidget.setCurrentWidget(self.current_page)
            self.backButton.show()

            
        
    def save_employee_changes(self):
        """Сохранение изменений сотрудника (нового или существующего)"""
        full_name = self.employeeNameEdit.text()
        position = self.positionCombo.currentText()
        department = self.departmentCombo.currentText()
        contact_info = self.contactsEdit.text()
        
        if not full_name:  # Проверка обязательных полей
            QMessageBox.warning(self, "Ошибка", "Поле 'ФИО' обязательно для заполнения")
            return
        
        if self.current_edit_id:  # Редактирование существующего
            success = self.db.update_employee(
                self.current_edit_id, full_name, position, department, contact_info
            )
            message = "Данные сотрудника обновлены"
        else:  # Добавление нового
            new_id = self.db.add_employee(full_name, position, department, contact_info)
            success = new_id is not None
            message = "Сотрудник успешно добавлен"
            if success:
                self.current_edit_id = new_id
        
        if success:
            QMessageBox.information(self, "Успех", message)
            self.load_data()  # Обновляем список
            self.stackedWidget.setCurrentWidget(self.pageMain)
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить данные")

    def save_storage_changes(self):
        """Сохранение изменений товара (нового или существующего)"""
        name = self.productNameEdit.text()
        articul = self.articulEdit.text()
        category = self.categoryCombo.currentText()
        location = self.locationEdit.text()
        quantity = self.quantitySpin.value()
        
        # Проверка обязательных полей
        if not all([name, articul, category, location]):
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны для заполнения")
            return
        
        try:
            if self.current_edit_id:  # Редактирование существующего товара
                success = self.db.update_storage_item(
                    self.current_edit_id, name, articul, category, location, quantity
                )
                message = "Данные товара обновлены"
            else:  # Добавление нового товара
                new_id = self.db.add_storage_item(name, articul, category, location, quantity)
                success = new_id is not None
                message = "Товар успешно добавлен"
                if success:
                    self.current_edit_id = new_id
            
            if success:
                QMessageBox.information(self, "Успех", message)
                self.load_data()
                self.stackedWidget.setCurrentWidget(self.pageMain)
            else:
                QMessageBox.warning(self, "Ошибка", "Ошибка при сохранении товара")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")
            print(f"Ошибка при сохранении товара: {e}")

    def save_partner_changes(self):
        """Сохранение изменений партнера (нового или существующего)"""
        name = self.companyNameEdit.text()
        contact_person = self.directorEdit.text()
        phone = self.partnerPhoneEdit.text()
        
        # Проверка обязательных полей
        if not all([name, contact_person, phone]):
            QMessageBox.warning(self, "Ошибка", 
                            "Поля 'Название компании', 'Контактное лицо' и 'Телефон' обязательны")
            return
        
        try:
            if self.current_edit_id:  # Редактирование существующего партнера
                success = self.db.update_partner(
                    self.current_edit_id, name, contact_person, phone
                )
                message = "Данные партнера обновлены"
            else:  # Добавление нового партнера
                new_id = self.db.add_partner(name, contact_person, phone)
                success = new_id is not None
                message = "Партнер успешно добавлен"
                if success:
                    self.current_edit_id = new_id
            
            if success:
                QMessageBox.information(self, "Успех", message)
                self.load_data()
                self.stackedWidget.setCurrentWidget(self.pageMain)
            else:
                QMessageBox.warning(self, "Ошибка", "Ошибка при сохранении партнера")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")
            print(f"Ошибка при сохранении партнера: {e}")

    def backButtonOpen(self):
        self.backButton.hide()
        self.stackedWidget.setCurrentWidget(self.pageMain)

    def on_add_clicked(self):
        """Обработчик нажатия кнопки Добавить"""
        if self.current_user_role == "Менеджер HR":
            self.open_add_employee_form()
        elif self.current_user_role == "Менеджер Склада":
            self.open_add_storage_form()
        elif self.current_user_role == "Менеджер Продаж":
            self.open_add_partner_form()

    def open_add_employee_form(self):
        """Открытие формы добавления сотрудника"""
        # Очищаем поля формы
        self.employeeNameEdit.clear()
        self.positionCombo.setCurrentIndex(0)
        self.departmentCombo.setCurrentIndex(0)
        self.contactsEdit.clear()
        
        # Устанавливаем флаг, что это новое добавление
        self.current_edit_id = None
        self.current_page = self.employeePage
        self.stackedWidget.setCurrentWidget(self.employeePage)
        self.backButton.show()

    def open_add_storage_form(self):
        """Открытие формы добавления товара на склад"""
        # Очищаем поля формы
        self.productNameEdit.clear()
        self.articulEdit.clear()
        self.categoryCombo.setCurrentIndex(0)
        self.locationEdit.clear()
        self.quantitySpin.setValue(0)
        
        # Устанавливаем флаг, что это новое добавление
        self.current_edit_id = None
        self.current_page = self.storagePage
        self.stackedWidget.setCurrentWidget(self.storagePage)
        self.backButton.show()

    def open_add_partner_form(self):
        """Открытие формы добавления партнера"""
        # Очищаем поля формы
        self.companyNameEdit.clear()
        self.directorEdit.clear()
        self.partnerPhoneEdit.clear()
        
        # Устанавливаем флаг, что это новое добавление
        self.current_edit_id = None
        self.current_page = self.partnerPage
        self.stackedWidget.setCurrentWidget(self.partnerPage)
        self.backButton.show()
    def delete_current_item(self):
        """Удаление текущего выбранного элемента"""
        if not hasattr(self, 'current_edit_id') or not self.current_edit_id:
            QMessageBox.warning(self, "Ошибка", "Не выбран элемент для удаления")
            return
        
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите удалить этот элемент?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        try:
            if self.current_user_role == "Менеджер HR":
                success = self.db.delete_employee(self.current_edit_id)
                message = "Сотрудник удален"
            elif self.current_user_role == "Менеджер Склада":
                success = self.db.delete_storage_item(self.current_edit_id)
                message = "Товар удален"
            elif self.current_user_role == "Менеджер Продаж":
                success = self.db.delete_partner(self.current_edit_id)
                message = "Партнер удален"
            else:
                QMessageBox.warning(self, "Ошибка", "Неизвестная роль пользователя")
                return
            
            if success:
                QMessageBox.information(self, "Успех", message)
                self.load_data()  # Обновляем список
                self.stackedWidget.setCurrentWidget(self.pageMain)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить элемент")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")
            print(f"Ошибка при удалении: {e}")
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont('Segoe UI', 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())