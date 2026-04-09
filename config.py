import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY","ehfevvhgfvj")

    DB_HOST = os.environ.get("DB_HOST","mysql.railway.internal")
    DB_USER = os.environ.get("DB_USER","root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD","RlZHCZODSwjoBzETSCeVAWQMrtYJWPiV")
    DB_NAME = os.environ.get("DB_NAME","railway")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))

