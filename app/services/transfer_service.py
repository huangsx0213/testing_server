from datetime import datetime
from app import db
from app.models.transfer import Transfer
from sqlalchemy import func

class TransferService:
    @staticmethod
    def load_data():
        return Transfer.query.all()

    @staticmethod
    def filter_sort_paginate(params):
        query = Transfer.query

        # Apply filtering
        if 'filter' in params:
            filter_params = params['filter']
            if 'status' in filter_params and filter_params['status']:
                query = query.filter(Transfer.status == filter_params['status'])
            if 'minAmount' in filter_params and filter_params['minAmount']:
                query = query.filter(func.cast(Transfer.amount, db.Float) >= float(filter_params['minAmount']))
            if 'maxAmount' in filter_params and filter_params['maxAmount']:
                query = query.filter(func.cast(Transfer.amount, db.Float) <= float(filter_params['maxAmount']))

        # Apply sorting
        if 'sort' in params:
            sort_field = params['sort']['field']
            sort_order = params['sort']['order']
            if hasattr(Transfer, sort_field):
                if sort_order == 'desc':
                    query = query.order_by(getattr(Transfer, sort_field).desc())
                else:
                    query = query.order_by(getattr(Transfer, sort_field))

        # Apply pagination
        page = int(params.get('page', 1))
        items_per_page = int(params.get('itemsPerPage', 10))
        pagination = query.paginate(page=page, per_page=items_per_page, error_out=False)

        return {
            'data': [item.to_dict() for item in pagination.items],
            'totalItems': pagination.total,
            'totalPages': pagination.pages,
            'currentPage': page
        }

    @staticmethod
    def get_summary():
        total_count = Transfer.query.count()
        total_amount = db.session.query(func.sum(func.cast(Transfer.amount, db.Float))).scalar() or 0
        active_transfers = Transfer.query.filter_by(status='Active')
        inactive_transfers = Transfer.query.filter_by(status='Inactive')
        active_count = active_transfers.count()
        inactive_count = inactive_transfers.count()
        active_amount = active_transfers.with_entities(func.sum(func.cast(Transfer.amount, db.Float))).scalar() or 0
        inactive_amount = inactive_transfers.with_entities(func.sum(func.cast(Transfer.amount, db.Float))).scalar() or 0

        return {
            'totalAmount': round(total_amount, 2),
            'totalCount': total_count,
            'activeAmount': round(active_amount, 2),
            'inactiveAmount': round(inactive_amount, 2),
            'activeCount': active_count,
            'inactiveCount': inactive_count
        }

    @staticmethod
    def add_transfer(transfer_data):
        new_transfer = Transfer.from_dict(transfer_data)
        db.session.add(new_transfer)
        db.session.commit()
        return new_transfer

    @staticmethod
    def update_transfer(transfer_id, transfer_data):
        transfer = Transfer.query.get(transfer_id)
        if transfer:
            transfer.reference_no = transfer_data['referenceNo']
            transfer.from_bank = transfer_data['from']
            transfer.to_bank = transfer_data['to']
            transfer.amount = transfer_data['amount']
            transfer.message_type = transfer_data['messageType']
            transfer.status = transfer_data['status']
            transfer.last_update = datetime.utcnow()
            db.session.commit()
            return transfer
        return None

    @staticmethod
    def delete_transfer(transfer_id):
        transfer = Transfer.query.get(transfer_id)
        if transfer:
            db.session.delete(transfer)
            db.session.commit()

    @staticmethod
    def bulk_update_status(ids, status):
        Transfer.query.filter(Transfer.id.in_(ids)).update({Transfer.status: status}, synchronize_session=False)
        db.session.commit()

    @staticmethod
    def get_max_reference_no():
        max_ref = db.session.query(func.max(Transfer.reference_no)).scalar()
        if max_ref:
            max_num = int(max_ref.replace('REF', ''))
            return f'REF{str(max_num + 1).zfill(4)}'
        else:
            return 'REF0001'