# API YaMDb

---
##  Описание

Проект предназначен для взаимодействия с API социальной сети YaMDb.
YaMDb собирает отзывы пользователей на различные произведения.

API предоставляет возможность взаимодействовать с базой данных по следующим направлениям:
  - авторизироваться
  - создавать свои отзывы и управлять ими (корректировать\удалять)
  - просматривать и комментировать отзывы других пользователей
  - просматривать комментарии к своему и другим отзывам
  - просматривать произведения, категории и жанры произведений

---
##  Используемые технологии

- Python 3.7.9
- requests==2.26.0
- django==2.2.16
- djangorestframework==3.12.4
- djangorestframework-simplejwt==4.7.2
- PyJWT==2.1.0
- pytest==6.2.4
- pytest-django==4.4.0
- pytest-pythonpath==0.7.3
- django_filter==21.1
- python-dotenv===0.20.0

##  Команды для запуска

Перед запуском необходимо склонировать проект:

python -m venv venv
Windows: source venv/Scripts/activate


И установить зависимости из файла requirements.txt:
python3 -m pip install --upgrade pip

pip install -r requirements.txt

Выполнить миграции:

python3 manage.py migrate


Запустить проект:

python3 manage.py runserver

##  Примеры запросов 

### Регистрация новых пользователей:

POST /api/v1/auth/signup/

'''
{
    "email": "string",
    "username": "user"
}
'''

### Пользователь отправляет POST-запрос с параметрами `username` и 
`confirmation_code` на эндпоинт `/api/v1/auth/token/`, в ответе на запрос ему 
приходит `token` (JWT-токен):

'''
json
{
    "username": "user",
    "confirmation_code": "string"
}
'''

## Об авторах
**Горшков Виталий**
**Дубовский Алексей**
