import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
metadata = Base.metadata


class Text(Base):
    __tablename__ = 'text_info'
    __table_args__ = {'sqlite_autoincrement': True}

    id = sa.Column('id', sa.Integer, primary_key=True)
    file_name = sa.Column('file_name', sa.String(250), unique=True)
    nausea_ratio = sa.Column('nausea_ratio', sa.Integer)
    is_fraud = sa.Column('is_fraud', sa.Boolean)

    def __init__(self, file_name, nausea_ratio, is_fraud):
        self.file_name = file_name
        self.nausea_ratio = nausea_ratio
        self.is_fraud = is_fraud


def add_data(data):
    engine = sa.create_engine('sqlite:///text_data.db')
    metadata.drop_all(engine)
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    for d in data:
        session.add(Text(file_name=d[0], nausea_ratio=d[1], is_fraud=d[2]))
    session.commit()
