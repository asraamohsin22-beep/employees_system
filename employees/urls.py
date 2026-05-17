from django.contrib import admin   # ✅ هذا مهم جدًا
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.salary_lookup, name='salary_lookup'),
    path('salary/', views.salary_lookup, name='salary_lookup'),
    path('', views.salary_lookup, name='salary_lookup'),
    path('pdf/<str:emp_id>/', views.generate_pdf, name='generate_pdf'),
]