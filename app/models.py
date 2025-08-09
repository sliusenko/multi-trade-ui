from sqlalchemy import (
    Table, Column, Integer, String, Boolean, ForeignKey,
    BigInteger, MetaData, Float, MetaData, DateTime,
    UniqueConstraint, Text, text
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from datetime import datetime

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("user_id", BigInteger, primary_key=True),
    Column("username", String, nullable=False, unique=True),
    Column("role", String),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("email", String(100)),
    Column("password_hash", String(255)),
)

strategy_rules = Table(
    "strategy_rules",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, nullable=False),
    Column("exchange", String, nullable=False),
    Column("pair", String, nullable=False),
    Column("action", String, nullable=False),
    Column("condition_type", String, nullable=False),
    Column("param_1", Float),
    Column("param_2", Float),
    Column("enabled", Boolean, default=True),
    Column("priority", Integer, default=0),
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
    Column("user_id", Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
    Column("name", String(50), nullable=False),
    Column("description", Text),
    Column("active", Boolean, nullable=False, server_default=text("false")),
    Column("created_at", DateTime, nullable=False, server_default=text("now()")),
    Column("exchange", Text),
    Column("pair", Text),
)

# --- strategy_set_rules ---
strategy_set_rules = Table(
    "strategy_set_rules",
    metadata,
    Column("set_id",  Integer, ForeignKey("strategy_sets.id", ondelete="CASCADE"), nullable=False),
    Column("rule_id", Integer, ForeignKey("strategy_rules.id", ondelete="CASCADE"), nullable=False),
    Column("enabled", Boolean, nullable=False, server_default=text("true")),
    Column("override_priority", Integer),
)

# --- strategy_weights ---
strategy_weights = Table(
    "strategy_weights",
    metadata,
    Column("user_id", Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
    Column("exchange", Text, nullable=False),
    Column("pair", Text, nullable=False),
    Column("rsi_weight",          Float,  server_default=text("1.0")),
    Column("forecast_weight",     Float,  server_default=text("1.0")),
    Column("acceleration_weight", Float,  server_default=text("1.0")),
    Column("trade_logic", Text, server_default=text("'COMBINER'")),
    Column("updated_at", DateTime, nullable=False, server_default=text("now()")),
)

roles = Table(
    "roles",
    metadata,
    Column("role_id", Integer, primary_key=True, index=True),
    Column("name", String(50), unique=True, nullable=False),
    Column("description", String(255), nullable=True),
)

permissions = Table(
    "permissions",
    metadata,
    Column("permission_id", Integer, primary_key=True, index=True),
    Column("name", String(50), unique=True, nullable=False),
    Column("description", String(255), nullable=True),
)

role_permissions = Table(
    "role_permissions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.role_id", ondelete="CASCADE")),
    Column("permission_id", Integer, ForeignKey("permissions.permission_id", ondelete="CASCADE")),
    UniqueConstraint("role_id", "permission_id", name="uix_role_permission")  # Заборона дублікатів
)