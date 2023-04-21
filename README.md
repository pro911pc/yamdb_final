# yamdb_final
![yamdb workflow](https://github.com/pro911pc/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

# API_YAMDB
REST API проект для сервиса YaMDb — сбор отзывов о фильмах, книгах или музыке.


## Адрес проекта
http://51.250.99.202/admin/

### Описание
Проект YaMDb собирает отзывы (Review) пользователей на произведения (Title). 
Произведения делятся на категории: "Книги", "Фильмы", "Музыка". 
Список категорий (Category) может быть расширен.
Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или 
послушать музыку. В каждой категории есть произведения: книги, фильмы или 
музыка. Например, в категории "Книги" могут быть произведения 
"Винни Пух и все-все-все" и "Марсианские хроники", а в категории 
"Музыка" — песня "Давеча" группы "Насекомые" и вторая сюита Баха. 
Произведению может быть присвоен жанр из списка предустановленных 
(например, "Сказка", "Рок" или "Артхаус"). Новые жанры может создавать 
только администратор. Благодарные или возмущённые читатели оставляют к 
произведениям текстовые отзывы (Review) и выставляют произведению рейтинг.
### Технологии
Python 3.8
Django 2.2.19
Docker
### # Шаблон наполнения .env файла

	DB_ENGINE=django.db.backends.postgresql   # провайдер
	DB_NAME=postgres		                  # имя базы данных
	POSTGRES_USER=postgres			          # пользователь базы данных
	POSTGRES_PASSWORD=postgres		          # пароль пользователя базы данных
	DB_HOST=db 				                  # имя хоста баз данных
	DB_PORT=5432			                  # порт для работы с базой данных

### # Запуск проекта в контейнерах Docker
- Перейдите в раздел infra для сборки docker-compose
```
sudo docker-compose up
```

- Выполнить migrate
```
sudo docker-compose exec web python manage.py migrate
```
- Для загрузки данных (опционально)
```
sudo docker-compose exec web python manage.py loaddata db.json
```
- Создайте пользователя
```
sudo docker-compose exec web python manage.py createsuperuser
```
- (или) Сменить пароль для пользователя admin
```
sudo docker-compose exec web python manage.py changepassword admin
```
- Сформируйте STATIC файлы:
```
sudo docker-compose exec web python manage.py collectstatic --no-input
```
# API ресурсы:
- **AUTH**: Аутентификация.
- **USERS**: Пользователи.
- **TITLES**: Произведения, к которым пишут отзывы.
- **CATEGORIES**: Категория произведений ("Фильмы", "Книги", "Музыка").
- **GENRES**: Жанры, одно из произведений может быть присвоено к нескольким жанрам.
- **REVIEWS**: Отзывы на произведения.
- **COMMENTS**: Комментарии к отзывам.

# Алгоритм регистрации пользователей
Пользователь отправляет POST-запрос с параметром email и username на `/api/v1/auth/signup`.
YaMDB отправляет письмо с кодом подтверждения (confirm_code) на адрес email (эмуляция почтовго сервера).
Пользователь отправляет POST-запрос с параметрами email и confirmation_code на `/api/v1/auth/token/`, 
в ответе на запрос ему приходит token.
Эти операции выполняются один раз, при регистрации пользователя. 
В результате пользователь получает токен и каждый раз отправяет его при запросе.

# Пользовательские роли
- **Аноним** — может просматривать описания произведений, читать отзывы и комментарии.
- **Аутентифицированный пользователь (user)** — может читать всё, как и Аноним, дополнительно может публиковать отзывы и ставить рейтинг произведениям (фильмам/книгам/песенкам), может комментировать чужие отзывы и ставить им оценки; может редактировать и удалять свои отзывы и комментарии.
- **Модератор (moderator)** — те же права, что и у Аутентифицированного пользователя плюс право удалять и редактировать любые отзывы и комментарии.
- **Администратор (admin)** — полные права на управление проектом и всем его содержимым. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.
- **Супер юзер** — те же права, что и у роли Администратор.