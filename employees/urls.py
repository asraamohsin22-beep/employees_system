from django.contrib import admin   # ✅ هذا مهم جدًا
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.salary_lookup, name='salary_lookup'),
    path('salary/', views.salary_lookup, name='salary_lookup'),
<<<<<<< HEAD
    path('', views.salary_lookup, name='salary_lookup'),
    path('pdf/<str:emp_id>/', views.generate_pdf, name='generate_pdf'),
=======
    path('logout/', views.logout_view, name='logout'),
   # path('pdf/<str:emp_id>/', views.generate_pdf, name='generate_pdf'),
    path('upload/', views.upload_excel, name='upload_excel'),
    
>>>>>>> ffbaacae5c1dec8bedf54c7f613a6ee3d654aea0
]