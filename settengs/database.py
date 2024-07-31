from settengs.config import Config

ORM = {
    'connections': {
        'default': Config.DB_URL,
    },
    'apps': {
        'models': {
            'models': ['aerich', *Config.DB_MODELS],
            'default_connection': 'default'
        }
    }
}
