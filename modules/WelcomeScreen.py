#  widget - это имя, присваиваемое компоненту пользовательского интерфейса,
#  с которым пользователь может взаимодействовать 
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (    
    QDialog, # это базовый класс диалогового окна
    QTableWidget
)
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QPushButton, QStackedWidget
from PyQt5.uic import loadUi # загрузка интерфейса, созданного в Qt Creator

import sqlite3
from datetime import date

from modules.Manager import Manager
from modules.database import showSelect


class WelcomeScreen(QDialog):
    """
    Это класс окна приветствия.
    """
    def __init__(self):
        """
        Это конструктор класса
        """
        super(WelcomeScreen, self).__init__()
        loadUi("views/welcomescreen.ui", self)  # загружаем интерфейс.
        self.model = showSelect()
        self.AvtorButton.clicked.connect(self.sign_out)
        self.AvtorButton.hide()
        self.stackedWidget.currentChanged.connect(self.hiddenButton)  
        self.PasswordField.setEchoMode(QLineEdit.Password)  # скрываем пароль
        self.SignInButton.clicked.connect(self.check_user)  # нажатие на кнопку и вызов функции

        self.insert_button.clicked.connect(self.insert)  # нажатие на кнопку и вызов функци
        self.edit_button.clicked.connect(self.update)
        self.delete_button.clicked.connect(self.delete)

        # Шаг 1: Изменяем подключение сигналов, чтобы передавать кнопку в метод open_table
        self.Clients.clicked.connect(lambda: self.open_table(self.Clients))
        self.Employees.clicked.connect(lambda: self.open_table(self.Employees))
        self.Materials.clicked.connect(lambda: self.open_table(self.Materials))
        self.Orders.clicked.connect(lambda: self.open_table(self.Orders))
        self.Production.clicked.connect(lambda: self.open_table(self.Production))
        self.Products.clicked.connect(lambda: self.open_table(self.Products))
        self.Recipes.clicked.connect(lambda: self.open_table(self.Recipes))
        self.Shipments.clicked.connect(lambda: self.open_table(self.Shipments))
        self.Storage.clicked.connect(lambda: self.open_table(self.Storage))
        self.Suppliers.clicked.connect(lambda: self.open_table(self.Suppliers))

        self.pages = {
    'Менеджер Логистики': {
        'table':['Shipments', 'Orders', 'Storage'],
      
    },
    'Менеджер Продаж': {
        'table':['Clients', 'Orders', 'Products'],
    },
    'Менеджер Производства': {
        'table':['Production', 'Materials', 'Equipment', 'Recipes'],
    },
    'Менеджер Склада': {
        'table':['Storage', 'Products', 'Shipments'],
    },
    'Менеджер Закупок': {
        'table':[ 'Suppliers', 'Materials', 'Orders'],
    },
    'Служба Поддержки Клиентов': {
        'table':['Clients', 'Orders', 'Shipments'],
    },
    'Менеджер HR': {
        'table':['Employees'],
    },
}   

        self.button_table_map = {
            self.Clients: 'Clients',
            self.Employees: 'Employees',
            self.Materials: 'Materials',
            self.Orders: 'Orders',
            self.Production: 'Production',
            self.Products: 'Products',
            self.Recipes: 'Recipes',
            self.Shipments: 'Shipments',
            self.Storage: 'Storage',
            self.Suppliers: 'Suppliers'
        }


    def hiddenButton(self):
        if self.stackedWidget.currentWidget() == self.Avtorisation:  
            self.AvtorButton.hide()
        else:
            self.AvtorButton.show()
        
        
    def sign_out(self):
        self.stackedWidget.setCurrentWidget(self.Avtorisation)
        
    def signupfunction(self): # создаем функцию регистрации        
        user = self.LoginField.text() # создаем пользователя и получаем из поля ввода логина введенный текст
        password = self.PasswordField.text() # создаем пароль и получаем из поля ввода пароля введенный текст
        return user, password # выводит логин и пароль       
    
    def hide_label(self, count):
        line_edits = []
        # Проходим по всем элементам в QVBoxLayout
        for i in range(self.verticalLayout_3.count()):
            item = self.verticalLayout_3.itemAt(i)
            widget = item.widget()
            widget.hide()
            
            # Проверяем, является ли виджет QLineEdit
            if isinstance(widget, QLineEdit):
                line_edits.append(widget)
        # Теперь line_edits содержит список всех QLineEdit в QVBoxLayout
        self.lines = line_edits[count:]
        for i in line_edits[count:]:
            i.show()

    def hide_buttons(self, role):
        button_edits = []
        allowed_tables = self.pages.get(role, {}).get('table', [])
        
        # Проходим по всем элементам в QVBoxLayout
        for i in range(self.horizontalLayout_4.count()):
            item = self.horizontalLayout_4.itemAt(i)
            widget = item.widget()
            
            # Проверяем, является ли виджет QPushButton
            if isinstance(widget, QPushButton):
                button_edits.append(widget)
        
        # Скрываем все кнопки
        for button in button_edits:
            button.hide()
        
        # Показываем только те кнопки, которые соответствуют разрешенным таблицам
        for button in button_edits:
            button_text = button.objectName()
            if button_text in allowed_tables:
                button.show()

    def check_user(self):
        try:
            user, password = self.signupfunction()
            print(user, password)
            if len(user)==0 or len(password)==0: # если пользователь оставил пустые поля
                self.ErrorField.setText("Заполните все поля") # выводим ошибку в поле
            else:
                self.ErrorField.setText(" ") # выводим ошибку в поле
                
                self.typeUser = self.model.execute_query('SELECT position FROM Employees WHERE login=(?) and password=(?)', user, password, fetch_one=True) # получаем тип пользователя, логин и пароль которого был введен
                self.typeUser = self.typeUser[0] # получает только один тип пользователя
                print(self.typeUser)
                if self.typeUser == None:
                    self.ErrorField.setText("Пользователь с такими данными не найден")
                else:    
                    self.stackedWidget.setCurrentWidget(self.selectTable)

                self.hide_buttons(self.typeUser)
        except Exception as e:
            print(f"An error occurred while executing the query: {e}")
            return None
    def open_table(self, button):
        # Шаг 3: Получаем имя таблицы из кнопки
        self.table_name = self.button_table_map[button] if button in self.button_table_map else ''
        
        # Проверяем, есть ли доступ к таблице для текущего типа пользователя
        accessible_tables = self.pages[self.typeUser]['table'] if self.typeUser in self.pages and 'table' in self.pages[self.typeUser] else []
        if self.table_name in accessible_tables:
            
            # Открываем таблицу с указанным запросом
            cols = self.model.select_data(self.tableMasteraZayavki, self.table_name)
            self.stackedWidget.setCurrentWidget(self.user)

            self.hide_label(11 - cols)
        else:
            # Обрабатываем случай, когда у пользователя нет доступа к таблице
            print(f"Доступ запрещен к таблице: {self.table_name}")
    def insert(self):
        values = [i.text() for i in self.lines]

        self.model.insert_data(self.table_name, values)
        cols = self.model.select_data(self.tableMasteraZayavki, self.table_name)
    
    def update(self):
        values = [i.text() for i in self.lines]

        self.model.update_data(self.table_name, values)
        cols = self.model.select_data(self.tableMasteraZayavki, self.table_name)

    def delete(self):
        values = [i.text() for i in self.lines]

        self.model.delete_data(self.table_name, values)
        cols = self.model.select_data(self.tableMasteraZayavki, self.table_name)