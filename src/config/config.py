import os
from typing import Final



class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Config(metaclass=SingletonMeta):
    """Config class to load environment variables."""

    _NAME: Final = "config"

    def __init__(self):
        self._load_config()

    def _load_config(self):
        """ Load environment variables. """
        self.ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
        self.PROVIEW_CAQH_ORG_URL: str = os.environ.get(
            "PROVIEW_CAQH_ORG_URL", "")
        self.CAQH_USER_NAME: str = os.environ.get("CAQH_USER_NAME", "")
        self.CAQH_USER_PASSWORD: str = os.environ.get("CAQH_USER_PASSWORD", "")
        self.PORT: int = int(os.environ.get('PORT', "8000"))
        self.BUCKET_NAME: str = os.environ.get('BUCKET_NAME', '')
        self.BUCKET_REGION: str = os.environ.get('BUCKET_REGION', 'sfo3')
        self.BUCKET_ENV: str = os.environ.get('BUCKET_ENV', 'dev')
        self.ACCESS_KEY: str = os.environ.get('ACCESS_KEY', '')
        self.SECRET_KEY: str = os.environ.get('SECRET_KEY', '')

        try:
            self._verify()
        except ValueError as e:
            print(e)

    def _verify(self):
        """ Verify that all required environment variables are set. """

        if self.ENVIRONMENT == "development":
            return

        ATTRIBUTES_TO_VERIFY = [
            "PROVIEW_CAQH_ORG_URL",
        ]

        # Verify that all attributes are set
        for attr_name in ATTRIBUTES_TO_VERIFY:
            # Get attribute
            attr = getattr(self, attr_name)

            # Verify attributes
            if isinstance(attr, str) and attr.strip():  # type: ignore
                pass
            elif not attr:
                raise ValueError(f"{attr_name} is not set")
