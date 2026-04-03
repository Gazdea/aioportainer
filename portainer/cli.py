"""Unified CLI for Portainer."""
import asyncio
import json

import click

from .client import PortainerClient
from .container_manager import ContainerManager
from .listener import EventListener
from .monitor import HealthMonitor
from .stack_manager import StackManager
from .watcher import ImageWatcher


def json_output(data, error=None):
    """Print JSON output."""
    result = {"success": error is None, "data": data, "error": error}
    print(json.dumps(result, default=str))


@click.group()
@click.option("--url", default="https://gaz-linux:9443", help="Portainer URL")
@click.option("--token", required=True, help="Portainer API Token")
@click.pass_context
def cli(ctx, url, token):
    """Portainer CLI - управление стеками и контейнерами."""
    ctx.ensure_object(dict)
    ctx.obj["client"] = PortainerClient(url=url, token=token)


# === STACK COMMANDS ===

@cli.group()
def stack():
    """Управление стеками."""
    pass


@stack.command("list")
@click.pass_context
def stack_list(ctx):
    """Список всех стеков."""
    async def run():
        client = ctx.obj["client"]
        await client.connect()
        try:
            sm = StackManager(client)
            stacks = await sm.list_stacks()
            data = [
                {
                    "id": s.id,
                    "name": s.name,
                    "status": s.status,
                    "status_text": s.status_text,
                    "endpoint_id": s.endpoint_id,
                    "state": s.state,
                    "is_active": s.is_active,
                    "is_error": s.is_error,
                }
                for s in stacks
            ]
            json_output(data)
        finally:
            await client.disconnect()

    asyncio.run(run())


@stack.command("status")
@click.argument("name")
@click.pass_context
def stack_status(ctx, name):
    """Статус стека по имени."""
    async def run():
        client = ctx.obj["client"]
        await client.connect()
        try:
            sm = StackManager(client)
            stack = await sm.get_stack(name)
            if not stack:
                json_output(None, {"code": "NOT_FOUND", "message": f"Stack '{name}' not found"})
                return

            containers = await sm.get_stack_containers(name)
            data = {
                "id": stack.id,
                "name": stack.name,
                "status": stack.status,
                "status_text": stack.status_text,
                "endpoint_id": stack.endpoint_id,
                "state": stack.state,
                "is_active": stack.is_active,
                "is_error": stack.is_error,
                "git_url": stack.git_url,
                "containers": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "image": c.image,
                        "state": c.state,
                        "status": c.status,
                        "is_running": c.is_running,
                    }
                    for c in containers
                ],
            }
            json_output(data)
        finally:
            await client.disconnect()

    asyncio.run(run())


@stack.command("deploy")
@click.argument("name")
@click.argument("message", required=False, default=None)
@click.option("--poll-interval", default=5, help="Polling interval in seconds")
@click.option("--max-retries", default=24, help="Max polling attempts")
@click.pass_context
def stack_deploy(ctx, name, message, poll_interval, max_retries):
    """Деплой стека (commit + push + redeploy + monitor)."""
    async def run():
        client = ctx.obj["client"]
        await client.connect()
        try:
            sm = StackManager(client)
            result = await sm.deploy(
                name,
                commit_message=message,
                poll_interval=poll_interval,
                max_retries=max_retries,
            )
            data = {
                "stack_id": result.stack.id,
                "name": result.stack.name,
                "success": result.success,
                "message": result.message,
                "status": result.stack.status,
            }
            if not result.success:
                json_output(data, {"code": "DEPLOY_FAILED", "message": result.message})
            else:
                json_output(data)
        finally:
            await client.disconnect()

    asyncio.run(run())


@stack.command("containers")
@click.argument("name")
@click.pass_context
def stack_containers(ctx, name):
    """Контейнеры стека."""
    async def run():
        client = ctx.obj["client"]
        await client.connect()
        try:
            sm = StackManager(client)
            containers = await sm.get_stack_containers(name)
            data = [
                {
                    "id": c.id,
                    "short_id": c.short_id,
                    "name": c.name,
                    "image": c.image,
                    "state": c.state,
                    "status": c.status,
                    "is_running": c.is_running,
                    "endpoint_id": c.endpoint_id,
                }
                for c in containers
            ]
            json_output(data)
        finally:
            await client.disconnect()

    asyncio.run(run())


