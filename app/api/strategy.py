from flask import Blueprint, render_template, redirect, url_for
from sqlalchemy import text
from app.services.db import db  # твоя SQLAlchemy сесія

strategy_bp = Blueprint('strategy', __name__)

@strategy_bp.route('/strategy_dashboard')
def strategy_dashboard():
    rules = db.session.execute(text("SELECT * FROM strategy_rules ORDER BY id")).fetchall()
    conditions = db.session.execute(text("SELECT * FROM strategy_conditions ORDER BY 1")).fetchall()
    sets = db.session.execute(text("SELECT * FROM strategy_sets ORDER BY id")).fetchall()
    weights = db.session.execute(text("SELECT * FROM strategy_weights ORDER BY user_id, exchange, pair")).fetchall()

    return render_template(
        'strategy_dashboard.html',
        rules=rules,
        conditions=conditions,
        sets=sets,
        weights=weights
    )

@strategy_bp.route('/delete_rule/<int:rule_id>', methods=['POST'])
def delete_rule(rule_id):
    db.session.execute(text("DELETE FROM strategy_rules WHERE id = :id"), {"id": rule_id})
    db.session.commit()
    return redirect(url_for('strategy.strategy_dashboard'))
