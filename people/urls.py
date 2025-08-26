from rest_framework.routers import DefaultRouter
from .views import TeacherViewSet, StaffViewSet, StudentViewSet, PrincipalListViewSet, PresidentListViewSet

router = DefaultRouter()
router.register(r"teachers", TeacherViewSet, basename="teachers")
router.register(r"staff", StaffViewSet, basename="staff")
router.register(r"students", StudentViewSet, basename="students")
router.register(r"principal-list", PrincipalListViewSet, basename="principal-list")
router.register(r"president-list", PresidentListViewSet, basename="president-list")
urlpatterns = router.urls
