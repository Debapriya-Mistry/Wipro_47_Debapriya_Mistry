class FrameworkError(Exception):
    """Base class for all framework errors."""

class ConfigError(FrameworkError):
    """Invalid or missing configuration."""

class SchemaValidationError(FrameworkError):
    """Response body did not match the expected JSON schema"""

class TestDataError(FrameworkError):
    """Requested test data could not be found or built"""