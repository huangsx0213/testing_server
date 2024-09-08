from flask import Blueprint, render_template, jsonify, request
from ..services.transfer_service import TransferService

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('table.html')

@main.route('/api/data', methods=['POST'])
def handle_data():
    if not request.json or 'action' not in request.json:
        return jsonify({"error": "Invalid request format"}), 400

    action = request.json['action']

    if action == 'get':
        transfers = TransferService.load_data()
        filtered_data = TransferService.filter_sort_paginate(transfers, request.json)
        return jsonify(filtered_data)
    elif action == 'delete':
        if 'id' not in request.json:
            return jsonify({"error": "No id provided for deletion"}), 400
        TransferService.delete_transfer(request.json['id'])
        return jsonify({"message": "Item deleted successfully"}), 200
    else:
        return jsonify({"error": "Invalid action"}), 400

@main.route('/api/summary', methods=['POST'])
def get_summary():
    transfers = TransferService.load_data()
    summary = TransferService.get_summary(transfers)
    return jsonify(summary)

@main.route('/api/add_item', methods=['POST'])
def add_item():
    new_transfer = TransferService.add_transfer(request.json)
    return jsonify({"message": "Item added successfully", "item": new_transfer.to_dict()}), 201

@main.route('/api/update_item/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    updated_transfer = TransferService.update_transfer(item_id, request.json)
    if updated_transfer:
        return jsonify({"message": "Item updated successfully", "item": updated_transfer.to_dict()}), 200
    return jsonify({"message": "Item not found"}), 404

@main.route('/api/delete_item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    TransferService.delete_transfer(item_id)
    return jsonify({"message": "Item deleted successfully"}), 200

@main.route('/api/bulk_update', methods=['POST'])
def bulk_update():
    update_data = request.json
    TransferService.bulk_update_status(update_data['ids'], update_data['status'])
    return jsonify({"message": "Bulk update successful"}), 200