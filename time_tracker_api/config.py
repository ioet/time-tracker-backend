class Config:
    DEBUG = False


class WhateverDevelopConfig(Config):
    DEBUG = True
    FLASK_DEBUG = True
    FLASK_ENV = "develop"
    DATABASE = "whatever"


DefaultConfig = WhateverDevelopConfig
