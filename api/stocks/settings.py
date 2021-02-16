import os
from functools import lru_cache
from pydantic import BaseSettings


@lru_cache()
def get_settings():
    return Settings()


class Settings(BaseSettings):
    app_name: str = "stocks"

    @property
    def config(self):
        config = self.__dict__.get('_config')
        if config is None:
            config = {
                "config": "goes here"
            }
            self.__dict__['config'] = config

        return config
