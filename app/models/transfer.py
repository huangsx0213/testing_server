from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transfer:
    id: int
    reference_no: str
    from_bank: str
    to_bank: str
    amount: str
    message_type: str
    status: str
    last_update: datetime

    @classmethod
    def from_dict(cls, data):
        # 自定义日期解析逻辑
        def parse_date(date_string):
            # 移除 'Z' 后缀，如果存在的话
            date_string = date_string.rstrip('Z')
            # 如果字符串中包含小数秒，将其规范化为 6 位
            if '.' in date_string:
                date_part, time_part = date_string.split('T')
                time_part, ms_part = time_part.split('.')
                ms_part = ms_part[:6].ljust(6, '0')
                date_string = f"{date_part}T{time_part}.{ms_part}"
            return datetime.fromisoformat(date_string)

        return cls(
            id=data['id'],
            reference_no=data['referenceNo'],
            from_bank=data['from'],
            to_bank=data['to'],
            amount=data['amount'],
            message_type=data['messageType'],
            status=data['status'],
            last_update=parse_date(data['lastUpdate'])
        )

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