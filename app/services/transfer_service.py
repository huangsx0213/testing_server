import json
from flask import current_app
from ..models.transfer import Transfer
from datetime import datetime

class TransferService:
    @classmethod
    def load_data(cls):
        try:
            with open(current_app.config['JSON_DATA_PATH'], 'r') as f:
                data = json.load(f)
                return [Transfer.from_dict(item) for item in data['data']]
        except FileNotFoundError:
            return []

    @classmethod
    def save_data(cls, transfers):
        data = {'data': [transfer.to_dict() for transfer in transfers]}
        with open(current_app.config['JSON_DATA_PATH'], 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def filter_sort_paginate(cls, transfers, params):
        # Apply filtering
        if 'filter' in params:
            transfers = [t for t in transfers if cls.apply_filter(t, params['filter'])]

        # Apply sorting
        if 'sort' in params:
            reverse = params['sort']['order'] == 'desc'
            field = params['sort']['field']
            field_mapping = {
                'referenceNo': 'reference_no',
                'from': 'from_bank',
                'to': 'to_bank',
                'amount': 'amount',
                'messageType': 'message_type',
                'status': 'status',
                'lastUpdate': 'last_update'
            }
            transfers.sort(key=lambda x: getattr(x, field_mapping.get(field, field)), reverse=reverse)

        # Calculate pagination
        page = int(params.get('page', 1))
        items_per_page = int(params.get('itemsPerPage', 10))
        total_items = len(transfers)
        total_pages = (total_items + items_per_page - 1) // items_per_page

        # Apply pagination
        start = (page - 1) * items_per_page
        end = start + items_per_page
        paginated_data = transfers[start:end]

        return {
            'data': [t.to_dict() for t in paginated_data],
            'totalItems': total_items,
            'totalPages': total_pages,
            'currentPage': page
        }

    @classmethod
    def apply_filter(cls, transfer, filter_params):
        for key, value in filter_params.items():
            if key == 'status' and value and transfer.status != value:
                return False
            if key == 'minAmount' and value and float(transfer.amount.replace('$', '').replace(',', '')) < float(value):
                return False
            if key == 'maxAmount' and value and float(transfer.amount.replace('$', '').replace(',', '')) > float(value):
                return False
        return True

    @staticmethod
    def get_summary(transfers):
        total_amount = sum(float(t.amount.replace('$', '').replace(',', '')) for t in transfers)
        total_count = len(transfers)
        active_transfers = [t for t in transfers if t.status == 'Active']
        inactive_transfers = [t for t in transfers if t.status == 'Inactive']
        active_amount = sum(float(t.amount.replace('$', '').replace(',', '')) for t in active_transfers)
        inactive_amount = sum(float(t.amount.replace('$', '').replace(',', '')) for t in inactive_transfers)

        return {
            'totalAmount': round(total_amount, 2),
            'totalCount': total_count,
            'activeAmount': round(active_amount, 2),
            'inactiveAmount': round(inactive_amount, 2),
            'activeCount': len(active_transfers),
            'inactiveCount': len(inactive_transfers)
        }

    @staticmethod
    def add_transfer(transfer_data):
        transfers = TransferService.load_data()
        new_id = max([t.id for t in transfers] + [0]) + 1
        new_transfer = Transfer(
            id=new_id,
            reference_no=transfer_data['referenceNo'],
            from_bank=transfer_data['from'],
            to_bank=transfer_data['to'],
            amount=transfer_data['amount'],
            message_type=transfer_data['messageType'],
            status=transfer_data['status'],
            last_update=datetime.now()
        )
        transfers.append(new_transfer)
        TransferService.save_data(transfers)
        return new_transfer

    @staticmethod
    def update_transfer(transfer_id, transfer_data):
        transfers = TransferService.load_data()
        for i, transfer in enumerate(transfers):
            if transfer.id == transfer_id:
                transfers[i] = Transfer(
                    id=transfer_id,
                    reference_no=transfer_data['referenceNo'],
                    from_bank=transfer_data['from'],
                    to_bank=transfer_data['to'],
                    amount=transfer_data['amount'],
                    message_type=transfer_data['messageType'],
                    status=transfer_data['status'],
                    last_update=datetime.now()
                )
                TransferService.save_data(transfers)
                return transfers[i]
        return None

    @staticmethod
    def delete_transfer(transfer_id):
        transfers = TransferService.load_data()
        transfers = [t for t in transfers if t.id != transfer_id]
        TransferService.save_data(transfers)

    @staticmethod
    def bulk_update_status(ids, status):
        transfers = TransferService.load_data()
        for transfer in transfers:
            if transfer.id in ids:
                transfer.status = status
                transfer.last_update = datetime.now()
        TransferService.save_data(transfers)