# === CONTAINER COMMANDS ===

@cli.group()
def container():
    """Управление контейнерами."""
    pass


@container.command("list")
@click.argument("endpoint")
@click.option("--stack", help="Filter by stack name")
@click.pass_context
def container_list(ctx, endpoint, stack):
    """Список контейнеров на endpoint."""
    async def run():
        client = ctx.obj["client"]
        await client.connect()
        try:
            cm = ContainerManager(client)
            containers = await cm.get_containers(endpoint, stack_name=stack)
            data = [
                {
                    "id": c.id,
                    "short_id": c.short_id,
                    "name": c.name,
                    "image": c.image,
                    "state": c.state,
                    "status": c.status,
                    "is_running": c.is_running,
                    "labels": c.labels,
                }
                for c in containers
            ]
            json_output(data)
        finally:
            await client.disconnect()

    asyncio.run(run())


@container.command("logs")
@click.argument("endpoint")
@click.argument("container_id")
@click.option("--lines", default=50, help="Number of log lines")
@click.pass_context
def container_logs(ctx, endpoint, container_id, lines):
    """Логи контейнера."""
    async def run():
        client = ctx.obj["client"]
        await client.connect()
        try:
            cm = ContainerManager(client)
            logs = await cm.get_logs(endpoint, container_id, lines)
            json_output({"logs": logs, "container_id": container_id})
        finally:
            await client.disconnect()

    asyncio.run(run())


@container.command("stats")
@click.argument("endpoint")
@click.argument("container_id")
@click.pass_context
def container_stats(ctx, endpoint, container_id):
    """Статистика контейнера (CPU, RAM, Network)."""
    async def run():
        client = ctx.obj["client"]
        await client.connect()
        try:
            cm = ContainerManager(client)
            stats = await cm.get_stats(endpoint, container_id)
            data = {
                "container_id": stats.container_id,
                "cpu_percent": stats.cpu_percent,
                "memory_usage_mb": round(stats.memory_usage_mb, 2),
                "memory_limit_mb": round(stats.memory_limit_mb, 2),
                "memory_percent": stats.memory_percent,
                "network_rx_kb": round(stats.network_rx / 1024, 2),
                "network_tx_kb": round(stats.network_tx / 1024, 2),
                "block_read_kb": round(stats.block_read / 1024, 2),
                "block_write_kb": round(stats.block_write / 1024, 2),
            }
            json_output(data)
        finally:
            await client.disconnect()

    asyncio.run(run())


@container.command("start")
@click.argument("endpoint")
@click.argument("container_id")
@click.pass_context
def container_start(ctx, endpoint, container_id):
    """Запустить контейнер."""
    async def run():
        client = ctx.obj["client"]
        await client.connect()
        try:
            cm = ContainerManager(client)
            await cm.start(endpoint, container_id)
            json_output({"message": f"Container {container_id} started"})
        finally:
            await client.disconnect()

    asyncio.run(run())


@container.command("stop")
@click.argument("endpoint")
@click.argument("container_id")
@click.pass_context
def container_stop(ctx, endpoint, container_id):
    """Остановить контейнер."""
    async def run():
        client = ctx.obj["client"]
        await client.connect()
        try:
            cm = ContainerManager(client)
            await cm.stop(endpoint, container_id)
            json_output({"message": f"Container {container_id} stopped"})
        finally:
            await client.disconnect()

    asyncio.run(run())


@container.command("restart")
@click.argument("endpoint")
@click.argument("container_id")
@click.pass_context
def container_restart(ctx, endpoint, container_id):
    """Перезапустить контейнер."""
    async def run():
        client = ctx.obj["client"]
        await client.connect()
        try:
            cm = ContainerManager(client)
            await cm.restart(endpoint, container_id)
            json_output({"message": f"Container {container_id} restarted"})
        finally:
            await client.disconnect()

    asyncio.run(run())


# === HEALTH COMMANDS ===

@cli.group()
def health():
    """Мониторинг здоровья."""
    pass


