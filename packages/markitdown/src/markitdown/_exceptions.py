"""Exception classes for the MarkItDown document conversion library.

Hierarchy::

    MarkItDownException
    ├── MissingDependencyException
    ├── UnsupportedFormatException
    └── FileConversionException

`FailedConversionAttempt` is a companion dataclass (not an exception) that
captures the outcome of a single converter attempt within a
`FileConversionException`.
"""

from typing import Optional, List, Any

MISSING_DEPENDENCY_MESSAGE = """{converter} recognized the input as a potential {extension} file, but the dependencies needed to read {extension} files have not been installed. To resolve this error, include the optional dependency [{feature}] or [all] when installing MarkItDown. For example:

* pip install markitdown[{feature}]
* pip install markitdown[all]
* pip install markitdown[{feature}, ...]
* etc."""


class MarkItDownException(Exception):
    """
    Base exception class for MarkItDown.
    """

    pass


class MissingDependencyException(MarkItDownException):
    """
    Converters shipped with MarkItDown may depend on optional
    dependencies. This exception is thrown when a converter's
    convert() method is called, but the required dependency is not
    installed. This is not necessarily a fatal error, as the converter
    will simply be skipped (an error will bubble up only if no other
    suitable converter is found).

    Error messages should clearly indicate which dependency is missing.
    """

    pass


class UnsupportedFormatException(MarkItDownException):
    """
    Thrown when no suitable converter was found for the given file.
    """

    pass


class FailedConversionAttempt(object):
    """Records a single failed attempt to convert a file.

    Collected by `FileConversionException` to give callers a full audit trail
    of which converters were tried and what error each one produced.

    Args:
        converter: The converter instance that was attempted. Used to display
            the converter class name in error messages.
        exc_info: The 3-tuple returned by `sys.exc_info()` at the point of
            failure, or ``None`` if no exception info is available.
    """

    def __init__(self, converter: Any, exc_info: Optional[tuple] = None):
        self.converter = converter
        self.exc_info = exc_info


class FileConversionException(MarkItDownException):
    """
    Thrown when a suitable converter was found, but the conversion
    process fails for any reason.
    """

    def __init__(
        self,
        message: Optional[str] = None,
        attempts: Optional[List[FailedConversionAttempt]] = None,
    ):
        self.attempts = attempts

        if message is None:
            if attempts is None:
                message = "File conversion failed."
            else:
                message = f"File conversion failed after {len(attempts)} attempts:\n"
                for attempt in attempts:
                    if attempt.exc_info is None:
                        message += f" -  {type(attempt.converter).__name__} provided no execution info."
                    else:
                        message += f" - {type(attempt.converter).__name__} threw {attempt.exc_info[0].__name__} with message: {attempt.exc_info[1]}\n"

        super().__init__(message)
