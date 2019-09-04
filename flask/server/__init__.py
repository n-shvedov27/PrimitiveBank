import atexit
import json
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from server.settingsObject import Settings


def read_config(config_file):
    try:
        with open(config_file) as f:
            data = json.load(f)
    except (OSError, IOError) as e:
        print("Error read settings file: " + config_file)
        sys.exit(1)
    except ValueError as e:
        print("Invalid json format settings file: " + config_file)
        sys.exit(1)
    return data


def db_url(db, data):
    try:
        url = db + '://' + data['user'] \
              + ':' + data['password'] \
              + '@' + data['host'] \
              + ':' + data['port'] \
              + (('/' + data['name']) if 'name' in data else '/')
        return url
    except KeyError as e:
        print("Wrong format config file")
        print("Not found key " + str(e) + " in " + db)
        sys.exit(1)


Base = declarative_base()
settings = Settings(read_config('settings.json'))
engine = create_engine(db_url('postgresql', settings.database))
Session = sessionmaker(bind=engine)

from server.models import User


def clean_holds():
    session = Session()
    try:
        session.connection(execution_options={'isolation_level': 'READ COMMITTED'})

        engine = session.get_bind()
        conn = engine.connect()

        conn.execute(User.__table__.select(True, for_update=True))

        stmt = User.__table__.update(). \
            where(User.balance - User.holds >= 0). \
            values(balance=User.balance - User.holds, holds=0)
        conn.execute(stmt)
    except SQLAlchemyError:
        pass
    finally:
        session.close()


scheduler = BackgroundScheduler()
scheduler.add_job(func=clean_holds, trigger="interval", seconds=600)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

app = Flask(__name__)

Base.metadata.create_all(engine)


def create_test_users():
    session = Session()
    try:
        session.add_all([
            User(unique_number='26c940a1-7228-4ea2-a3bc-e6460b172040', fio='Петров Иван Сергеевич', balance=100, holds=300,
                 status=True),
            User(unique_number='7badc8f8-65bc-449a-8cde-855234ac63e1', fio='Kazitsky Jason', balance=200, holds=200,
                 status=True),
            User(unique_number='5597cc3d-c948-48a0-b711-393edf20d9c0', fio='Пархоменко Антон Александрович', balance=10,
                 holds=300, status=True),
            User(unique_number='867f0924-a917-4711-939b-90b179a96392', fio='Петечкин Петр Измаилович', balance=1000000,
                 holds=1, status=False)
        ])
        session.commit()
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()


create_test_users()

from .views import *
