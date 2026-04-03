# aioportainer

Async CLI для Portainer API с поддержкой Git-деплоя, мониторинга, отслеживания обновлений образов и событий Docker.

## Возможности

- **Асинхронный HTTP-клиент** - Полное покрытие Portainer API
- **Управление стеками** - Git-based деплой с автоматическим commit/push/redeploy
- **Управление контейнерами** - Запуск, остановка, перезагрузка, логи, статистика
- **Мониторинг здоровья** - Проверка состояния стеков и контейнеров
- **ImageWatcher** - Мониторинг обновлений Docker-образов
- **EventListener** - События Docker в реальном времени

## Установка

```bash
pip install -e .
```

## Быстрый старт

```python
import asyncio
from portainer import PortainerClient, StackManager

async def main():
    async with PortainerClient(
        url="https://portainer:9443",
        token="your-api-key",
    ) as client:
        sm = StackManager(client)
        stacks = await sm.list_stacks()
        for s in stacks:
            print(f"{s.name}: {s.status_text}")

asyncio.run(main())
```

## Использование CLI

```bash
# Установить токен
$env:PORTAINER_TOKEN="your-token"

# Список стеков
portainer stack list --url "https://portainer:9443" --token $env:PORTAINER_TOKEN

# Деплой стека
portainer stack deploy mystack "update message"

# Мониторинг образов
portainer watch images --interval 6

# Слушать события
portainer events start --duration 30
```

## Структура проекта

```
portainer/
├── client.py         # HTTP-клиент (Portainer API)
├── models.py         # Dataclass-модели
├── stack_manager.py  # Управление стеками + git
├── container_manager.py  # Управление контейнерами
├── monitor.py        # Мониторинг здоровья
├── watcher.py        # ImageWatcher
├── listener.py       # EventListener
└── cli.py            # CLI
```

## Разработка

```bash
# Установка с dev-зависимостями
pip install -e ".[dev]"

# Запуск тестов
pytest

# Линтинг
ruff check portainer/

# Типизация
mypy portainer/
```

## Лицензия

MIT
