import os
from flask import Flask
from extensions import db, login_manager, limiter, csrf
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ---------------------------
    # LOGIN MANAGER CONFIG
    # ---------------------------
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from models.user_model import User
        try:
            return User.query.get(int(user_id))
        except:
            return None

    # ---------------------------
    # INITIALIZE EXTENSIONS
    # ---------------------------
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    # ---------------------------
    # DATABASE INITIALIZATION
    # ---------------------------
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Error executing db.create_all(): {e}")

        # Run schema.sql if exists
        schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                try:
                    from sqlalchemy import text
                    with db.engine.connect() as conn:
                        conn.execute(text(schema_sql))
                        conn.commit()
                except Exception as e:
                    print(f"Error executing schema.sql: {e}")

    # ---------------------------
    # REGISTER BLUEPRINTS
    # ---------------------------
    from routes.main_routes import main_bp
    from routes.auth_routes import auth_bp
    from routes.task_routes import task_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(admin_bp)

    return app


# ============================================================
# 🔥 IMPORTANT: THIS LINE FIXES YOUR GUNICORN ERROR
# ============================================================
try:
    app = create_app()
    print("✅ App created successfully")
except Exception as e:
    print("❌ ERROR CREATING APP:", e)
    raise e


# ============================================================
# LOCAL DEVELOPMENT ONLY
# ============================================================
if __name__ == '__main__':
    app.run(debug=True)
