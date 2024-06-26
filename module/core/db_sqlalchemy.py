
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import pandas as pd


class Database:
    def __init__(self, Session : sessionmaker) -> None:
        self.session = Session()
    
    def update(self, record_id, table,**kwargs):
        try:
            self.session.begin()
            record = self.session.query(table).filter_by(id=record_id).with_for_update().first()
            for field, value in kwargs.items():
                setattr(record, field, value)
            self.session.commit()
            return self.session.execute(text("SELECT @@ROWCOUNT")).scalar()

        except Exception as e:
            self.session.rollback()
            raise e

        finally: self.session.close()

    def insert(self, table, **kwargs):
        try:
            self.session.begin()
            new_record = table(**kwargs)
            self.session.add(new_record)
            self.session.commit()
            return self.session.execute(text("SELECT @@ROWCOUNT")).scalar()

        except Exception as e:
            self.session.rollback()
            raise e

        finally: self.session.close()
    
    def select_to_dataframe(self, query):
        try:
            self.session.begin()
            affected_rows = self.session.execute(text(query))
            dados = affected_rows.all()
            return pd.DataFrame(list(dados),columns=list(affected_rows.keys()))

        except Exception as e:
            raise e

        finally: self.session.close()

    def run_query(self, query,values=None):
        try:
            self.session.begin()
            self.session.execute(text(query),values)
            self.session.commit()

            return self.session.execute(text("SELECT @@ROWCOUNT")).scalar()

        except Exception as e:
            self.session.rollback()
            raise e

        finally: self.session.close()

    def bulk_insert_df(self, df, table):
        try:
            self.session.begin()
            self.session.bulk_insert_mappings(table, df.to_dict(orient='records'))
            self.session.commit()
            return self.session.execute(text("SELECT @@ROWCOUNT")).scalar()

        except Exception as e:
            self.session.rollback()
            raise e

        finally: self.session.close()