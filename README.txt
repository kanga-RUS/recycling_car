python 3.5

1) Установить необходимые пакеты
$ sudo apt-get install apache2 libapache2-mod-wsgi python-dev
2) Активировать модуль wsgi для apache2
$ sudo a2enmod wsgi
3) Поместить папку с приложением в необходимый каталог /var/www/flaskapp
4) В выбранной папке создать виртуальное окружение
$ virtualenv env -p ($which python3)
5) Активировать виртуальное окружение
$ source env/bin/activate
6) Установить все необходимые зависимости
$ pip install -r requirements.txt
7) Деактивировать виртуальное окружение
$ deactivate
8) Создаем пользователя без домашнего каталога:
$ sudo useradd -M flask
9) Отключаем шелл:
$ sudo usermod -s /bin/false flask
10) Блокируем аккаунт для доступа из консоли:
$ sudo usermod -L flask
11) Добавляем пользователя в группу Apache www-data
$  sudo adduser flask www-data
12) Изменяем права доступа (на запись) к папке для скачивания файлов ПТС автомобиля
$ sudo chown -R www-data:www-data /var/www/flaskapp/flaskapp/uploads
13) перемещаем файл 'flaskapp.conf' в папку /etc/apache2/sites-available
14) применяем настройки файла конфигурации
$ sudo a2ensite flask.conf
15) в файл '/etc/apache2/mods-available/wsgi.conf' добавляем строчки
WSGIPythonHome /usr/bin/python3.5
WSGIPithonPath /var/www/flaskapp/env/lib/python3.5/site-packages/
16) Отключаем default-конфигурацию сайта
$ sudo a2dissite 000-default.conf
17) Перезапускаем Apache
$ sudo service apache2 reload
