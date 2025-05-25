from setuptools import setup, find_packages

setup(
    name='car_rental',
    version='0.1.0',
    packages=find_packages(),  # если ты используешь структуру с подкаталогами
    py_modules=['car_rental'],  # если car_rental.py лежит отдельно
    author='Твоё имя',
    description='Система проката автомобилей на Python',
    install_requires=[],  # можно указать зависимости
    python_requires='>=3.8',
)
