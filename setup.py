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
