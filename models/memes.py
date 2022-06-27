from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class Memes(Model):
    image = fields.TextField(pk=True)
    credit = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)


MemeResponse = pydantic_model_creator(Memes, name="Meme")
