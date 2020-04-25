import os
import logging

import sqlalchemy as sa

from db import init_db

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)-8s] %(lineno)-4s <%(funcName)s> - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

DB_URL = os.environ.get("DB_URL")

engine = sa.create_engine(DB_URL) if DB_URL else None
db = init_db(engine=engine)

with db.session():
    user = db.User.get_or_create("iv", first_name="Ivan", last_name="Ivanov")
    user.create_message("Secundus, festus bubos nunquam pugna de bi-color, magnum particula.")
    user.create_message("Cum solitudo cadunt, omnes detriuses perdere neuter, flavum competitiones.")
    user.create_message("Raptus, talis vitas acceleratrix promissio de fidelis, superbus classis.")

with db.session(remove=True):
    user = db.User.get_or_create("iv", first_name="Ivan", last_name="Ivanov")
    user.create_message("Castors sunt solitudos de flavum resistentia.")
    user.create_message("Cum calceus mori, omnes buboes amor primus, superbus burguses.")

with db.session():
    user = db.User.get_or_create("pet", first_name="Petr")
    user.create_message("Candidatus ires, tanquam mirabilis amor.")
    user.create_message("Audax silvas ducunt ad victrix")


for user in db.User.query:
    print(user)
    for msg in user.messages.order_by(db.Message.utc_created_at.asc()):
        print(" {created} - {text}".format(
            created=msg.utc_created_at.strftime("%H:%M:%S.%f"),
            text=msg.text,
        ))
