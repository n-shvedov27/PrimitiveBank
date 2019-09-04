from http import HTTPStatus

from flask import jsonify, request

from . import Session
from . import app
from .models import User
from .utils import validate_json
from .middlewares import handle_exceptions
from .exceptions import UserNotFoundException


@app.route('/api/ping')
@handle_exceptions
def ping():
    return jsonify({
        'status': HTTPStatus.OK,
        'result': True,
        'addition': {},
        "description": {}
    })


@app.route('/api/add', methods=['PATCH'])
@handle_exceptions
def add():
    required_params = {
        'unique_number': str,
        'increase_value': int
    }
    validate_json(request, required_params)

    data = request.get_json()

    unique_number = data['unique_number']
    increase_value = int(data['increase_value'])

    user_info = User.increase_balance(unique_number, increase_value)

    return jsonify({
        'status': HTTPStatus.OK,
        'result': True,
        'addition': user_info,
        "description": {}
    })


@app.route('/api/substract', methods=['PATCH'])
@handle_exceptions
def substract():
    required_params = {
        'unique_number': str,
        'substract_value': int
    }
    validate_json(request, required_params)

    data = request.get_json()

    unique_number = data['unique_number']
    substract_value = int(data['substract_value'])

    user_info = User.substract_balance(unique_number, substract_value)

    return jsonify({
        'status': HTTPStatus.OK,
        'result': True,
        'addition': user_info,
        "description": {}
    })


@app.route('/api/status')
@handle_exceptions
def status():
    required_params = {
        'unique_number': str
    }
    validate_json(request, required_params)

    session = Session()

    data = request.get_json()
    unique_number = data['unique_number']

    user = session.query(User).filter_by(unique_number=unique_number).first()
    if user is None:
        raise UserNotFoundException("Not found user with unique number: {}".format(unique_number))

    return jsonify({
        'status': HTTPStatus.OK,
        'result': True,
        'addition': user.serialize(),
        'description': {}
    })
