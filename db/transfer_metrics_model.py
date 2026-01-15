from sqlalchemy import Column, Integer, BigInteger, Float, Text, DateTime, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

class TransferMetrics(Base):
    __tablename__ = 'transfer_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(Text, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(Text)

    total_transfer_time = Column(Float, nullable=False)
    throughput = Column(Float, nullable=False)
    peak_throughput = Column(Float, nullable=False)

    transfer_byte_difference = Column(Integer)
    transfer_status = Column(Text, nullable=False)

    cpu_usage_avg = Column(Float)
    cpu_usage_peak = Column(Float)
    ram_usage_avg = Column(Float)
    ram_usage_peak = Column(Float)

    timestamp = Column(DateTime(timezone=True), default=func.now())

