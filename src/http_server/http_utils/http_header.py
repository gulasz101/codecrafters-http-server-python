from enum import Enum


class HttpHeader(Enum):
    CONTENT_TYPE = "Content-Type"
    CONTENT_LENGTH = "Content-Length"
    CONTENT_ENCODING = "Content-Encoding"
    USER_AGENT = "User-Agent"
    ACCEPT = "Accept"
    ACCEPT_ENCODING = "Accept-Encoding"
