import os
from contextlib import ContextDecorator

import odoo
from odoo.tools import config


# pylint: disable=class-camelcase
class replace_exceptions(ContextDecorator):
    """
    Hide some exceptions behind another error. Can be used as a function
    decorator or as a context manager.

    .. code-block:

        @route('/super/secret/route', auth='public')
        @replace_exceptions(AccessError, by=NotFound())
        def super_secret_route(self):
            if not request.session.uid:
                raise AccessError("Route hidden to non logged-in users")
            ...

        def some_util():
            ...
            with replace_exceptions(ValueError, by=UserError("Invalid argument")):
                ...
            ...

    :param exceptions: the exception classes to catch and replace.
    :param by: the exception to raise instead.
    """

    def __init__(self, *exceptions, by):
        if not exceptions:
            raise ValueError("Missing exceptions")

        wrong_exc = next(
            (exc for exc in exceptions if not issubclass(exc, Exception)), None
        )
        if wrong_exc:
            raise TypeError(f"{wrong_exc} is not an exception class.")

        self.exceptions = exceptions
        self.by = by

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None and issubclass(exc_type, self.exceptions):
            raise self.by from exc_value


def file_path(file_path, filter_ext=("",), env=None):
    """Verify that a file exists under a known `addons_path` directory and return its full path.

    Examples::

    >>> file_path('hr')
    >>> file_path('hr/static/description/icon.png')
    >>> file_path('hr/static/description/icon.png', filter_ext=('.png', '.jpg'))

    :param str file_path: absolute file path, or relative path within any `addons_path`
    directory
    :param list[str] filter_ext: optional list of supported extensions (lowercase, with
    leading dot)
    :param env: optional environment, required for a file path within a temporary
    directory
        created using `file_open_temporary_directory()`
    :return: the absolute path to the file
    :raise FileNotFoundError: if the file is not found under the known `addons_path`
    directories
    :raise ValueError: if the file doesn't have one of the supported extensions
    (`filter_ext`)
    """
    root_path = os.path.abspath(config["root_path"])
    addons_paths = odoo.addons.__path__ + [root_path]
    if env and hasattr(env.transaction, "__file_open_tmp_paths"):
        addons_paths += env.transaction.__file_open_tmp_paths
    is_abs = os.path.isabs(file_path)
    normalized_path = os.path.normpath(os.path.normcase(file_path))

    if filter_ext and not normalized_path.lower().endswith(filter_ext):
        raise ValueError("Unsupported file: " + file_path)

    # ignore leading 'addons/' if present, it's the final component of root_path, but
    # may sometimes be included in relative paths
    if normalized_path.startswith("addons" + os.sep):
        normalized_path = normalized_path[7:]

    for addons_dir in addons_paths:
        # final path sep required to avoid partial match
        parent_path = os.path.normpath(os.path.normcase(addons_dir)) + os.sep
        fpath = (
            normalized_path
            if is_abs
            else os.path.normpath(
                os.path.normcase(os.path.join(parent_path, normalized_path))
            )
        )
        if fpath.startswith(parent_path) and os.path.exists(fpath):
            return fpath

    raise FileNotFoundError("File not found: " + file_path)
