# Важно!

После создания виртуального окружения

```
python3 -m venv venv
```

Добавь в скрипт `venv/bin/activate` или `venv/scripts/activate` следующие строчки после:

```
VIRTUAL_ENV="/absolute/path/to/selenium_learning/venv"
export VIRTUAL_ENV

_OLD_VIRTUAL_PATH="$PATH"
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH
```

```
PYTHONPATH="/absolute/path/to/selenium_learning"
export PYTHONPATH

# echo не обязательно )
echo "PATH=$PATH"
echo "PYTHONPATH=$PYTHONPATH"
```

Что-бы Python смог увидеть и импортировать модули.