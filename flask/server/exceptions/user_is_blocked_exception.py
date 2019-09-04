from .base_exception import BaseServerException


class UserIsBlockedException(BaseServerException):
    def __init__(self, message, ):
        super(Exception, self).__init__(message)
