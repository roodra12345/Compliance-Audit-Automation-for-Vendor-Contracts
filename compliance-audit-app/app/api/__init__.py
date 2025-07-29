from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__)
contracts_bp = Blueprint('contracts', __name__)
clauses_bp = Blueprint('clauses', __name__)
reports_bp = Blueprint('reports', __name__)
alerts_bp = Blueprint('alerts', __name__)
chat_bp = Blueprint('chat', __name__)
code_gen_bp = Blueprint('code_generation', __name__)

# Import routes
from app.api import auth, contracts, clauses, reports, alerts, chat, code_generation