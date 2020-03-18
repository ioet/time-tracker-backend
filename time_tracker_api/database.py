"""
Agnostic database assets

Put here your utils and class independent of
the database solution
"""
from flask import Flask

RepositoryModel = None


def init_app(app: Flask) -> None:
    """Make the app ready to use the database"""
    database_strategy_name = app.config['DATABASE']
    with app.app_context():
        module = globals()["use_%s" % database_strategy_name](app)
        global RepositoryModel
        RepositoryModel = module.repository_model


def create(model_name: str):
    """Creates the repository instance for the chosen database"""
    return RepositoryModel(model_name)


def use_sql(app: Flask) -> None:
    from time_tracker_api import sql_repository
    sql_repository.init_app(app)
    return sql_repository
