"""Unit tests for Bootstrap functionality."""

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from src.podlet import Bootstrap, ResourceAbstract, ResourceRegistry
from src.podlet.helpers import Resolve


class DatabaseResource(ResourceAbstract):
    """A mock database resource for testing."""
    
    @classmethod
    def identity(cls) -> str:
        return "database"
    
    def initialize(self) -> None:
        """Initialize mock database connection."""
        self.connection = {"connected": True, "host": "localhost", "port": 5432}
        self.query_count = 0
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """Mock query execution."""
        self.query_count += 1
        return {"status": "success", "query": query, "count": self.query_count}

    def get_host(self) -> str: return self.options().get("host", "localhost")
    def get_port(self) -> int: return self.options().get("port", 5432)

class CacheResource(ResourceAbstract):
    """A mock cache resource for testing."""
    
    @classmethod
    def identity(cls) -> str:
        return "cache"
    
    def initialize(self) -> None:
        """Initialize mock cache."""
        self.cache = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Any:
        """Mock cache get operation."""
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Mock cache set operation."""
        self.cache[key] = value

    def get_type(self) -> str: return self.options().get("type", "default")
    def get_ttl(self) -> int: return self.options().get("ttl", 0)

class LoggerResource(ResourceAbstract):
    """A mock logger resource for testing."""
    
    @classmethod
    def identity(cls) -> str:
        return "logger"
    
    def initialize(self) -> None:
        """Initialize mock logger."""
        self.logs = []
    
    def log(self, level: str, message: str) -> None:
        """Mock logging operation."""
        self.logs.append({"level": level, "message": message})
    
    def get_logs(self, level: str | None = None) -> list:
        """Get logs, optionally filtered by level."""
        if level is None:
            return self.logs
        return [log for log in self.logs if log["level"] == level]

    def get_level(self) -> str: return self.options().get("level", "info")
    def get_output(self) -> str: return self.options().get("output", "console")




@pytest.fixture
def registrar_options() -> Dict[str, Any]:
    """Provide a sample options dictionary for testing."""
    return {
        "resource": {
            "database": {
                "enabled": True,
                "host": "db.test.local",
                "port": 3306
            },
            "cache": {
                "enabled": True,
                "type": "redis",
                "ttl": 3600
            },
            "logger": {
                "enabled": True,
                "level": "debug",
                "output": "file"
            }
        }
    }



@pytest.fixture
def bootstrap(registrar_options: Dict[str, Any]) -> Bootstrap:
    """Fixture to create a Bootstrap instance with test resources."""
    return Bootstrap(
        resources=[DatabaseResource, CacheResource, LoggerResource],
        options=registrar_options
    )
        



class TestBootstrapWithResources:
    """Test cases for the Bootstrap class."""

    def test_resource_registration(self, bootstrap: Bootstrap) -> None:
        """Test that resources are registered correctly."""
        assert bootstrap.has_registry(ResourceAbstract)

    def test_get_database_resource(self, bootstrap: Bootstrap) -> None:
        """Test retrieval and functionality of DatabaseResource."""
        db_resource = bootstrap.get_resource("database")
        assert isinstance(db_resource, DatabaseResource)
        db_resource.initialize()
        result = db_resource.execute_query("SELECT * FROM users;")
        assert result["status"] == "success"
        assert result["query"] == "SELECT * FROM users;"
        assert result["count"] == 1


    def test_get_cache_resource(self, bootstrap: Bootstrap) -> None:
        """Test retrieval and functionality of CacheResource."""
        cache_resource = bootstrap.get_resource("cache")
        assert isinstance(cache_resource, CacheResource)
        cache_resource.initialize()
        assert cache_resource.get("missing_key") is None
        cache_resource.set("test_key", "test_value")
        assert cache_resource.get("test_key") == "test_value"
        
    def test_get_logger_resource(self, bootstrap: Bootstrap) -> None:
        """Test retrieval and functionality of LoggerResource."""
        logger_resource = bootstrap.get_resource("logger")
        assert isinstance(logger_resource, LoggerResource)
        logger_resource.initialize()
        logger_resource.log("info", "This is an info message.")
        logger_resource.log("error", "This is an error message.")
        all_logs = logger_resource.get_logs()
        assert len(all_logs) == 2
        error_logs = logger_resource.get_logs("error")
        assert len(error_logs) == 1
        assert error_logs[0]["message"] == "This is an error message."

    def test_resource_options(self, bootstrap: Bootstrap, registrar_options: Dict[str, Any]) -> None:
        
        # db
        db_resource = bootstrap.get_resource("database")
        assert db_resource.get_host() == registrar_options["resource"]["database"]["host"]
        assert db_resource.get_port() == registrar_options["resource"]["database"]["port"]
        assert db_resource.options().get("enabled") is True

        # log
        logger_resource = bootstrap.get_resource("logger")
        assert logger_resource.get_level() == registrar_options["resource"]["logger"]["level"]
        assert logger_resource.get_output() == registrar_options["resource"]["logger"]["output"]
        assert logger_resource.options().get("enabled") is True

        # cache
        cache_resource = bootstrap.get_resource("cache")
        assert cache_resource.get_type() == registrar_options["resource"]["cache"]["type"]
        assert cache_resource.get_ttl() == registrar_options["resource"]["cache"]["ttl"]
        assert cache_resource.options().get("enabled") is True

    def test_get_resource_with_strings(self, bootstrap: Bootstrap) -> None:
        """Test that get_resource enforces type correctness."""
        db_resource = bootstrap.get_resource("database")
        assert isinstance(db_resource, DatabaseResource)
    
        cache_resource = bootstrap.get_resource("cache")
        assert isinstance(cache_resource, CacheResource)

        logger_resource = bootstrap.get_resource("logger")
        assert isinstance(logger_resource, LoggerResource)
        
    def test_get_resource_with_types(self, bootstrap: Bootstrap) -> None:
        """Test that get_resource enforces type correctness when using types."""
        db_resource = bootstrap.get_resource(DatabaseResource)
        assert isinstance(db_resource, DatabaseResource)
    
        cache_resource = bootstrap.get_resource(CacheResource)
        assert isinstance(cache_resource, CacheResource)

        logger_resource = bootstrap.get_resource(LoggerResource)
        assert isinstance(logger_resource, LoggerResource)


    def test_get_resource_type_error(self, bootstrap: Bootstrap) -> None:
        """Test that get_resource raises TypeError for incorrect types."""
        with pytest.raises(ValueError):
            bootstrap.get_resource("apple")  # Not a ResourceAbstract


class TestBootstrapAdditionalCoverage:
    """Additional tests for complete Bootstrap coverage."""

    def test_bootstrap_no_resources(self) -> None:
        """Test Bootstrap initialization with no resources."""
        bootstrap = Bootstrap()
        assert bootstrap.has_registry(ResourceAbstract)
        # Should have empty resource registry
        registry = bootstrap.get_registry(ResourceAbstract)
        assert registry.registered == {}
        assert registry.initialized == {}

    def test_bootstrap_get_registry(self) -> None:
        """Test get_registry method for resource registry."""
        bootstrap = Bootstrap()
        registry = bootstrap.get_registry(ResourceAbstract)
        assert isinstance(registry, ResourceRegistry)

    def test_bootstrap_register_additional_registry(self) -> None:
        """Test registering additional registries beyond default."""
        from dataclasses import dataclass

        from src.podlet.registry import Registry

        @dataclass
        class TestRegistry(Registry[int]):
            @classmethod
            def kind(cls) -> str:
                return "test"

        bootstrap = Bootstrap()
        bootstrap.register_registry(TestRegistry)  # type: ignore
        assert bootstrap.has_registry("test")

    def test_get_resource_invalid_identity(self) -> None:
        """Test get_resource with non-existent identity raises error."""
        bootstrap = Bootstrap()
        with pytest.raises(ValueError, match="RegistrantAbstract 'invalid' is not registered"):
            bootstrap.get_resource("invalid")

    def test_bootstrap_set_options(self) -> None:
        """Test options manipulation methods."""
        bootstrap = Bootstrap()
        new_options = {"resource": {"test": {"value": 42}}}
        bootstrap.set_options(new_options)
        assert bootstrap.options == new_options

        registry_opts = {"test": {"enabled": True}}
        bootstrap.set_registry_options("resource", registry_opts)
        assert bootstrap.get_registry_options("resource") == registry_opts

    def test_resource_registry_through_bootstrap(self) -> None:
        """Test ResourceRegistry integration via Bootstrap methods."""
        bootstrap = Bootstrap(resources=[DatabaseResource])
        # Test resources() method returns correct registry
        registry = bootstrap.resources()
        assert isinstance(registry, ResourceRegistry)

        # Test it can retrieve registered resources
        db = bootstrap.get("resource", "database")
        assert isinstance(db, DatabaseResource)
