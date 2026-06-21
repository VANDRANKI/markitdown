from typing import Optional, List, Any

MISSING_DEPENDENCY_MESSAGE = """{converter} recognized the input as a potential {extension} file, but the dependencies needed to read {extension} files have not been installed. To resolve this error, include the optional dependency [{feature}] or [all] when installing MarkItDown. For example:

* pip install markitdown[{feature}]
* pip install markitdown[all]
* pip install markitdown[{feature}, ...]
* etc."""


class MarkItDownException(Exception):
    """
    Base exception class for all MarkItDown errors.

    Catching this class will capture every exception raised by the library,
    making it useful as a broad safety net in application code::

        from markitdown import MarkItDown, MarkItDownException

        try:
            result = MarkItDown().convert("file.pdf")
        except MarkItDownException as exc:
            print(f"Conversion failed: {exc}")
    """

    pass


class MissingDependencyException(MarkItDownException):
    """
    Raised when a converter requires an optional dependency that is not installed.

    Converters shipped with MarkItDown may depend on optional packages (e.g.
    ``python-docx``, ``pdfminer.six``).  When ``convert()`` is called on a
    converter whose required package is absent, this exception is raised.

    This is *not* necessarily a fatal error for the overall conversion
    pipeline: the :class:`~markitdown.MarkItDown` driver catches this
    exception, skips the failing converter, and attempts any remaining
    converters.  An error only bubbles up to the caller if *no* suitable
    converter succeeds.

    Error messages should clearly state which package is missing and how to
    install it.  Use :data:`MISSING_DEPENDENCY_MESSAGE` as a template.
    """

    pass


class UnsupportedFormatException(MarkItDownException):
    """
    Raised when no registered converter can handle the given file.

    This exception is thrown by :class:`~markitdown.MarkItDown` after all
    converters have declined to accept a file (i.e. every ``accepts()`` call
    returned ``False``).  It signals that the file format is genuinely
    unsupported rather than that a conversion attempt failed mid-way.
    """

    pass


class FailedConversionAttempt:
    """
    Records the outcome of a single, failed converter invocation.

    :class:`FileConversionException` aggregates one or more of these objects
    to provide a detailed audit trail when multiple converters were tried and
    all of them failed.

    Attributes
    ----------
    converter:
        The :class:`~markitdown.DocumentConverter` instance that was invoked.
    exc_info:
        The 3-tuple returned by :func:`sys.exc_info` at the time of failure
        ``(type, value, traceback)``, or ``None`` if no exception information
        was captured.
    """

    def __init__(self, converter: Any, exc_info: Optional[tuple] = None):
        self.converter = converter
        self.exc_info = exc_info


class FileConversionException(MarkItDownException):
    """
    Raised when one or more converters attempted (and failed) to convert a file.

    Unlike :class:`UnsupportedFormatException` (where no converter even tried),
    this exception indicates that at least one converter accepted the file but
    the conversion process itself failed.

    Parameters
    ----------
    message:
        A human-readable description of the failure.  When omitted a message
        is generated automatically from *attempts*.
    attempts:
        An optional list of :class:`FailedConversionAttempt` objects
        describing each converter that was tried and why it failed.  Included
        in the auto-generated message when *message* is ``None``.

    Attributes
    ----------
    attempts:
        The list of :class:`FailedConversionAttempt` objects passed at
        construction time (may be ``None`` if not provided).
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
                message = f"File conversion failed after {len(attempts)} attempt(s):\n"
                for attempt in attempts:
                    if attempt.exc_info is None:
                        message += f" - {type(attempt.converter).__name__} provided no exception info.\n"
                    else:
                        message += (
                            f" - {type(attempt.converter).__name__} raised"
                            f" {attempt.exc_info[0].__name__}: {attempt.exc_info[1]}\n"
                        )

        super().__init__(message)
