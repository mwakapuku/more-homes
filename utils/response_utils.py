from rest_framework.response import Response


def create_response(msg, response_status, total_item=0, data=None):
    body = {
        "total_item": total_item,
        "detail": msg,
        "data": data,
        "status_code": response_status
    }
    return Response(body, status=response_status)


def create_auth_response(msg, access_token, refresh_token, user, response_status):
    body = {
        "detail": msg,
        "access": str(access_token),
        "refresh": str(refresh_token),
        "status_code": response_status,
        "data": user
    }
    return Response(body, status=response_status)