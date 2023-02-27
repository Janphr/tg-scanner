# Telegram-Scanner
Code for:
https://youtu.be/-NjVUOdyPNY

## Getting started
Use poetry or pip to get everything running

then replace 
[api_id](./tg_scanner/app/modules/tg_scanner.py#L56) and [api_hash](./tg_scanner/app/modules/tg_scanner.py#L57) with the one of your telegram account: \
https://core.telegram.org/api/obtaining_api_id

lastly set you [start_channel](./tg_scanner/app/modules/tg_scanner.py#L58)

and run main.py or `poetry run main`

## install Poetry for Linux
```
curl -sSL https://install.python-poetry.org | python3 -
```

## install Poetry for Windows
```
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

## install all dependencies
if you'd like to have .venv locally in the project
```
poetry config virtualenvs.in-project true
```
then
```
poetry install
```

## update all dependencies
```
poetry update
```

## for more read the [docs](https://python-poetry.org/docs/) or
```
poetry list
```