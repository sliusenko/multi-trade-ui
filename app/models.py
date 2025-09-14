from sqlalchemy import (
    Table, Column, Integer, String, Boolean, ForeignKey,
    BigInteger, Float, MetaData, DateTime, PrimaryKeyConstraint,
    UniqueConstraint, Text, text, Enum, Numeric, Index
)

from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import text, func 
from datetime import datetime

# Якщо в БД enum вже створений:
from sqlalchemy.dialects.postgresql import ENUM

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

user_active_pairs = Table(
    "user_active_pairs",
    metadata,
    Column("user_id", Integer, nullable=False),
    Column("exchange", String, nullable=False),
    Column("pair", String, nullable=False),
    Column("is_active", Boolean, default=True),
    Column("auto_trade_enabled", Boolean, default=True),
)


bot_activity_log = Table(
    "bot_activity_log",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("timestamp", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
    Column("exchange", String, nullable=False),
    Column("pair", String, nullable=False),
    Column("signal", Text, nullable=False),
    Column("comment", Text, nullable=False),
    Column("signal_type", String, nullable=False),
)

forecast_longterm_history = Table(
    "forecast_longterm_history",
    metadata,
    Column("pair", Text, nullable=False),
    Column("timestamp", DateTime(timezone=True), nullable=False),
    Column("predicted_price", Float),
    Column("forecasted_at", DateTime(timezone=True), server_default=text("now()")),
    Column("exchange", Text, nullable=False),
    Column("forecast_delta", Float),
    Column("forecast_acceleration", Float),
    Column("user_id", BigInteger, nullable=False, server_default=text("0")),
    Column("timeframe", Text, nullable=False, server_default=text("'1d'::text")),
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
    Column(
        "set_type",
        ENUM("default", "scalping", "aggressive", "combiner", name="strategy_set_type"),
        nullable=True,
        server_default="default"
    ),
)

# --- strategy_sets_rules ---
strategy_sets_rules = Table(
    "strategy_sets_rules",
    metadata,
    Column("set_id", Integer, ForeignKey("strategy_sets.id", ondelete="CASCADE"), nullable=False),
    Column("rule_id", Integer, ForeignKey("strategy_rules.id", ondelete="CASCADE"), nullable=False),
    Column("enabled", Boolean, nullable=False, server_default=text("true")),
    Column("override_priority", Integer),
    Column("user_id", BigInteger, nullable=False),
    Column("priority", Integer, nullable=False, server_default=text("100")),
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


analysis_data = Table(
    "analysis_data",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("pair", Text, nullable=False),
    Column("exchange", Text, nullable=False),
    Column("user_id", Integer, nullable=False),
    Column("timeframe", Text, nullable=False),
    Column("timestamp", DateTime(timezone=True), nullable=False),

    # ключові поля для графіка
    Column("price", Numeric),

    # (далі — найчастіше використовувані у твоєму UI/боті; за потреби додай інші)
    Column("change", Numeric),
    Column("rsi", Numeric),
    Column("rsi_z", Numeric),
    Column("rsi_z_sell_threshold", Numeric),
    Column("rsi_z_buy_threshold", Numeric),
    Column("volume", Numeric),
    Column("ma_vol_5", Numeric),
    Column("ma_vol_10", Numeric),
    Column("avg_volume", Numeric),
    Column("macd", Numeric),
    Column("macd_signal", Numeric),
    Column("macd_prev", Numeric),
    Column("macd_signal_prev", Numeric),
    Column("sma_50", Numeric),
    Column("sma_200", Numeric),
    Column("volatility", Numeric),
    Column("delta_price", Numeric),
    Column("acceleration", Numeric),
    Column("open", Numeric),
    Column("close", Numeric),
    Column("high", Numeric),
    Column("low", Numeric),
    Column("rsi_period", Integer),
    Column("price_z", Numeric(12, 6)),
    Column("volume_z", Numeric(12, 6)),
    Column("macd_diff_z", Numeric(12, 6)),
    Column("volatility_z", Numeric(12, 6)),
    Column("sma_50_trend", Integer),
    Column("sma_200_trend", Integer),
    Column("sma_50_trend_strength", Float),
    Column("sma_200_trend_strength", Float),
    Column("bb_period", Integer),
    Column("adx", Numeric),
    Column("plus_di", Numeric),
    Column("minus_di", Numeric),

    # у тебе в БД є унікальний ключ на (pair, exchange, user_id, timeframe, timestamp)
    UniqueConstraint(
        "pair", "exchange", "user_id", "timeframe", "timestamp",
        name="analysis_data_pair_exchange_user_id_timeframe_timestamp_key"
    ),
)

# індекси як на скрінах
Index(
    "idx_ad_user_pair_tf_ts",
    analysis_data.c.user_id,
    analysis_data.c.exchange,
    analysis_data.c.pair,
    analysis_data.c.timeframe,
    analysis_data.c.timestamp.desc(),
)
Index(
    "idx_analysis_data_price_z",
    analysis_data.c.pair,
    analysis_data.c.exchange,
    analysis_data.c.timeframe,
    analysis_data.c.price_z,
)
Index(
    "idx_analysis_data_sma_trends",
    analysis_data.c.pair,
    analysis_data.c.exchange,
    analysis_data.c.timeframe,
    analysis_data.c.sma_50_trend,
    analysis_data.c.sma_200_trend,
)
Index(
    "idx_analysis_data_ts_brin",
    analysis_data.c.timestamp,
    postgresql_using="brin",
    postgresql_with={"pages_per_range": "32"},
)
# часткові індекси по конкретних таймфреймах
Index(
    "idx_analysis_15m",
    analysis_data.c.user_id,
    analysis_data.c.exchange,
    analysis_data.c.pair,
    analysis_data.c.timestamp.desc(),
    postgresql_where=(analysis_data.c.timeframe == text("'15m'::text")),
)
Index(
    "idx_analysis_5m",
    analysis_data.c.user_id,
    analysis_data.c.exchange,
    analysis_data.c.pair,
    analysis_data.c.timestamp.desc(),
    postgresql_where=(analysis_data.c.timeframe == text("'5m'::text")),
)