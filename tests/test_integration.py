import os
import shutil
import pytest
from car_rental import CarRentalSystem, User
from datetime import date, timedelta

@pytest.fixture
def system():
    # Создание изолированной тестовой среды
    test_data_dir = "test_data"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir)

    system = CarRentalSystem()
    system.data_dir = test_data_dir
    system.cars_file = os.path.join(test_data_dir, "cars.json")
    system.rentals_file = os.path.join(test_data_dir, "rentals.json")
    system.users_file = os.path.join(test_data_dir, "users.json")

    system._initialize_data()
    system._load_data()

    yield system

    shutil.rmtree(test_data_dir)

def test_full_rental_flow(system):
    # Регистрация пользователя
    assert system.register_user("user1", "pass1") == True
    assert system.login("user1", "pass1") == True

    # Добавление машины админом
    admin = User("admin", "admin123", "admin")
    system.users.append(admin)
    system._save_users()
    system.login("admin", "admin123")
    assert system.add_car("BMW", "X5", 2022, 5000) == True

    # Вход обычного пользователя
    assert system.login("user1", "pass1") == True

    # Получение доступных машин
    cars = system.get_available_cars()
    assert len(cars) == 1
    car_id = cars[0].id

    # Аренда автомобиля
    today = date.today()
    start = today + timedelta(days=1)
    end = start + timedelta(days=3)
    total = system.rent_car(car_id, start.isoformat(), end.isoformat())

    assert total == 3 * cars[0].daily_price

    # Проверка, что аренда создана
    rentals = system.get_user_rentals()
    assert len(rentals) == 1
    assert rentals[0].car_id == car_id

    # Отмена аренды
    rental_id = rentals[0].id
    assert system.cancel_rental(rental_id) == True

    # Проверка, что статус стал "cancelled"
    rentals = system.get_user_rentals()
    assert rentals[0].status == "cancelled"
