from .base_exception import BaseServerException


class NotEnoughMoneyException(BaseServerException):
    def __init__(self, message, ):
        super(Exception, self).__init__(message)
