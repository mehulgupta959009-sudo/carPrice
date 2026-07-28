import json
from http import HTTPStatus
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from predictor import predict_price


def handler(request, context=None):
    try:
        body = request.get('body', '{}')
        if isinstance(body, (bytes, bytearray)):
            body = body.decode('utf-8')
        payload = json.loads(body) if body else {}
        price = predict_price(payload)
        return {
            'statusCode': HTTPStatus.OK,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'price': round(price, 2),
                'message': 'This estimate is generated from your selected vehicle profile.'
            })
        }
    except Exception as exc:
        return {
            'statusCode': HTTPStatus.BAD_REQUEST,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(exc)})
        }
