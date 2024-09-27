from app import db
from datetime import datetime

class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference_no = db.Column(db.String(64), unique=True, nullable=False)
    from_bank = db.Column(db.String(64), nullable=False)
    to_bank = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.String(64), nullable=False)
    message_type = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'referenceNo': self.reference_no,
            'from': self.from_bank,
            'to': self.to_bank,
            'amount': self.amount,
            'messageType': self.message_type,
            'status': self.status,
            'lastUpdate': self.last_update.isoformat() + 'Z'
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            reference_no=data['referenceNo'],
            from_bank=data['from'],
            to_bank=data['to'],
            amount=data['amount'],
            message_type=data['messageType'],
            status=data['status']
        )