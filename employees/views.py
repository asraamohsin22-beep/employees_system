from django.shortcuts import render, redirect
from .models import Employee
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from weasyprint import HTML
import pandas as pd
from django.contrib.admin.views.decorators import staff_member_required
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)

def to_int(value):
    if value is None:
        return 0
    value = str(value).strip()
    if value == '' or value.lower() == 'nan':
        return 0
    return int(float(value))
@staff_member_required
def upload_excel(request):
    message = None
    if request.method == "POST" and request.FILES.get('file'):
        file = request.FILES['file']

        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_path = fs.path(filename)

        df = pd.read_excel(file_path)
           # ✅ حذف البيانات القديمة
        Employee.objects.all().delete()

        for _, row in df.iterrows():
          
                emp_id = str(row['التسلسل']).strip()
                Employee.objects.update_or_create(
                 emp_id=emp_id,
                 defaults={
                    'name': row['اسم الموظف'],
                    'job_title': row['عنوان وظيفي'],
                    'grade': row['د وظيفية'],
                    'stage': row['المرحلة'],
                    'base_salary': to_int(row['الراتب']),
                    'marital_status': row['الزوجية'],
                    'children': to_int(row['الاطفال']),
                    'position': str(row['المنصب']),
                    'certificate': str(row['الشهادة']),
                    'location': str(row['موقع جغرافي']),
                    'professional': to_int(row['مهنية']),
                    'engineering':to_int(row['الهندسية']),
                    'risk_type': str(row['الخطورة']),
                    'allowances': to_int(row['الاضافات']),
                    'bonuses': to_int(row['مكافئات']),
                    'overtime': to_int(row['ساعات اضافية']),
                    'total': to_int(row['المجموع']),
                    'retirement': to_int(row['التقاعد']),
                    'tax': to_int(row['الضريبة']),
                    'deductions': to_int(row['الاستقطاعات']),
                    'social_security': to_int(row['صندوق الضمان الاجتماعي']),
                    'final_total': to_int(row['المجموع.1']),
                    'net_salary': to_int(row['الصافي']),
                }
            )

        message = "تم رفع البيانات بنجاح ✅"

    return render(request, "upload.html", {"message": message})
def login_view(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('salary_lookup')
        else:
            error = "بيانات الدخول غير صحيحة"

    return render(request, "login.html", {"error": error})
@login_required
def salary_lookup(request):
    employee = None
    error = None

    if request.method == "POST":
        emp_id = request.POST.get("emp_id")

        if emp_id:
            emp_id = emp_id.strip()

            employee = Employee.objects.filter(
    emp_id=str(emp_id)
).first()

            if not employee:
                error = "لا يوجد موظف بهذا الرقم"
        else:
            error = "الرجاء إدخال الرقم الوظيفي"

    return render(request, "salary.html", {
        "employee": employee,
        "error": error
    })

# 👇 هنا تضيفها (تحتها مباشرة)
def logout_view(request):
    logout(request)
    return redirect('login')
def generate_pdf(request, emp_id):
    employee = Employee.objects.filter(emp_id=emp_id).first()

    html = render(request, 'salary_pdf.html', {
        'employee': employee
    }).content.decode('utf-8')

    pdf = HTML(string=html).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="salary.pdf"'

    return response