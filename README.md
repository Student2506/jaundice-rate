# Фильтр желтушных новостей


Данный проект представляет из себя веб-сервис, который, по запросу, забирает и анализирует статьи с сайта inosmi.ru показывая совпадения текста по словарю (текущий словарь представляет собой список слов, встречающихся в "жёлтой прессе") 

Для работы потребуется запустить вэб-сервис (указано ниже) и отправить запрос через http(s)-клиент, указав ссылки, которые требуется проанализировать

Пока поддерживается только один новостной сайт - [ИНОСМИ.РУ](https://inosmi.ru/). Для него разработан специальный адаптер, умеющий выделять текст статьи на фоне остальной HTML разметки. Для других новостных сайтов потребуются новые адаптеры, все они будут находиться в каталоге `adapters`. Туда же помещен код для сайта ИНОСМИ.РУ: `adapters/inosmi_ru.py`.

В перспективе можно создать универсальный адаптер, подходящий для всех сайтов, но его разработка будет сложной и потребует дополнительных времени и сил.

# Как установить

Вам понадобится Python версии 3.7 или старше. Для установки пакетов рекомендуется создать виртуальное окружение.

Первым шагом установите пакеты:

```python3
pip install -r requirements.txt
```

# Как запустить

```python3
python -m aiohttp.web -H localhost -P 80 server:init_func
```

# Отправка запроса
сделать запрос формата в браузере или другом http-клиенте
http://127.0.0.1?urls=https://...html
где https://...html адрес статьи

# Как запустить тесты

Для тестирования используется [pytest](https://docs.pytest.org/en/latest/), тестами покрыты фрагменты кода сложные в отладке: text_tools.py и адаптеры. Команды для запуска тестов:

```
python -m pytest adapters/inosmi_ru.py
```

```
python -m pytest text_tools.py
```

# Цели проекта

Код написан в учебных целях. Это урок из курса по веб-разработке — [Девман](https://dvmn.org).
