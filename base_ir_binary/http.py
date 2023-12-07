import base64
import contextlib
import os
from io import BytesIO
from os.path import join as opj
from pathlib import Path
from zlib import adler32

import werkzeug.local
import werkzeug.utils

from odoo.http import STATIC_CACHE_LONG, Response, request, root
from odoo.tools import config

from .misc import file_path

try:
    from werkzeug.utils import send_file as _send_file
except ImportError:
    from odoo.http import send_file as _send_file


class Stream:
    """
    Send the content of a file, an attachment or a binary field via HTTP

    This utility is safe, cache-aware and uses the best available
    streaming strategy. Works best with the --x-sendfile cli option.

    Create a Stream via one of the constructors: :meth:`~from_path`:,
    :meth:`~from_attachment`: or :meth:`~from_binary_field`:, generate
    the corresponding HTTP response object via :meth:`~get_response`:.

    Instantiating a Stream object manually without using one of the
    dedicated constructors is discouraged.
    """

    type: str = ""  # 'data' or 'path' or 'url'
    data = None
    path = None
    url = None

    mimetype = None
    as_attachment = False
    download_name = None
    conditional = True
    etag = True
    last_modified = None
    max_age = None
    immutable = False
    size = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def from_path(cls, path, filter_ext=("",)):
        """Create a :class:`~Stream`: from an addon resource."""
        path = file_path(path, filter_ext)
        check = adler32(path.encode())
        stat = os.stat(path)
        return cls(
            type="path",
            path=path,
            download_name=os.path.basename(path),
            etag=f"{int(stat.st_mtime)}-{stat.st_size}-{check}",
            last_modified=stat.st_mtime,
            size=stat.st_size,
        )

    @classmethod
    def from_attachment(cls, attachment):
        """Create a :class:`~Stream`: from an ir.attachment record."""
        attachment.ensure_one()

        self = cls(
            mimetype=attachment.mimetype,
            download_name=attachment.name,
            conditional=True,
            etag=attachment.checksum,
        )

        if attachment.store_fname:
            self.type = "path"
            self.path = werkzeug.security.safe_join(
                os.path.abspath(config.filestore(request.db)), attachment.store_fname
            )
            stat = os.stat(self.path)
            self.last_modified = stat.st_mtime
            self.size = stat.st_size

        elif attachment.db_datas:
            self.type = "data"
            self.data = attachment.raw
            self.last_modified = attachment["__last_update"]
            self.size = len(self.data)

        elif attachment.url:
            # When the URL targets a file located in an addon, assume it
            # is a path to the resource. It saves an indirection and
            # stream the file right away.
            static_path = root.get_static_file(
                attachment.url, host=request.httprequest.environ.get("HTTP_HOST", "")
            )
            if static_path:
                self = cls.from_path(static_path)
            else:
                self.type = "url"
                self.url = attachment.url

        else:
            self.type = "data"
            self.data = b""
            self.size = 0

        return self

    @classmethod
    def from_binary_field(cls, record, field_name):
        """Create a :class:`~Stream`: from a binary field."""
        data_b64 = record[field_name]
        data = base64.b64decode(data_b64) if data_b64 else b""
        return cls(
            type="data",
            data=data,
            etag=request.env["ir.attachment"]._compute_checksum(data),
            last_modified=record["__last_update"] if record._log_access else None,
            size=len(data),
        )

    # pylint: disable=method-required-super
    def read(self):
        """Get the stream content as bytes."""
        if self.type == "url":
            raise ValueError("Cannot read an URL")

        if self.type == "data":
            return self.data

        with open(self.path, "rb") as file:
            return file.read()

    def get_response(self, as_attachment=None, immutable=None, **send_file_kwargs):
        """
        Create the corresponding :class:`~Response` for the current stream.

        :param bool as_attachment: Indicate to the browser that it
            should offer to save the file instead of displaying it.
        :param bool immutable: Add the ``immutable`` directive to the
            ``Cache-Control`` response header, allowing intermediary
            proxies to aggressively cache the response. This option
            also set the ``max-age`` directive to 1 year.
        :param send_file_kwargs: Other keyword arguments to send to
            :func:`odoo.tools._vendor.send_file.send_file` instead of
            the stream sensitive values. Discouraged.
        """
        assert self.type in (
            "url",
            "data",
            "path",
        ), "Invalid type: {self.type!r}, should be 'url', 'data' or 'path'."
        assert (
            getattr(self, self.type) is not None
        ), "There is nothing to stream, missing {self.type!r} attribute."

        if self.type == "url":
            return request.redirect(self.url, code=301, local=False)

        if as_attachment is None:
            as_attachment = self.as_attachment
        if immutable is None:
            immutable = self.immutable

        send_file_kwargs = {
            "mimetype": self.mimetype,
            "as_attachment": as_attachment,
            "download_name": self.download_name,
            "conditional": self.conditional,
            "etag": self.etag,
            "last_modified": self.last_modified,
            "max_age": STATIC_CACHE_LONG if immutable else self.max_age,
            "environ": request.httprequest.environ,
            "response_class": Response,
            **send_file_kwargs,
        }

        if self.type == "data":
            return _send_file(BytesIO(self.data), **send_file_kwargs)

        # self.type == 'path'
        send_file_kwargs["use_x_sendfile"] = False
        if config["x_sendfile"]:
            with contextlib.suppress(ValueError):  # outside of the filestore
                fspath = Path(self.path).relative_to(
                    opj(config["data_dir"], "filestore")
                )
                x_accel_redirect = f"/web/filestore/{fspath}"
                send_file_kwargs["use_x_sendfile"] = True

        res = _send_file(self.path, **send_file_kwargs)

        if immutable and res.cache_control:
            res.cache_control["immutable"] = None  # None sets the directive

        if "X-Sendfile" in res.headers:
            res.headers["X-Accel-Redirect"] = x_accel_redirect

            # In case of X-Sendfile/X-Accel-Redirect, the body is empty,
            # yet werkzeug gives the length of the file. This makes
            # NGINX wait for content that'll never arrive.
            res.headers["Content-Length"] = "0"

        return res
