# -*- coding: utf-8 -*-
"""
Web Server for Tooling IO Management System
"""

import os
import sys
import logging
from flask import Flask, request, jsonify, render_template

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import config
try:
    from config.settings import settings
    FLASK_HOST = settings.FLASK_HOST
    FLASK_PORT = settings.FLASK_PORT
    FLASK_DEBUG = settings.FLASK_DEBUG
    SECRET_KEY = settings.SECRET_KEY
except ImportError:
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'tooling-io-secret-key')

# Create Flask app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = SECRET_KEY


def _parse_positive_int_arg(arg_name: str, default: int) -> int:
    """Parse positive integer query argument."""
    raw_value = request.args.get(arg_name, default)
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{arg_name} must be an integer") from exc

    if value <= 0:
        raise ValueError(f"{arg_name} must be greater than 0")

    return value


def _get_json_dict(required: bool = False):
    """Return request JSON body as a dict."""
    data = request.get_json(silent=True)
    if required and data is None:
        raise ValueError('request body must be a JSON object')
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError('request body must be a JSON object')
    return data


def _validation_error(message: str):
    return jsonify({'success': False, 'error': message}), 400


# ========================================
# Tool IO Management API
# ========================================

@app.route('/api/tool-io-orders', methods=['GET'])
def api_tool_io_orders_list():
    """鏌ヨ鍑哄叆搴撳崟鍒楄〃"""
    try:
        from backend.services.tool_io_service import list_orders

        result = list_orders({
            'order_type': request.args.get('order_type'),
            'order_status': request.args.get('order_status'),
            'initiator_id': request.args.get('initiator_id'),
            'keeper_id': request.args.get('keeper_id'),
            'keyword': request.args.get('keyword'),
            'date_from': request.args.get('date_from'),
            'date_to': request.args.get('date_to'),
            'page_no': _parse_positive_int_arg('page_no', 1),
            'page_size': _parse_positive_int_arg('page_size', 20)
        })

        return jsonify(result)
    except ValueError as e:
        return _validation_error(str(e))
    except Exception as e:
        logger.error(f"鏌ヨ鍑哄叆搴撳崟鍒楄〃澶辫触: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tool-io-orders', methods=['POST'])
def api_tool_io_orders_create():
    """鍒涘缓鍑哄叆搴撳崟"""
    try:
        from backend.services.tool_io_service import create_order

        data = _get_json_dict(required=True)
        result = create_order(data)

        if result.get('success'):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except ValueError as e:
        return _validation_error(str(e))
    except Exception as e:
        logger.error(f"鍒涘缓鍑哄叆搴撳崟澶辫触: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tool-io-orders/<order_no>', methods=['GET'])
def api_tool_io_order_detail(order_no):
    """鑾峰彇鍑哄叆搴撳崟璇︽儏"""
    try:
        from backend.services.tool_io_service import get_order_detail

        order = get_order_detail(order_no)
        if not order:
            return jsonify({'success': False, 'error': 'order not found'}), 404

        return jsonify({'success': True, 'data': order})
    except Exception as e:
        logger.error(f"鑾峰彇鍑哄叆搴撳崟璇︽儏澶辫触: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tool-io-orders/<order_no>/submit', methods=['POST'])
def api_tool_io_order_submit(order_no):
    """鎻愪氦鍑哄叆搴撳崟"""
    try:
        from backend.services.tool_io_service import submit_order

        data = _get_json_dict(required=True)
        if not data.get('operator_id') or not data.get('operator_name') or not data.get('operator_role'):
            return _validation_error('operator_id, operator_name and operator_role are required')

        result = submit_order(order_no, data)

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
    except ValueError as e:
        return _validation_error(str(e))
    except Exception as e:
        logger.error(f"鎻愪氦鍑哄叆搴撳崟澶辫触: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tool-io-orders/<order_no>/keeper-confirm', methods=['POST'])
def api_tool_io_order_keeper_confirm(order_no):
    """Keeper confirmation endpoint."""
    try:
        from backend.services.tool_io_service import keeper_confirm

        data = _get_json_dict(required=True)
        if not data.get('keeper_id') or not data.get('keeper_name'):
            return _validation_error('keeper_id and keeper_name are required')
        if not isinstance(data.get('items'), list):
            return _validation_error('items must be a JSON array')

        result = keeper_confirm(order_no, data)

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
    except ValueError as e:
        return _validation_error(str(e))
    except Exception as e:
        logger.error(f"淇濈鍛樼‘璁ゅけ璐? {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tool-io-orders/<order_no>/final-confirm', methods=['POST'])
def api_tool_io_order_final_confirm(order_no):
    """Final confirmation endpoint."""
    try:
        from backend.services.tool_io_service import final_confirm

        data = _get_json_dict(required=True)
        if not data.get('operator_id') or not data.get('operator_name') or not data.get('operator_role'):
            return _validation_error('operator_id, operator_name and operator_role are required')

        result = final_confirm(order_no, data)

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
    except ValueError as e:
        return _validation_error(str(e))
    except Exception as e:
        logger.error(f"鏈€缁堢‘璁ゅけ璐? {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tool-io-orders/<order_no>/final-confirm-availability', methods=['GET'])
def api_tool_io_order_final_confirm_availability(order_no):
    """Query whether final confirmation is currently available."""
    try:
        from backend.services.tool_io_service import get_final_confirm_availability

        result = get_final_confirm_availability(
            order_no,
            request.args.get('operator_id', ''),
            request.args.get('operator_role', ''),
        )

        if result.get('success'):
            return jsonify(result)
        return jsonify(result), 404
    except Exception as e:
        logger.error(f"鏈€缁堢‘璁ゅ彲鐢ㄦ€ф煡璇㈠け璐? {e}")
        return jsonify({'success': False, 'error': str(e), 'available': False}), 500


@app.route('/api/tool-io-orders/<order_no>/reject', methods=['POST'])
def api_tool_io_order_reject(order_no):
    """椹冲洖鍗曟嵁"""
    try:
        from backend.services.tool_io_service import reject_order

        data = _get_json_dict(required=True)
        if not data.get('reject_reason'):
            return _validation_error('reject_reason is required')
        if not data.get('operator_id') or not data.get('operator_name') or not data.get('operator_role'):
            return _validation_error('operator_id, operator_name and operator_role are required')

        result = reject_order(order_no, data)

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
    except ValueError as e:
        return _validation_error(str(e))
    except Exception as e:
        logger.error(f"椹冲洖鍗曟嵁澶辫触: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tool-io-orders/<order_no>/cancel', methods=['POST'])
def api_tool_io_order_cancel(order_no):
    """鍙栨秷鍗曟嵁"""
    try:
        from backend.services.tool_io_service import cancel_order

        data = _get_json_dict(required=True)
        if not data.get('operator_id') or not data.get('operator_name') or not data.get('operator_role'):
            return _validation_error('operator_id, operator_name and operator_role are required')

        result = cancel_order(order_no, data)

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
    except ValueError as e:
        return _validation_error(str(e))
    except Exception as e:
        logger.error(f"鍙栨秷鍗曟嵁澶辫触: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tool-io-orders/<order_no>/logs', methods=['GET'])
def api_tool_io_order_logs(order_no):
    """鑾峰彇鎿嶄綔鏃ュ織"""
    try:
        from backend.services.tool_io_service import get_order_logs

        logs = get_order_logs(order_no)
        return jsonify({'success': True, 'data': logs})
    except Exception as e:
        logger.error(f"鑾峰彇鎿嶄綔鏃ュ織澶辫触: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tool-io-orders/<order_no>/notification-records', methods=['GET'])
def api_tool_io_order_notification_records(order_no):
    """Return notification records for one order."""
    try:
        from backend.services.tool_io_service import get_notification_records

        result = get_notification_records(order_no)
        if result.get('success'):
            return jsonify(result)
        return jsonify(result), 404
    except Exception as e:
        logger.error(f'failed to load notification records for {order_no}: {e}')
        return jsonify({'success': False, 'error': str(e), 'data': []}), 500

@app.route('/api/tool-io-orders/pending-keeper', methods=['GET'])
def api_tool_io_orders_pending_keeper():
    """Return pending keeper orders."""
    try:
        from backend.services.tool_io_service import get_pending_keeper_list

        orders = get_pending_keeper_list(request.args.get('keeper_id'))

        return jsonify({'success': True, 'data': orders})
    except Exception as e:
        logger.error(f"鑾峰彇寰呯‘璁ゅ崟鎹け璐? {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tools/search', methods=['GET'])
def api_tools_search():
    """宸ヨ鎼滅储"""
    try:
        from backend.services.tool_io_service import search_tool_inventory

        result = search_tool_inventory({
            'keyword': request.args.get('keyword'),
            'status': request.args.get('status'),
            'location': request.args.get('location'),
            'location_id': request.args.get('location_id'),
            'page_no': _parse_positive_int_arg('page_no', 1),
            'page_size': _parse_positive_int_arg('page_size', 20)
        })

        return jsonify(result)
    except ValueError as e:
        return _validation_error(str(e))
    except Exception as e:
        logger.error(f"宸ヨ鎼滅储澶辫触: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tools/batch-query', methods=['POST'])
def api_tools_batch_query():
    """鎵归噺鏌ヨ宸ヨ"""
    try:
        from backend.services.tool_io_service import batch_query_tools

        data = _get_json_dict(required=True)
        tool_codes = data.get('tool_codes')
        if not isinstance(tool_codes, list):
            return _validation_error('tool_codes must be a JSON array')

        result = batch_query_tools(tool_codes)
        if result.get('success'):
            return jsonify(result)
        return jsonify(result), 400
    except ValueError as e:
        return _validation_error(str(e))
    except Exception as e:
        logger.error(f"鎵归噺鏌ヨ宸ヨ澶辫触: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tool-io-orders/<order_no>/generate-keeper-text', methods=['GET'])
def api_generate_keeper_text(order_no):
    """鐢熸垚淇濈鍛樼粨鏋勫寲鏂囨湰"""
    try:
        from backend.services.tool_io_service import generate_keeper_text

        result = generate_keeper_text(order_no)
        if result.get('success'):
            return jsonify(result)
        return jsonify(result), 404 if result.get('error') == 'order not found' else 400
    except Exception as e:
        logger.error(f"鐢熸垚淇濈鍛樻枃鏈け璐? {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tool-io-orders/<order_no>/generate-transport-text', methods=['GET'])
def api_generate_transport_text(order_no):
    """鐢熸垚杩愯緭閫氱煡鏂囨湰"""
    try:
        from backend.services.tool_io_service import generate_transport_text

        result = generate_transport_text(order_no)
        if result.get('success'):
            return jsonify(result)
        return jsonify(result), 404 if result.get('error') == 'order not found' else 400
    except Exception as e:
        logger.error(f"鐢熸垚杩愯緭鏂囨湰澶辫触: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tool-io-orders/<order_no>/notify-transport', methods=['POST'])
def api_notify_transport(order_no):
    """Send transport notification via Feishu"""
    try:
        from backend.services.tool_io_service import notify_transport

        data = _get_json_dict()
        result = notify_transport(order_no, data)
        if result.get('success'):
            return jsonify(result)
        error = result.get('error')
        if error == 'order not found':
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as e:
        return _validation_error(str(e))
    except Exception as e:
        logger.error(f"Transport notification failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tool-io-orders/<order_no>/notify-keeper', methods=['POST'])
def api_notify_keeper(order_no):
    """Send keeper request notification via Feishu"""
    try:
        from backend.services.tool_io_service import notify_keeper
        data = _get_json_dict()
        result = notify_keeper(order_no, data)
        if result.get('success'):
            return jsonify(result)
        error = result.get('error')
        if error == 'order not found':
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as e:
        return _validation_error(str(e))
    except Exception as e:
        logger.error(f"Keeper notification failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# 椤甸潰璺敱
@app.route('/inventory')
def inventory_page():
    """Inventory list page"""
    return render_template('inventory_list.html')


@app.route('/inventory/create')
def inventory_create_page():
    """Create order page"""
    return render_template('inventory_form.html')


@app.route('/inventory/<order_no>')
def inventory_detail_page(order_no):
    """Order detail page"""
    return render_template('inventory_detail.html')


@app.route('/inventory/keeper')
def inventory_keeper_page():
    """Keeper workbench page"""
    return render_template('inventory_keeper.html')


# ========================================
# Health Check
# ========================================

@app.route('/api/health')
def api_health():
    """Health check"""
    try:
        from database import test_db_connection
        db_ok, db_msg = test_db_connection()
        status_code = 200 if db_ok else 503
        return jsonify({
            'status': 'ok' if db_ok else 'error',
            'database': db_msg
        }), status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/db/test')
def api_db_test():
    """Database connection test"""
    try:
        from database import test_db_connection
        ok, msg = test_db_connection()
        return jsonify({'success': ok, 'message': msg})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========================================
# Main Entry
# ========================================

if __name__ == '__main__':
    logger.info(f"鍚姩宸ヨ鍑哄叆搴撶鐞嗙郴缁? {FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)

