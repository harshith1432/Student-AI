from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from extensions import db, limiter
from models.task_model import Task, AIResponse, UsageLog
from services.ai_service import generate_ai_response
from services.export_service import generate_pdf, generate_docx, generate_txt
from datetime import datetime

task_bp = Blueprint('task', __name__)

@task_bp.route('/api/tasks/generate', methods=['POST'])
@login_required
@limiter.limit("50 per day")
def generate_task():
    data = request.get_json()
    if not data or not data.get('task_type') or not data.get('prompt'):
        return jsonify({"message": "Missing task_type or prompt"}), 400

    task_type = data['task_type']
    prompt = data['prompt']
    parameters = data.get('parameters', {})

    try:
        # Save Task to DB
        new_task = Task(
            user_id=current_user.id,
            task_type=task_type,
            prompt=prompt,
            parameters=parameters
        )
        db.session.add(new_task)
        db.session.flush() # get new_task.id

        # Call AI Service
        ai_output = generate_ai_response(task_type, prompt, parameters)

        # Save Response to DB
        new_response = AIResponse(
            task_id=new_task.id,
            response_text=ai_output
        )
        db.session.add(new_response)

        # Log usage
        log = UsageLog(
            user_id=current_user.id,
            action=f"generate_{task_type}",
            tokens_used=1 # Mock token usage, in real app get from API response stats
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            "message": "Task completed successfully",
            "task_id": new_task.id,
            "response_id": new_response.id,
            "response": ai_output
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error handling task: {e}")
        return jsonify({"message": "Error processing task", "error": str(e)}), 500


@task_bp.route('/api/tasks/history', methods=['GET'])
@login_required
def get_history():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).limit(50).all()
    history = []
    for t in tasks:
        resp = AIResponse.query.filter_by(task_id=t.id).first()
        history.append({
            "id": t.id,
            "task_type": t.task_type,
            "prompt": t.prompt,
            "created_at": t.created_at.isoformat(),
            "response": resp.response_text if resp else None
        })
    
    return jsonify({"history": history}), 200


@task_bp.route('/api/tasks/export/<int:response_id>', methods=['GET'])
@login_required
def export_file(response_id):
    export_format = request.args.get('format', 'pdf').lower()
    is_handwritten = request.args.get('handwritten', 'false').lower() == 'true'
    
    # Verify ownership
    response_record = AIResponse.query.get(response_id)
    if not response_record:
        return jsonify({"message": "Response not found"}), 404
        
    task = Task.query.get(response_record.task_id)
    if task.user_id != current_user.id:
        return jsonify({"message": "Unauthorized"}), 403

    text_content = response_record.response_text
    
    try:
        if export_format == 'pdf':
            file_data = generate_pdf(text_content, is_handwritten=is_handwritten)
            mimetype = 'application/pdf'
            filename = f"student_ai_{task.task_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        elif export_format == 'docx':
            file_data = generate_docx(text_content)
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            filename = f"student_ai_{task.task_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.docx"
        elif export_format == 'txt':
            file_data = generate_txt(text_content)
            mimetype = 'text/plain'
            filename = f"student_ai_{task.task_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        else:
            return jsonify({"message": "Unsupported format"}), 400

        return send_file(
            file_data,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"Error exporting file: {e}")
        return jsonify({"message": "Export failed", "error": str(e)}), 500
