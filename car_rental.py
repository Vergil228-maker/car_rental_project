import json
import os
from datetime import datetime, date
from typing import List, Dict, Optional

class Car:
    def __init__(self, id: int, brand: str, model: str, year: int, daily_price: float, available: bool = True):
        self.id = id
        self.brand = brand
        self.model = model
        self.year = year
        self.daily_price = daily_price
        self.available = available
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'daily_price': self.daily_price,
            'available': self.available
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Car':
        return cls(
            id=data['id'],
            brand=data['brand'],
            model=data['model'],
            year=data['year'],
            daily_price=data['daily_price'],
            available=data['available']
        )
    
    def __str__(self) -> str:
        return f"{self.brand} {self.model} ({self.year}) - {self.daily_price} руб/день"

class Rental:
    def __init__(self, id: int, car_id: int, username: str, start_date: str, end_date: str, total_price: float, status: str = "active"):
        self.id = id
        self.car_id = car_id
        self.username = username
        self.start_date = start_date
        self.end_date = end_date
        self.total_price = total_price
        self.status = status
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'car_id': self.car_id,
            'username': self.username,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'total_price': self.total_price,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Rental':
        return cls(
            id=data['id'],
            car_id=data['car_id'],
            username=data['username'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            total_price=data['total_price'],
            status=data.get('status', 'active')
        )
    
    def __str__(self) -> str:
        return f"Аренда #{self.id}: с {self.start_date} по {self.end_date} - {self.total_price} руб."

class User:
    def __init__(self, username: str, password: str, role: str = "customer"):
        self.username = username
        self.password = password
        self.role = role
    
    def to_dict(self) -> Dict:
        return {
            'username': self.username,
            'password': self.password,
            'role': self.role
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        return cls(
            username=data['username'],
            password=data['password'],
            role=data['role']
        )

class CarRentalSystem:
    def __init__(self):
        self.data_dir = "data"
        self.cars_file = os.path.join(self.data_dir, "cars.json")
        self.rentals_file = os.path.join(self.data_dir, "rentals.json")
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.current_user: Optional[User] = None
        
        self._initialize_data()
        self._load_data()
    
    def _initialize_data(self):
        """Создает директорию и файлы данных, если они не существуют"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        if not os.path.exists(self.cars_file):
            with open(self.cars_file, 'w') as f:
                json.dump([], f)
        
        if not os.path.exists(self.rentals_file):
            with open(self.rentals_file, 'w') as f:
                json.dump([], f)
        
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump([], f)
    
    def _load_data(self):
        """Загружает данные из файлов"""
        with open(self.cars_file, 'r') as f:
            self.cars = [Car.from_dict(car) for car in json.load(f)]
        
        with open(self.rentals_file, 'r') as f:
            self.rentals = [Rental.from_dict(rental) for rental in json.load(f)]
        
        with open(self.users_file, 'r') as f:
            self.users = [User.from_dict(user) for user in json.load(f)]
    
    def _save_cars(self):
        """Сохраняет данные об автомобилях"""
        with open(self.cars_file, 'w') as f:
            json.dump([car.to_dict() for car in self.cars], f, indent=2)
    
    def _save_rentals(self):
        """Сохраняет данные об арендах"""
        with open(self.rentals_file, 'w') as f:
            json.dump([rental.to_dict() for rental in self.rentals], f, indent=2)
    
    def _save_users(self):
        """Сохраняет данные о пользователях"""
        with open(self.users_file, 'w') as f:
            json.dump([user.to_dict() for user in self.users], f, indent=2)
    
    def register_user(self, username: str, password: str) -> bool:
        """Регистрация нового пользователя"""
        if any(user.username == username for user in self.users):
            return False
        
        new_user = User(username, password)
        self.users.append(new_user)
        self._save_users()
        return True
    
    def login(self, username: str, password: str) -> bool:
        """Аутентификация пользователя"""
        for user in self.users:
            if user.username == username and user.password == password:
                self.current_user = user
                return True
        return False
    
    def logout(self):
        """Выход из системы"""
        self.current_user = None
    
    def add_car(self, brand: str, model: str, year: int, daily_price: float) -> bool:
        """Добавление нового автомобиля (для администратора)"""
        if not self.current_user or self.current_user.role != "admin":
            return False
        
        new_id = max((car.id for car in self.cars), default=0) + 1
        new_car = Car(new_id, brand, model, year, daily_price)
        self.cars.append(new_car)
        self._save_cars()
        return True
    
    def get_available_cars(self) -> List[Car]:
        """Получение списка доступных автомобилей"""
        today = date.today().isoformat()
        rented_car_ids = {
            rental.car_id for rental in self.rentals
            if rental.status == "active" and rental.end_date >= today
        }
        
        return [car for car in self.cars if car.id not in rented_car_ids]
    
    def rent_car(self, car_id: int, start_date: str, end_date: str) -> Optional[float]:
        """Аренда автомобиля"""
        if not self.current_user:
            return None
        
        try:
            car = next(car for car in self.cars if car.id == car_id)
        except StopIteration:
            return None
        
        # Проверка доступности автомобиля
        available_cars = self.get_available_cars()
        if car not in available_cars:
            return None
        
        # Проверка дат
        try:
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)
        except ValueError:
            return None
        
        if start < date.today():
            return None
        
        if end <= start:
            return None
        
        # Расчет стоимости
        days = (end - start).days
        total_price = days * car.daily_price
        
        # Создание аренды
        new_id = max((rental.id for rental in self.rentals), default=0) + 1
        new_rental = Rental(
            id=new_id,
            car_id=car.id,
            username=self.current_user.username,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price
        )
        
        self.rentals.append(new_rental)
        self._save_rentals()
        
        return total_price
    
    def get_user_rentals(self) -> List[Rental]:
        """Получение аренд текущего пользователя"""
        if not self.current_user:
            return []
        
        return [
            rental for rental in self.rentals
            if rental.username == self.current_user.username
        ]
    
    def cancel_rental(self, rental_id: int) -> bool:
        """Отмена аренды"""
        if not self.current_user:
            return False
        
        for rental in self.rentals:
            if rental.id == rental_id and rental.username == self.current_user.username:
                rental.status = "cancelled"
                self._save_rentals()
                return True
        
        return False

class ConsoleInterface:
    def __init__(self):
        self.system = CarRentalSystem()
        self._initialize_admin()
    
    def _initialize_admin(self):
        """Создает администратора, если его нет"""
        if not any(user.username == "admin" for user in self.system.users):
            admin = User("admin", "admin123", "admin")
            self.system.users.append(admin)
            self.system._save_users()
    
    def _display_menu(self):
        """Отображает главное меню"""
        print("\n=== Система проката автомобилей ===")
        print("1. Войти в систему")
        print("2. Зарегистрироваться")
        print("3. Просмотреть доступные автомобили")
        
        if self.system.current_user:
            print("\n=== Пользовательское меню ===")
            print("4. Арендовать автомобиль")
            print("5. Мои аренды")
            print("6. Отменить аренду")
            print("7. Выйти из системы")
            
            if self.system.current_user.role == "admin":
                print("\n=== Администраторское меню ===")
                print("8. Добавить автомобиль")
                print("9. Просмотреть все аренды")
        
        print("0. Выход из программы")
    
    def _clear_screen(self):
        """Очищает экран консоли"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def run(self):
        """Запускает главный цикл приложения"""
        while True:
            self._clear_screen()
            self._display_menu()
            
            choice = input("\nВыберите действие: ")
            
            if choice == "0":
                print("Выход из программы...")
                break
            
            elif choice == "1":
                self._login()
            
            elif choice == "2":
                self._register()
            
            elif choice == "3":
                self._show_available_cars()
            
            elif choice == "4" and self.system.current_user:
                self._rent_car()
            
            elif choice == "5" and self.system.current_user:
                self._show_user_rentals()
            
            elif choice == "6" and self.system.current_user:
                self._cancel_rental()
            
            elif choice == "7" and self.system.current_user:
                self.system.logout()
                print("Вы вышли из системы.")
                input("Нажмите Enter для продолжения...")
            
            elif choice == "8" and self.system.current_user and self.system.current_user.role == "admin":
                self._add_car()
            
            elif choice == "9" and self.system.current_user and self.system.current_user.role == "admin":
                self._show_all_rentals()
            
            else:
                print("Неверный выбор или действие недоступно.")
                input("Нажмите Enter для продолжения...")
    
    def _login(self):
        """Обрабатывает вход пользователя"""
        self._clear_screen()
        print("=== Вход в систему ===")
        username = input("Имя пользователя: ")
        password = input("Пароль: ")
        
        if self.system.login(username, password):
            print(f"Добро пожаловать, {username}!")
        else:
            print("Неверное имя пользователя или пароль.")
        
        input("Нажмите Enter для продолжения...")
    
    def _register(self):
        """Обрабатывает регистрацию пользователя"""
        self._clear_screen()
        print("=== Регистрация ===")
        username = input("Имя пользователя: ")
        password = input("Пароль: ")
        
        if self.system.register_user(username, password):
            print("Регистрация успешна. Теперь вы можете войти в систему.")
        else:
            print("Пользователь с таким именем уже существует.")
        
        input("Нажмите Enter для продолжения...")
    
    def _show_available_cars(self):
        """Показывает доступные автомобили"""
        self._clear_screen()
        print("=== Доступные автомобили ===")
        cars = self.system.get_available_cars()
        
        if not cars:
            print("Нет доступных автомобилей.")
        else:
            for car in cars:
                print(f"\nID: {car.id}")
                print(f"Марка: {car.brand}")
                print(f"Модель: {car.model}")
                print(f"Год выпуска: {car.year}")
                print(f"Цена за день: {car.daily_price} руб.")
        
        input("\nНажмите Enter для продолжения...")
    
    def _rent_car(self):
        """Обрабатывает аренду автомобиля"""
        self._clear_screen()
        print("=== Аренда автомобиля ===")
        cars = self.system.get_available_cars()
        
        if not cars:
            print("Нет доступных автомобилей для аренды.")
            input("Нажмите Enter для продолжения...")
            return
        
        print("\nДоступные автомобили:")
        for car in cars:
            print(f"{car.id}. {car.brand} {car.model} ({car.year}) - {car.daily_price} руб/день")
        
        try:
            car_id = int(input("\nВведите ID автомобиля: "))
            start_date = input("Дата начала (ГГГГ-ММ-ДД): ")
            end_date = input("Дата окончания (ГГГГ-ММ-ДД): ")
            
            total_price = self.system.rent_car(car_id, start_date, end_date)
            
            if total_price is not None:
                print(f"\nАренда оформлена успешно!")
                print(f"Общая стоимость: {total_price:.2f} руб.")
            else:
                print("\nОшибка при оформлении аренды. Проверьте введенные данные.")
        
        except ValueError:
            print("\nОшибка ввода. Пожалуйста, введите корректные данные.")
        
        input("\nНажмите Enter для продолжения...")
    
    def _show_user_rentals(self):
        """Показывает аренды текущего пользователя"""
        self._clear_screen()
        print("=== Мои аренды ===")
        rentals = self.system.get_user_rentals()
        
        if not rentals:
            print("У вас нет активных аренд.")
        else:
            for rental in rentals:
                car = next(car for car in self.system.cars if car.id == rental.car_id)
                print(f"\nАренда #{rental.id}")
                print(f"Автомобиль: {car.brand} {car.model}")
                print(f"Период: с {rental.start_date} по {rental.end_date}")
                print(f"Стоимость: {rental.total_price:.2f} руб.")
                print(f"Статус: {rental.status}")
        
        input("\nНажмите Enter для продолжения...")


