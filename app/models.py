from app.services.db import db

class StrategyRule(db.Model):
    __tablename__ = "strategy_rules"
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50))
    condition_type = db.Column(db.String(50))
    enabled = db.Column(db.Boolean)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
