from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Call, CallLog, Customer
from sqlalchemy import desc, func

calls_bp = Blueprint('calls', __name__)

@calls_bp.route('/', methods=['GET'])
@jwt_required()
def get_calls():
    """Get all calls with optional filtering"""
    customer_id = request.args.get('customer_id', type=int)
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    admin_view = request.args.get('admin_view', 'false').lower() == 'true'

    query = Call.query

    if customer_id:
        query = query.filter_by(customer_id=customer_id)

    if status:
        query = query.filter_by(status=status)

    # Order by most recent first
    query = query.order_by(desc(Call.created_at))

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'calls': [call.to_dict(admin_view=admin_view) for call in pagination.items],
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages,
        'per_page': per_page
    }), 200


@calls_bp.route('/<int:call_id>', methods=['GET'])
@jwt_required()
def get_call(call_id):
    """Get a specific call with full details and logs"""
    admin_view = request.args.get('admin_view', 'false').lower() == 'true'
    call = Call.query.get(call_id)

    if not call:
        return jsonify({'error': 'Call not found'}), 404

    return jsonify(call.to_dict(include_logs=True, admin_view=admin_view)), 200


@calls_bp.route('/<int:call_id>/transcript', methods=['GET'])
@jwt_required()
def get_call_transcript(call_id):
    """Get the full transcript of a call"""
    call = Call.query.get(call_id)

    if not call:
        return jsonify({'error': 'Call not found'}), 404

    logs = CallLog.query.filter_by(call_id=call_id).order_by(CallLog.timestamp).all()

    return jsonify({
        'call_id': call_id,
        'transcript': call.transcript,
        'logs': [log.to_dict() for log in logs]
    }), 200


@calls_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_call_stats():
    """Get call statistics"""
    customer_id = request.args.get('customer_id', type=int)
    days = request.args.get('days', 30, type=int)  # Last N days

    from datetime import datetime, timedelta

    start_date = datetime.utcnow() - timedelta(days=days)

    query = Call.query.filter(Call.created_at >= start_date)

    if customer_id:
        query = query.filter_by(customer_id=customer_id)

    total_calls = query.count()

    # Calls by status
    completed_calls = query.filter_by(status='completed').count()
    failed_calls = query.filter_by(status='failed').count()

    # Average duration
    avg_duration = db.session.query(func.avg(Call.duration_seconds)).filter(
        Call.created_at >= start_date
    ).scalar() or 0

    # Callback requests
    callback_requests = query.filter_by(callback_requested=True).count()

    # Total costs
    total_twilio_cost = db.session.query(func.sum(Call.twilio_cost)).filter(
        Call.created_at >= start_date
    ).scalar() or 0

    total_openai_cost = db.session.query(func.sum(Call.openai_cost)).filter(
        Call.created_at >= start_date
    ).scalar() or 0

    return jsonify({
        'period_days': days,
        'total_calls': total_calls,
        'completed_calls': completed_calls,
        'failed_calls': failed_calls,
        'avg_duration_seconds': round(avg_duration, 2),
        'callback_requests': callback_requests,
        'costs': {
            'twilio': round(total_twilio_cost, 2),
            'openai': round(total_openai_cost, 2),
            'total': round(total_twilio_cost + total_openai_cost, 2)
        }
    }), 200


@calls_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_calls():
    """Get most recent calls for dashboard"""
    limit = request.args.get('limit', 10, type=int)
    customer_id = request.args.get('customer_id', type=int)

    query = Call.query

    if customer_id:
        query = query.filter_by(customer_id=customer_id)

    calls = query.order_by(desc(Call.created_at)).limit(limit).all()

    return jsonify({
        'calls': [call.to_dict() for call in calls]
    }), 200
