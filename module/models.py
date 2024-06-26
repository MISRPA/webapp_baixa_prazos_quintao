from sqlalchemy import (Column, Integer, String, create_engine, 
                        Boolean, text, Text, DateTime, Table, MetaData)
from sqlalchemy.orm import sessionmaker,declarative_base
from datetime import datetime


Base = declarative_base()
