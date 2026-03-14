from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.user_model import User
from models.task_model import Task, UsageLog
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

# Basic mock role check since schema didn't include role column.
# In a real app we'd add `role = db.Column(db.String)` to users table.
# Here we'll just allow any logged in user as an example, but restrict if needed.
def is_admin():
    # Example: return current_user.username == 'admin'
    # Returning True for dev purposes
    return True

@admin_bp.route('/api/admin/stats', methods=['GET'])
@login_required
def get_stats():
    if not is_admin():
        return jsonify({"message": "Forbidden"}), 403

    total_users = User.query.count()
    total_tasks = Task.query.count()
    
    # Get breakdown of task types
    task_breakdown = db.session.query(
        Task.task_type, func.count(Task.id)
    ).group_by(Task.task_type).all()
    breakdown_dict = {t[0]: t[1] for t in task_breakdown}

    return jsonify({
        "total_users": total_users,
        "total_tasks": total_tasks,
        "task_breakdown": breakdown_dict
    }), 200

@admin_bp.route('/api/admin/users', methods=['GET'])
@login_required
def get_users():
    if not is_admin():
        return jsonify({"message": "Forbidden"}), 403

    users = User.query.all()
    return jsonify({
        "users": [u.to_dict() for u in users]
    }), 200
