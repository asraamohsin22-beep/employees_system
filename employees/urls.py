from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),  # 👈 هذا الحل
    path('login/', views.login_view, name='login'),
    path('salary/', views.salary_lookup, name='salary_lookup'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_excel, name='upload_excel'),
    path('pdf/<str:emp_id>/', views.generate_pdf, name='generate_pdf'),
    
]
