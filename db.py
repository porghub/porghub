import os

TORTOISE_ORM = {
    "connections": {"default": "sqlite://credits.db"},
    "apps": {"models": {"models": ["aerich.models", "models.memes"]}},
}
