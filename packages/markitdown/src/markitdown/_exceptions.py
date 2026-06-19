"""Custom exception hierarchy for the MarkItDown conversion pipeline.

All exceptions raised by MarkItDown derive from :class:`MarkItDownException`
so callers can catch them with a single ``except MarkItDownException`` clause
or handle specific sub-types for finer-grained error recovery.

Typical exception flow
----------------------
1. :class:`MissingDependencyException` — raised *inside* a converter when
   an optional dependency (e.g. ``pptx``, ``openpyxl``) is absent.  The
   orchestrator catches this and tries the next converter.
2. :class:`UnsupportedFormatException` — raised by the orchestrator when
   *no* converter accepted the file.
3. :class:`FileConversionException` — raised when a converter was matched
   but failed mid-conversion.  Carries the list of
   :class:`FailedConversionAttempt` records for diagnosis.
"""

from typing import Optional, List, Any

MISSING_DEPENDENCY_MESSAGE = """{converter} recognized the input as a potential {extension} file, but the dependencies needed to read {extension} files have not been installed. To resolve this error, include the optional dependency [{feature}] or [all] when installing MarkItDown. For example:

* pip install markitdown[{feature}]
* pip install markitdown[all]
* pip install markitdown[{feature}, ...]
* etc."""


class MarkItDownException(Exception):
    """Base exception class for all MarkItDown errors.

    Catch this class to handle any error originating from MarkItDown
    without needing to import each sub-type individually.

    Example::

        from markitdown import MarkItDown, MarkItDownException

        md = MarkItDown()
        try:
            result = md.convert("document.xyz")
        except MarkItDownException as exc:
            print(f"Conversion failed: {exc}")
    """

    pass


class MissingDependencyException(MarkItDownException):
    """Raised when a converter requires an optional dependency that is absent.

    Converters bundled with MarkItDown may depend on packages that are not
    installed by default (e.g. ``python-pptx`` for PowerPoint files).
    When such a converter is invoked and the dependency is missing, it raises
    this exception instead of a bare :class:`ImportError`.

    The MarkItDown orchestrator *catches* this exception internally and
    falls through to the next candidate converter.  It only propagates to
    the caller if every candidate converter raises it.

    The error message should use :data:`MISSING_DEPENDENCY_MESSAGE` as a
    template so the user receives a consistent, actionable prompt.

    Example::

        from markitdown._exceptions import (
            MissingDependencyException,
            MISSING_DEPENDENCY_MESSAGE,
        )

        try:
            import pptx  # noqa: F401
        except ImportError:
            raise MissingDependencyException(
                MISSING_DEPENDENCY_MESSAGE.format(
                    converter="PowerPointConverter",
                    extension=".pptx",
                    feature="pptx",
                )
            )
    """

    pass


class UnsupportedFormatException(MarkItDownException):
    """Raised when no registered converter can handle the given file.

    This exception is thrown by the MarkItDown orchestrator after all
    candidate converters have been tried and none returned a positive
    ``accepts()`` response.

    Attributes:
        (Inherits all attributes from :class:`Exception`.)

    Example::

        from markitdown import MarkItDown, UnsupportedFormatException

        md = MarkItDown()
        try:
            result = md.convert("unknown.xyz")
        except UnsupportedFormatException:
            print("No converter available for this file type.")
    """

    pass


class FailedConversionAttempt:
    """Records the outcome of a single (failed) converter invocation.

    Instances of this class are collected by the MarkItDown orchestrator
    when a converter raises an exception during ``convert()``.  The list
    is attached to a :class:`FileConversionException` so callers can
    inspect which converters were tried and why each one failed.

    Attributes:
        converter: The converter instance that was attempted.
        exc_info: A 3-tuple ``(type, value, traceback)`` as returned by
            :func:`sys.exc_info`, or ``None`` if no exception info was
            captured.

    Example::

        import sys
        from markitdown._exceptions import FailedConversionAttempt

        try:
            converter.convert(stream, stream_info)
        except Exception:
            attempt = FailedConversionAttempt(converter, sys.exc_info())
    """

    def __init__(self, converter: Any, exc_info: Optional[tuple] = None) -> None:
        """Initialise a failed-attempt record.

        Args:
            converter: The converter instance that raised an exception.
            exc_info: The 3-tuple from :func:`sys.exc_info`, or ``None``
                when no exception context is available.
        """
        self.converter = converter
        self.exc_info = exc_info


class FileConversionException(MarkItDownException):
    """Raised when a matched converter fails during the conversion step.

    Unlike :class:`UnsupportedFormatException`, this exception implies
    that *at least one* converter accepted the file but subsequently
    encountered an error while processing it.

    Attributes:
        attempts: List of :class:`FailedConversionAttempt` records, one
            per converter that was tried.  ``None`` when the exception
            was created without attempt tracking.

    Example::

        from markitdown import MarkItDown, FileConversionException

        md = MarkItDown()
        try:
            result = md.convert("corrupted.pdf")
        except FileConversionException as exc:
            if exc.attempts:
                for attempt in exc.attempts:
                    print(type(attempt.converter).__name__, attempt.exc_info)
    """

    def __init__(
        self,
        message: Optional[str] = None,
        attempts: Optional[List[FailedConversionAttempt]] = None,
    ) -> None:
        """Initialise a file-conversion error.

        Args:
            message: Human-readable description of the failure.  When
                omitted and ``attempts`` is provided, a message is
                auto-generated that lists each converter and the
                exception it raised.
            attempts: Ordered list of :class:`FailedConversionAttempt`
                objects, one per converter that was tried.  Pass
                ``None`` (the default) when tracking is unavailable.
        """
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
                        message += (
                            f" - {type(attempt.converter).__name__} threw "
                            f"{attempt.exc_info[0].__name__} with message: "
                            f"{attempt.exc_info[1]}\n"
                        )

        super().__init__(message)
