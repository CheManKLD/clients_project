<h1 align="center">Clients project</h1>
Тестовое задание.

## Технологии:
### Djando, Django REST frameworks, PostgreSQL

<h2 align="center">Запуск приложения</h2>
1. Клонировать проект.
2. Создать файл `.env` в корневой папке следующего содержания:

```
DEBUG=1
SECRET_KEY=СЮДА_ВСТАВИТЬ_ВАШ_СЕКРЕТНЫЙ_DJANGO_КЛЮЧ
ALLOWED_HOSTS=localhost,127.0.0.1,[::1]
DATABASE_URL=psql://clients_user:password@localhost:5432/clients_db
```

3. Создать виртуальное окружение, активировать его и установить зависимости командой `pip install -r requirements.txt`.
4. Выполнить миграцию в базу данных командой `python manage.py migrate`.
5. Создать superuser командой `python manage.py createsuperuser` и назначить ему username и password.
6. Запустить приложение командой `python manage.py runserver` и следовать API документации ниже.

<h2 align="center">API документация</h2>

### Доступные API методы:
**POST** `api/v1/upload-data/xlsx/` - обработка и загрузка данных из файлов `client_org.xlsx` и `bills.xlsx`
в базу данных.

**GET** `api/v1/client-list/` - Получение списка всех клиентов. Каждый элемент списка выводится с данными:
<ul>
    <li>Название клиента</li>
    <li>Количество организаций</li>
    <li>Приход (сумма по счетам всех организаций клиента)</li>
</ul>

**GET** `api/v1/bill-list/` - Получение списка счетов с возможностью фильтрации по наименованию организации и/или
по наименованию клиента.