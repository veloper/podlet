# Podlet

[![PyPI version](https://badge.fury.io/py/podlet.svg)](https://pypi.org/project/podlet/)

A minimal, type-safe dependency injection framework for Python, focused on resource management and the Bootstrap pattern.

## Installation

```bash
pip install podlet
```

## Quick Start

```python
from podlet import Bootstrap, ResourceAbstract

class DatabaseResource(ResourceAbstract):
    @classmethod
    def kind(cls) -> str:
        return "resource"

    @classmethod
    def identity(cls) -> str:
        return "database"

    def initialize(self) -> None:
        self.connection = f"{self.options().get('host')}:{self.options().get('port')}"

    def query(self, sql: str):
        return f"Executed: {sql}"

bootstrap = Bootstrap(resources=[Database], options={
    "resource": {
        "database": {
            "host": "localhost",
            "port": 5432
        }
    }
})

db = bootstrap.get_resource("database")
print(db.query("SELECT 1"))  # Executed: SELECT 1
```

## Core Concepts

### Bootstrap

The central DI container that manages multiple registries and coming default with a `ResourceRegistry`.

```python
bootstrap = Bootstrap()
assert bootstrap.has_registry(ResourceRegistry)
```

### Resources

Define injectable dependencies by inheriting from `ResourceAbstract`.

```python
class CacheResource(ResourceAbstract):
    @classmethod
    def identity(cls) -> str:
        return "cache"

    def initialize(self) -> None:
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value):
        self.store[key] = value
```

### Registration and Retrieval

Register resources and retrieve them type-safely or by identity.

```python
bootstrap = Bootstrap(resources=[DatabaseResource, CacheResource], options={
    "resource": {
        "database": {
            "enabled": True,
            "host": "localhost",
            "port": 5432
        },
        "cache": {
            "enabled": True
        }
    }
})


db: Database = bootstrap.get_resource(Database)  # type-safe
db = bootstrap.get_resource("database")  # by string
```

### Dependencies

Resources can access other resources via `self.registry`.

```python
class Service(ResourceAbstract):
    @classmethod
    def identity(cls) -> str:
        return "service"

    def initialize(self) -> None:
        self.db = self.registry.get("database")

    def do_work(self):
        return self.db.query("SELECT 1")
```

## Advanced Usage

### Structure

- `Registrar`: Manages multiple `Registry` instances.
    - `Registry`: Manages multiple `Registrant` instances.
        - `RegistrantAbstract`: Base class for registrable entities (e.g., resources, services, etc.)

### Custom Registrars, Registries, and Registrants

Bootstrap is actually built on top of the underlying `Registrar` -> `Registry` -> `RegistrantAbstract` pattern and you're free to construct your own in any compatible way.

```python
from podlet import Registry

class ServiceRegistry(Registry):
    @classmethod
    def kind(cls) -> str:
        return "service"

class DatabaseService(RegistrantAbstract):
    @classmethod
    def kind(cls) -> str:
        return "database"

class MyApp(Registrar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_registry(ServiceRegistry)

    def get(name: str):
         return self.get_registry("service").get(name)

app = MyApp()

app.get("database") 
```

### Direct Registry Access

Interact with registries directly.

```python
bootstrap.has_registry("resource")
registry = bootstrap.get_registry("resource")
bootstrap.register(NewResource)
bootstrap.set_options({"resource": {"new": {"enabled": True}}})
```

## Testing

Mock resources for testing.

```python
import pytest

class MockDBResource(ResourceAbstract):
    @classmethod
    def identity(cls) -> str:
        return "database"

    def initialize(self):
        self.queries = []

    def query(self, sql):
        self.queries.append(sql)
        return {"result": "mock"}

@pytest.fixture
def bootstrap():
    return Bootstrap(resources=[MockDBResource], options={
        "resource": {
            "database": {
                "enabled": True
            }
        }
    })

def test_db(bootstrap):
    db = bootstrap.get_resource("database")
    result = db.query("SELECT * FROM users")
    assert result["result"] == "mock"
    assert len(db.queries) == 1
```

## Architecture

- **Type Safety**: Compile-time guarantees with generics.
- **Lifecycle**: Lazy initialization, singleton pattern, memory efficient.
- **Resolution**: Smart polymorphic resolution via `Resolve` utility.

## Contributing

Contributions welcome! Please open issues or PRs on GitHub.

## Acknowledgements

Inspiration for this project was drawn from Zend Framework's plugin architecture. 

## License

3-Clause BSD License. See LICENSE file.
