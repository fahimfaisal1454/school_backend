from django.urls import path
from .views import TeacherDashboardSummary, MyClasses, LatestNotices

urlpatterns = [
    path('teacher/dashboard/summary/', TeacherDashboardSummary.as_view()),
    path('teacher/my-classes/', MyClasses.as_view()),
    path('teacher/notices/', LatestNotices.as_view()),
]
