
class ServiceError(Exception):
    """Base class for all service errors"""
    pass


class NotFoundError(ServiceError):
    """Raised when resource not found"""
    pass


class ValidationError(ServiceError):
    """Raised when input validation fails"""
    pass


class FileAccessError(ServiceError):
    """Raised when file access is unsafe"""
    pass