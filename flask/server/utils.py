from flask import Request
from json.decoder import JSONDecodeError
from .exceptions import InvalidRequestException
from typing import Dict

def validate_json(request: Request, params: Dict):
    try:
        data = request.get_json()
    except JSONDecodeError:
        raise InvalidRequestException('invalid json')

    difference = set(params.keys()). \
        difference(set(data.keys()))
    if difference:
        raise InvalidRequestException("{} missing".format(difference))

    for param, type in params.items():
        if not isinstance(data[param], type):
            raise InvalidRequestException("{} must be {}".format(param, str(type)))
