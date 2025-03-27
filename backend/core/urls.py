from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from candidates.views import CandidateProfileViewSet, UserRegistrationView, UserLoginView, UserLogoutView
from jobs.views import JobPostingViewSet
from matching.views import JobMatchViewSet

router = DefaultRouter()
router.register(r'candidates', CandidateProfileViewSet)
router.register(r'jobs', JobPostingViewSet)
router.register(r'matches', JobMatchViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/register/', UserRegistrationView.as_view(), name='user_registration'),  # Added route
    path('api/login/', UserLoginView.as_view(), name='login'),
    path('api/logout/', UserLogoutView.as_view(), name='logout'),

]