import sqlite3

class DatabaseHandler:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()
        
    def connect(self):
        """Подключение к базе данных и инициализация"""
        try:
            self.conn = sqlite3.connect('uchet.db')
            self.cursor = self.conn.cursor()
            
            # Инициализация типов партнеров
            # self.cursor.execute("SELECT COUNT(*) FROM Partners_type")
            # if self.cursor.fetchone()[0] == 0:
            #     types = ['ЗАО', 'ООО', 'ПАО', 'ОАО']
            #     for t in types:
            #         self.cursor.execute("INSERT INTO Partners_type (Tip) VALUES (?)", (t,))
            #     self.conn.commit()
                
        except sqlite3.Error as e:
            raise Exception(f"Ошибка подключения к БД: {str(e)}")

    def check_login(self, username, password):
        """Проверка учетных данных и возврат роли пользователя"""
        try:
            self.cursor.execute("""
                SELECT position 
                FROM Employee 
                WHERE login = ? AND password = ?
            """, (username, password))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Ошибка авторизации: {str(e)}")
            return None

    def get_employees(self):
        """Получение списка сотрудников"""
        try:
            self.cursor.execute("""
                SELECT 
                    employee_id, 
                    full_name, 
                    position, 
                    department, 
                    contact_info
                FROM Employee 
            """)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Ошибка загрузки сотрудников: {str(e)}")

    def get_storage(self):
        """Получение информации о складе"""
        try:
            self.cursor.execute("""
                SELECT 
                    s.storage_id,
                    p.name, 
                    p.articul, 
                    p.category, 
                    s.location, 
                    s.quantity
                FROM Storage s
                JOIN Products p ON s.product_id = p.product_id
            """)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Ошибка загрузки склада: {str(e)}")

    def get_partners(self):
        """Получение списка всех партнеров"""
        try:
            self.cursor.execute("""
            SELECT c.client_id, c.name, c.contact_info, 
                   c.phone
            FROM Clients c
        """)
            # ORDER BY p.Rejting DESC
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Ошибка загрузки партнеров: {str(e)}")
        
    def get_partner_by_id(self, client_id):
        """Получение данных партнера по ID"""
        self.cursor.execute("""
            SELECT 
                client_id,
                name, 
                contact_info, 
                phone
            FROM Clients 
            WHERE client_id = ?
        """, (client_id,))
        return self.cursor.fetchone()

    def get_employee_by_id(self, employee_id):
        """Получение данных сотрудника по ID"""
        self.cursor.execute("""
            SELECT 
                employee_id,
                full_name, 
                position, 
                department,
                contact_info
            FROM Employee 
            WHERE employee_id = ?
        """, (employee_id,))
        return self.cursor.fetchone()

    def get_storage_item_by_id(self, product_id):
        """Получение данных товара на складе по ID"""
        self.cursor.execute("""
            SELECT 
                p.product_id,
                p.name,
                p.articul,
                p.category,
                s.location,
                s.quantity
            FROM Products p
            JOIN Storage s ON p.product_id = s.product_id
            WHERE p.product_id = ?
        """, (product_id,))
        return self.cursor.fetchone()
    
    def update_partner(self, client_id, name, contact_person, phone):
        """Обновление данных партнера"""
        try:
            self.cursor.execute("""
                UPDATE Clients 
                SET 
                    name = ?,
                    contact_info = ?,
                    phone = ?
                WHERE client_id = ?
            """, (name, contact_person, phone, client_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении партнера: {e}")
            self.conn.rollback()
            return False

    def update_employee(self, employee_id, full_name, position, department, contact_info):
        """Обновление данных сотрудника"""
        try:
            self.cursor.execute("""
                UPDATE Employee 
                SET 
                    full_name = ?,
                    position = ?,
                    department = ?,
                    contact_info = ?
                WHERE employee_id = ?
            """, (full_name, position, department, contact_info, employee_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении сотрудника: {e}")
            self.conn.rollback()
            return False

    def update_storage_item(self, product_id, name, articul, category, location, quantity):
        """Обновление данных товара на складе"""
        try:
            # Обновляем данные в таблице Products
            self.cursor.execute("""
                UPDATE Products 
                SET 
                    name = ?,
                    articul = ?,
                    category = ?
                WHERE product_id = ?
            """, (name, articul, category, product_id))
            
            # Обновляем данные в таблице Storage
            self.cursor.execute("""
                UPDATE Storage 
                SET 
                    location = ?,
                    quantity = ?
                WHERE product_id = ?
            """, (location, quantity, product_id))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении товара: {e}")
            self.conn.rollback()
            return False
        
    def add_employee(self, full_name, position, department, contact_info):
        """Добавление нового сотрудника в базу данных"""
        try:
            self.cursor.execute("""
                INSERT INTO Employee (full_name, position, department, contact_info)
                VALUES (?, ?, ?, ?)
            """, (full_name, position, department, contact_info))
            self.conn.commit()
            return self.cursor.lastrowid  # Возвращаем ID нового сотрудника
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении сотрудника: {e}")
            self.conn.rollback()
            return None
    
        # В класс DB
    def add_storage_item(self, name, articul, category, location, quantity):
        """Добавление нового товара на склад"""
        try:
            # Сначала добавляем в Products
            self.cursor.execute("""
                INSERT INTO Products (name, articul, category)
                VALUES (?, ?, ?)
            """, (name, articul, category))
            product_id = self.cursor.lastrowid
            
            # Затем добавляем в Storage
            self.cursor.execute("""
                INSERT INTO Storage (product_id, location, quantity)
                VALUES (?, ?, ?)
            """, (product_id, location, quantity))
            
            self.conn.commit()
            return product_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении товара: {e}")
            self.conn.rollback()
            return None

    def add_partner(self, name, contact_person, phone):
        """Добавление нового партнера"""
        try:
            self.cursor.execute("""
                INSERT INTO Clients (name, contact_info, phone)
                VALUES (?, ?, ?)
            """, (name, contact_person, phone))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении партнера: {e}")
            self.conn.rollback()
            return None
    def delete_employee(self, employee_id):
        """Удаление сотрудника по ID"""
        try:
            self.cursor.execute("DELETE FROM Employee WHERE employee_id = ?", (employee_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении сотрудника: {e}")
            self.conn.rollback()
            return False

    def delete_storage_item(self, product_id):
        """Удаление товара по ID"""
        try:
            # Сначала удаляем из Storage
            self.cursor.execute("DELETE FROM Storage WHERE product_id = ?", (product_id,))
            # Затем удаляем из Products
            self.cursor.execute("DELETE FROM Products WHERE product_id = ?", (product_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении товара: {e}")
            self.conn.rollback()
            return False

    def delete_partner(self, client_id):
        """Удаление партнера по ID"""
        try:
            self.cursor.execute("DELETE FROM Clients WHERE client_id = ?", (client_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении партнера: {e}")
            self.conn.rollback()
            return False
    def close(self):
        """Закрытие соединения с БД"""
        if self.conn:
            self.conn.close()