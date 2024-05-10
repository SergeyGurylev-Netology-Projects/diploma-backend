# Дипломная работа по профессии Fullstack-разработчик на Python

# Облачное хранилище My Cloud

## Backend

### Инструменты разработки

- Python
- Django
 
- ### Структура проекта

- **diploma** - основные конфигурационные файлы 
- **media** хранилище файлов пользователей приложения
- **my_cloud** - серверная часть приложения
- **frontend** - интерфейсная часть приложения

### Установка компонентов

`pip install -r requirements.txt`

### Статика

Из предварительно собранного frontend-проекта из папки `dist/assets` скопировать файлы скриптов и стилей в папку `frontend/dist/assets`
В файле `frontend/dist/index.html` изменить имена файлов скриптов и стилей на скопированные.

### Сервер

Установить на сервере postrges, gunicorn, nginx
Создать базу данных в postrges с пользователем с правами superuser. Параметры подключения указать в файле .env

Сконфигурировать nginx по следующему шаблону

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
