import os
from flask import Flask
from extensions import db, login_manager, limiter, csrf
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from models.user_model import User
        try:
            return User.query.get(int(user_id))
        except:
            return None

    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    # Initialize database
    with app.app_context():
        # First let Flask-SQLAlchemy create mapped tables (useful fallback)
        try:
            db.create_all()
        except Exception as e:
            print(f"Error executing db.create_all(): {e}")

        # Also execute our schema.sql manually to ensure our custom schema is loaded correctly
        schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                try:
                    from sqlalchemy import text
                    # Using SQLAlchemy core connection to execute raw SQL
                    with db.engine.connect() as conn:
                        conn.execute(text(schema_sql))
                        conn.commit()
                except Exception as e:
                    print(f"Error executing schema.sql: {e}")

    # Register Blueprints later
    from routes.main_routes import main_bp
    from routes.auth_routes import auth_bp
    from routes.task_routes import task_bp
    from routes.admin_routes import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(admin_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
