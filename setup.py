from setuptools import setup, find_packages

requirements = [
    "pandas==2.1.4",
    "beautifulsoup4==4.12.2",
    "requests==2.31.0",
    "colorama==0.4.6",
    "aiogram==3.3.0",
]

setup(
    name="cs2crap",
    version="1.1.2",
    author="cls",
    author_email="ferjenkill@gmail.com",
    description="Инструментарий для парсинга, автоматизации поиска выгод и торговли предметами Counter Strike 2",
    url="https://github.com/maxfraid/cs2crap",
    packages=find_packages(),
    install_requires=requirements,
)


#Алгоритм при работе с проектом в гитхабе
#1 Создаём виртуальное окружение в папке проекта,командой cd .. (выходим в папку гитхаб, cd folder project) командой python -m venv venv
#2 активируем виртуальное окружение .\venv\Scripts\activate , если юпитер выбираем select kernal справа на верху, или внизу с права.
#3 Запуск проекта, установка требуемых зависимостей, если проект запускаеться на голом venv без пакетовв, то выгружаем голый requirements.
#3.1 pip freeze > .\requirements.txt выгрузка зависимостей
#4 Создаём .gitignore, добавляем venv в gitignore
#5 добавляем workflow (по линтеру)
#6 если работаем с чужим проектом, создаём виртуальное окружение и устанавливаем зависимости зависимости pip install -r requirements.txt
#7 Когда 1, 2 или более файлов, уже разделяем комиты.