@health.command("check")
@click.argument("name")
@click.pass_context
def health_check(ctx, name):
    """Check stack health."""
    async def run():
        client = ctx.obj["client"]
        await client.connect()
        try:
            monitor = HealthMonitor(client)
            result = await monitor.check_stack_health(name)
            json_output(result)
        finally:
            await client.disconnect()

    asyncio.run(run())


@health.command("all")
@click.pass_context
def health_all(ctx):
    """Check all stacks health."""
    async def run():
        client = ctx.obj["client"]
        await client.connect()
        try:
            monitor = HealthMonitor(client)
            results = await monitor.check_all_stacks()
            json_output(results)
        finally:
            await client.disconnect()

    asyncio.run(run())


# === SYSTEM COMMANDS ===

@cli.group()
def system():
    """Системная информация."""
    pass


@system.command("stats")
@click.pass_context
def system_stats(ctx):
    """Общая статистика системы."""
    async def run():
        client = ctx.obj["client"]
        await client.connect()
        try:
            monitor = HealthMonitor(client)
            stats = await monitor.get_system_stats()
            json_output(stats)
        finally:
            await client.disconnect()

    asyncio.run(run())


# === WATCH COMMANDS ===

@cli.group()
def watch():
    """Мониторинг обновлений образов."""
    pass


@watch.command("images")
@click.option("--interval", default=12, help="Polling interval in hours")
@click.option("--endpoint", default=None, help="Specific endpoint ID")
@click.pass_context
def watch_images(ctx, interval, endpoint):
    """Запустить мониторинг обновлений образов."""
    async def run():
        client = ctx.obj["client"]
        await client.connect()
        try:
            import datetime
            watcher = ImageWatcher(
                client,
                interval=datetime.timedelta(hours=interval),
                endpoint_id=endpoint,
                debug=True,
            )
            watcher.start()

            await asyncio.sleep(10)

            results = []
            for (ep_id, container_id), result in watcher.results.items():
                results.append({
                    "endpoint_id": ep_id,
                    "container_id": container_id,
                    "container_name": result.container_name,
                    "image": result.image,
                    "update_available": result.status.update_available if result.status else False,
                })
            json_output(results)

            watcher.stop()
        finally:
            await client.disconnect()

    asyncio.run(run())


@watch.command("status")
@click.pass_context
def watch_status(ctx):  # noqa: ARG001
    """Показать статус мониторинга."""
    json_output({"message": "Use watch images command to start monitoring"})


# === EVENTS COMMANDS ===

@cli.group()
def events():
    """События Docker в реальном времени."""
    pass


@events.command("start")
@click.option("--endpoint", default=None, help="Specific endpoint ID")
@click.option("--types", default="container", help="Event types (comma-separated)")
@click.option("--duration", default=30, help="Duration in seconds")
@click.pass_context
def events_start(ctx, endpoint, types, duration):
    """Слушать события в реальном времени."""
    async def run():
        client = ctx.obj["client"]
        await client.connect()
        try:
            event_types = types.split(",") if types else None
            listener = EventListener(
                client,
                endpoint_id=endpoint,
                event_types=event_types,
                debug=True,
            )

            collected = []

            def on_event(result):
                collected.append({
                    "endpoint_id": result.endpoint_id,
                    "type": result.event.type,
                    "action": result.event.action,
                    "actor_id": result.event.actor_id,
                })

            listener.register_callback(on_event)
            listener.start()

            await asyncio.sleep(duration)

            listener.stop()
            json_output(collected)

        finally:
            await client.disconnect()

    asyncio.run(run())


@events.command("list")
@click.argument("endpoint")
@click.option("--since", default=3600, help="Seconds in the past")
@click.pass_context
def events_list(ctx, endpoint, since):
    """Получить недавние события."""
    async def run():
        client = ctx.obj["client"]
        await client.connect()
        try:
            listener = EventListener(client, endpoint_id=int(endpoint))
            results = await listener.get_recent_events(int(endpoint), since)

            data = [
                {
                    "type": r.event.type,
                    "action": r.event.action,
                    "actor_id": r.event.actor_id,
                    "time": r.event.time,
                }
                for r in results
            ]
            json_output(data)
        finally:
            await client.disconnect()

    asyncio.run(run())


def main():
    """Entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
