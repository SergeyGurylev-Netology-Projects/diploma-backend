# Дипломная работа по профессии Fullstack-разработчик на Python

# Облачное хранилище My Cloud

## Backend

### Инструменты разработки

- Python
- Django
 
### Структура проекта

- **diploma** - основные конфигурационные файлы 
- **media/user_files** хранилище файлов пользователей (создается автоматически при работе приложения)
- **media/deleted_files** хранилище удаленных файлов пользователей (создается автоматически при работе приложения при удалении файла)
- **my_cloud** - серверная часть приложения (models, views, rest) 
- **frontend** - интерфейсная часть приложения (react)

### Статика

Из предварительно собранного frontend-проекта из папки `dist/assets` скопировать файлы скриптов и стилей в папку `frontend/dist/assets`
В файле `frontend/dist/index.html` изменить имена файлов скриптов и стилей на скопированные.

### Сервер

- Развернуть приложение из репозитория на сервере. Создать и активировать виртуальное окружение. Установить компоненты командой 
`pip install -r requirements.txt`
- Собрать файлы статики командой `python manage.py collectstatic`
- Установить postgres, gunicorn, nginx. Сконфигурировать nginx по следующему шаблону

```
server {
  listen 80;
  server_name your_ip_address;

  location /static/ {
    root /home/your_user_name/diploma-backend;
  }
  location / {
    include proxy_params;
    proxy_pass http://unix:/home/your_user_name/diploma-backend/diploma/project.sock;
  }
}
```

- Создать базу данных в postgres. Параметры подключения указать в файле .env
- Добавить в базу данных пользователя с правами superuser

### Переменные окружения
В корне проекта создать файл .env<br>
Содержимое файла<br>
```
SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=
DB_NAME=
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=
```
