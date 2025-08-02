from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, MetaData

metadata = MetaData()

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
    Column("rule_id", Integer, ForeignKey("strategy_rules.id")),  # ✅ правильно
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
