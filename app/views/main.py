from flask import Blueprint, render_template, jsonify, request, Response
from ..services.transfer_service import TransferService
import xml.etree.ElementTree as ET
from functools import wraps

main = Blueprint('main', __name__)


def support_xml_response(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        result = f(*args, **kwargs)

        if request.headers.get('Accept') == 'application/xml':
            # Convert result to XML
            root = ET.Element('response')

            def dict_to_xml(tag, d):
                elem = ET.Element(tag)
                for key, val in d.items():
                    if isinstance(val, dict):
                        child = dict_to_xml(key, val)
                        elem.append(child)
                    elif isinstance(val, list):
                        for item in val:
                            if isinstance(item, dict):
                                child = dict_to_xml(key, item)
                                elem.append(child)
                            else:
                                child = ET.Element(key)
                                child.text = str(item)
                                elem.append(child)
                    else:
                        child = ET.Element(key)
                        child.text = str(val)
                        elem.append(child)
                return elem

            root = dict_to_xml('response', result)
            xml_string = ET.tostring(root, encoding='unicode')
            return Response(xml_string, mimetype='application/xml')
        else:
            # Return JSON response
            return jsonify(result)

    return decorated_function


@main.route('/')
def index():
    return render_template('table.html')


@main.route('/api/data', methods=['POST'])
@support_xml_response
def handle_data():
    if not request.json or 'action' not in request.json:
        return {"error": "Invalid request format"}

    action = request.json['action']

    if action == 'get':
        transfers = TransferService.load_data()
        filtered_data = TransferService.filter_sort_paginate(transfers, request.json)
        return filtered_data
    elif action == 'delete':
        if 'id' not in request.json:
            return {"error": "No id provided for deletion"}
        TransferService.delete_transfer(request.json['id'])
        return {"message": "Item deleted successfully"}
    else:
        return {"error": "Invalid action"}


@main.route('/api/summary', methods=['POST'])
@support_xml_response
def get_summary():
    transfers = TransferService.load_data()
    summary = TransferService.get_summary()
    return summary


@main.route('/api/add_item', methods=['POST'])
@support_xml_response
def add_item():
    new_transfer = TransferService.add_transfer(request.json)
    return {"message": "Item added successfully", "item": new_transfer.to_dict()}


@main.route('/api/update_item/<int:item_id>', methods=['PUT'])
@support_xml_response
def update_item(item_id):
    updated_transfer = TransferService.update_transfer(item_id, request.json)
    if updated_transfer:
        return {"message": "Item updated successfully", "item": updated_transfer.to_dict()}
    return {"message": "Item not found"}


@main.route('/api/delete_item/<int:item_id>', methods=['DELETE'])
@support_xml_response
def delete_item(item_id):
    TransferService.delete_transfer(item_id)
    return {"message": "Item deleted successfully"}


@main.route('/api/bulk_update', methods=['POST'])
@support_xml_response
def bulk_update():
    update_data = request.json
    TransferService.bulk_update_status(update_data['ids'], update_data['status'])
    return {"message": "Bulk update successful"}