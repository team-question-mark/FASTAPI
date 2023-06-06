from sqlalchemy import Column, Table
from sqlalchemy.sql.sqltypes import INTEGER, String
from config.db import meta

signLangs = Table('sign_lang', meta,
                  Column('word', String(30), primary_key=True),
                  Column('aniadress',String(255)),
                  )


