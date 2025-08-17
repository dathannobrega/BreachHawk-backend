
from django.http import JsonResponse
from django.db import connections, DatabaseError
from pymongo import MongoClient
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health_check(request):
    status = {"status": "ok"}
    # Check PostgreSQL
    try:
        connections["default"].cursor().execute("SELECT 1;")
        status["postgresql"] = "ok"
    except DatabaseError as e:
        return JsonResponse({"status": "error", "message": str(e)})

    # Check MongoDB
    try:
        mongo_client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=2000)
        mongo_client.admin.command("ping")
        status["mongodb"] = "ok"
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse(status)
