
import os
import shutil
import pytest
from car_rental import CarRentalSystem, User

@pytest.fixture
def test_system():
    # Подготовка: создаем отдельную папку data для теста
    test_data_dir = "test_data"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir)

    # Создаем копию системы с переопределением путей к данным
    system = CarRentalSystem()
    system.data_dir = test_data_dir
    system.cars_file = os.path.join(test_data_dir, "cars.json")
    system.rentals_file = os.path.join(test_data_dir, "rentals.json")
    system.users_file = os.path.join(test_data_dir, "users.json")

    system._initialize_data()
    system._load_data()

    yield system

    # Очистка после теста
    shutil.rmtree(test_data_dir)

def test_user_registration_and_login(test_system):
    assert test_system.register_user("testuser", "testpass") == True
    assert test_system.login("testuser", "testpass") == True
    assert test_system.current_user.username == "testuser"

def test_add_car_as_admin(test_system):
    # Добавим админа вручную
    admin = User("admin", "admin123", "admin")
    test_system.users.append(admin)
    test_system._save_users()

    assert test_system.login("admin", "admin123") == True
    result = test_system.add_car("Toyota", "Camry", 2020, 3000)
    assert result == True
    assert len(test_system.cars) == 1
    assert test_system.cars[0].brand == "Toyota"

def test_get_available_cars(test_system):
    # Добавим админа и машину
    admin = User("admin", "admin123", "admin")
    test_system.users.append(admin)
    test_system._save_users()
    test_system.login("admin", "admin123")
    test_system.add_car("Honda", "Civic", 2018, 2500)

    cars = test_system.get_available_cars()
    assert len(cars) == 1
    assert cars[0].model == "Civic"
