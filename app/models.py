from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, BigInteger, MetaData
from sqlalchemy.dialects.postgresql import TIMESTAMP

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("user_id", BigInteger, primary_key=True),
    Column("username", String),
    Column("role", String),
    Column("created_at", TIMESTAMP),
    Column("email", String(100)),
    Column("password_hash", String(255))
)

strategy_rules = Table(
    "strategy_rules",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("action", String),
    Column("condition_type", String),
    Column("enabled", Boolean)
)

strategy_conditions = Table(
    "strategy_conditions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("rule_id", Integer, ForeignKey("strategy_rules.id")),
    Column("user_id", Integer),
    Column("exchange", String),
    Column("pair", String),
    Column("action", String),
    Column("condition_name", String),
    Column("enabled", Boolean)
)

strategy_sets = Table(
    "strategy_sets",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer),
    Column("name", String)
)

strategy_weights = Table(
    "strategy_weights",
    metadata,
    Column("user_id", Integer, primary_key=True),
    Column("exchange", String),
    Column("pair", String),
    Column("rsi_weight", Integer),
    Column("forecast_weight", Integer),
    Column("acceleration_weight", Integer),
    Column("trade_logic", String)
)
