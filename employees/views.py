from django.shortcuts import render
from .models import Employee
from django.conf import settings
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from io import BytesIO
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import pandas as pd
def to_int(value):
    if value is None:
        return 0
    value = str(value).strip()
    if value == '' or value.lower() == 'nan':
        return 0
    return int(float(value))


def import_employees_from_dataframe(df):
    field_map = {
        "emp_id": 0,
        "name": 1,
        "job_title": 2,
        "grade": 3,
        "stage": 4,
        "base_salary": 5,
        "marital_status": 6,
        "children": 7,
        "position": 8,
        "certificate": 9,
        "location": 10,
        "professional": 11,
        "engineering": 12,
        "risk_type": 13,
        "allowances": 14,
        "bonuses": 15,
        "overtime": 16,
        "total": 17,
        "retirement": 18,
        "tax": 19,
        "deductions": 20,
        "social_security": 21,
        "final_total": 22,
        "net_salary": 23,
    }

    if df.shape[1] < len(field_map):
        raise ValueError("ملف Excel لا يحتوي على جميع الأعمدة المطلوبة")

    Employee.objects.all().delete()

    imported = 0
    for _, row in df.iterrows():
        emp_id = str(row.iloc[field_map["emp_id"]]).strip()
        if not emp_id or emp_id.lower() == "nan":
            continue

        Employee.objects.update_or_create(
            emp_id=emp_id,
            defaults={
                "name": row.iloc[field_map["name"]],
                "job_title": row.iloc[field_map["job_title"]],
                "grade": row.iloc[field_map["grade"]],
                "stage": row.iloc[field_map["stage"]],
                "base_salary": to_int(row.iloc[field_map["base_salary"]]),
                "marital_status": row.iloc[field_map["marital_status"]],
                "children": to_int(row.iloc[field_map["children"]]),
                "position": str(row.iloc[field_map["position"]]),
                "certificate": str(row.iloc[field_map["certificate"]]),
                "location": str(row.iloc[field_map["location"]]),
                "professional": to_int(row.iloc[field_map["professional"]]),
                "engineering": to_int(row.iloc[field_map["engineering"]]),
                "risk_type": str(row.iloc[field_map["risk_type"]]),
                "allowances": to_int(row.iloc[field_map["allowances"]]),
                "bonuses": to_int(row.iloc[field_map["bonuses"]]),
                "overtime": to_int(row.iloc[field_map["overtime"]]),
                "total": to_int(row.iloc[field_map["total"]]),
                "retirement": to_int(row.iloc[field_map["retirement"]]),
                "tax": to_int(row.iloc[field_map["tax"]]),
                "deductions": to_int(row.iloc[field_map["deductions"]]),
                "social_security": to_int(row.iloc[field_map["social_security"]]),
                "final_total": to_int(row.iloc[field_map["final_total"]]),
                "net_salary": to_int(row.iloc[field_map["net_salary"]]),
            },
        )
        imported += 1

    return imported


@staff_member_required(login_url="/secret-admin-123/login/")
def upload_excel(request):
    message = None
    error = None

    if request.method == "POST":
        excel_file = request.FILES.get("file")
        if not excel_file:
            error = "الرجاء اختيار ملف Excel"
        elif not excel_file.name.lower().endswith((".xlsx", ".xls")):
            error = "الملف يجب أن يكون بصيغة Excel"
        else:
            try:
                df = pd.read_excel(excel_file)
                imported = import_employees_from_dataframe(df)
                message = f"تم رفع بيانات {imported} موظف بنجاح"
            except Exception as exc:
                error = f"تعذر رفع الملف: {exc}"

    return render(request, "upload.html", {"message": message, "error": error})
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
@login_required
def generate_pdf(request, emp_id):
    employee = Employee.objects.filter(emp_id=emp_id).first()
    if not employee:
        return HttpResponse("Employee not found", status=404)

    font_name = "ArabicFont"
    bundled_font = settings.BASE_DIR / "employees" / "static" / "fonts" / "NotoNaskhArabic-Regular.ttf"
    for font_path in (bundled_font, r"C:\Windows\Fonts\tahoma.ttf", r"C:\Windows\Fonts\arial.ttf"):
        if Path(font_path).exists():
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            break
    else:
        font_name = "Helvetica"

    def ar(value):
        text = "" if value is None else str(value)
        return get_display(arabic_reshaper.reshape(text))

    title_style = ParagraphStyle(
        "ArabicTitle",
        fontName=font_name,
        fontSize=16,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0d6efd"),
    )
    cell_style = ParagraphStyle(
        "ArabicCell",
        fontName=font_name,
        fontSize=11,
        leading=15,
        alignment=TA_RIGHT,
    )
    label_style = ParagraphStyle(
        "ArabicLabel",
        parent=cell_style,
        textColor=colors.white,
    )

    rows = [
        ("اسم الموظف", employee.name),
        ("عنوان وظيفي", employee.job_title),
        ("د وظيفية", employee.grade),
        ("المرحلة", employee.stage),
        ("الراتب", employee.base_salary),
        ("الزوجية", employee.marital_status),
        ("الأطفال", employee.children),
        ("المنصب", employee.position),
        ("الشهادة", employee.certificate),
        ("موقع جغرافي", employee.location),
        ("مهنية", employee.professional),
        ("الهندسية", employee.engineering),
        ("الخطورة", employee.risk_type),
        ("الاضافات", employee.allowances),
        ("مكافئات", employee.bonuses),
        ("ساعات إضافية", employee.overtime),
        ("المجموع", employee.total),
        ("التقاعد", employee.retirement),
        ("الضريبة", employee.tax),
        ("الاستقطاعات", employee.deductions),
        ("صندوق الضمان الاجتماعي", employee.social_security),
        ("المجموع.1", employee.final_total),
        ("الصافي", employee.net_salary),
    ]

    data = []
    for label, value in rows:
        data.append([
            Paragraph(ar(value), cell_style),
            Paragraph(ar(label), label_style),
        ])

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    table = Table(data, colWidths=[11 * cm, 6 * cm], repeatRows=0)
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#0d6efd")),
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, -1), (0, -1), colors.HexColor("#eaf7ef")),
    ]))

    story = [
        Paragraph(ar("شريط الراتب الإلكتروني"), title_style),
        Spacer(1, 0.4 * cm),
        table,
        Spacer(1, 0.4 * cm),
        Paragraph(ar("By : Msc asraa mohsin"), cell_style),
    ]
    doc.build(story)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="salary_{employee.emp_id}.pdf"'
    return response
