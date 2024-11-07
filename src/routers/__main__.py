from flask import Blueprint
from src.controllers import hello

router = Blueprint('router', __name__)


@router.route('/', methods=['GET'])
def root():
    return hello()
