from __future__ import annotations


class KanseiError(Exception):
    """Base class for Kansei domain errors."""


class InstanceNotFoundError(KanseiError):
    """Raised when no Kansei instance root can be found."""


class RegistryError(KanseiError):
    """Raised when project or provider registry data is invalid."""


class ProjectNotFoundError(RegistryError):
    """Raised when a project id is not registered."""


class ProviderNotFoundError(RegistryError):
    """Raised when a provider id is not registered."""


class ConfigError(KanseiError):
    """Raised when workspace configuration cannot be loaded."""
