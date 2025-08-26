from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  # TODO: change to IsAuthenticated later
from django.utils import timezone
from academics.models import ClassRoutine
from academics.serializers import ClassRoutineSerializer
from institution.models import Notice
from institution.serializers import NoticeSerializer


def _resolve_teacher_name(request):
    """
    For now:
    - If ?teacher=Name is provided, use it (lets you test w/o login).
    - Otherwise, if user is authenticated and role == Teacher,
      try to use request.user.get_full_name() or username.
    """
    q = request.query_params.get('teacher')
    if q:
        return q.strip()
    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False) and getattr(user, "role", "") == "Teacher":
        return user.get_full_name() or user.username
    return None

class TeacherDashboardSummary(APIView):
    permission_classes = [AllowAny]   # TODO: switch to IsAuthenticated

    def get(self, request):
        teacher_name = _resolve_teacher_name(request)
        today = timezone.localdate()
        weekday = today.strftime("%A")  # "Monday", "Tuesday", ...

        qs = ClassRoutine.objects.filter(day_of_week__iexact=weekday)
        if teacher_name:
            qs = qs.filter(teacher__iexact=teacher_name)

        classes = ClassRoutineSerializer(qs, many=True).data
        latest_notices_qs = Notice.objects.order_by('-date')[:5]
        latest_notices = NoticeSerializer(latest_notices_qs, many=True, context={'request': request}).data

        return Response({
            "teacher": teacher_name,
            "today": str(today),
            "weekday": weekday,
            "counts": {
                "total_classes_today": len(classes),
                "pending_results": 0,     # placeholder until result entry model/UI
                "notices": len(latest_notices),
            },
            "today_classes": classes,
            "latest_notices": latest_notices,
        })

class MyClasses(APIView):
    permission_classes = [AllowAny]   # TODO: switch later

    def get(self, request):
        teacher_name = _resolve_teacher_name(request)
        day = request.query_params.get("day")
        if not day:
            day = timezone.localdate().strftime("%A")
        qs = ClassRoutine.objects.filter(day_of_week__iexact=day)
        if teacher_name:
            qs = qs.filter(teacher__iexact=teacher_name)
        data = ClassRoutineSerializer(qs, many=True).data
        return Response({"day": day, "teacher": teacher_name, "classes": data})



class LatestNotices(APIView):
    permission_classes = [AllowAny]   # TODO: switch later

    def get(self, request):
        limit = int(request.query_params.get("limit", 10))
        qs = Notice.objects.order_by('-date')[:limit]
        data = NoticeSerializer(qs, many=True, context={'request': request}).data
        return Response({"count": len(data), "results": data})
