from flask import jsonify, make_response
from sqlalchemy.exc import SQLAlchemyError
from http import HTTPStatus
import functools
from ..exceptions import (
    InvalidRequestException, NotEnoughMoneyException,
    UserNotFoundException, UserIsBlockedException
)


def handle_exceptions(f):
    @functools.wraps(f)
    def handle_exceptions_wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (InvalidRequestException, NotEnoughMoneyException, UserIsBlockedException, SQLAlchemyError) as e:
            return make_response(jsonify({
                'status': HTTPStatus.BAD_REQUEST,
                'result': False,
                'addition': {'message': str(e)},
                'description': {}
            }, HTTPStatus.BAD_REQUEST))
        except UserNotFoundException:
            return make_response(jsonify({
                'status': HTTPStatus.NOT_FOUND,
                'result': False,
                'addition': {'message': 'user not found'},
                'description': {}
            }, HTTPStatus.NOT_FOUND))

    return handle_exceptions_wrapper
