import pandas as pd
from django.core.management.base import BaseCommand, CommandError

from employees.views import import_employees_from_dataframe


class Command(BaseCommand):
    help = "Import employees from an Excel file. This is for server/admin use only."

    def add_arguments(self, parser):
        parser.add_argument("excel_file", help="Path to the Excel file to import")

    def handle(self, *args, **options):
        excel_file = options["excel_file"]

        try:
            df = pd.read_excel(excel_file)
        except Exception as exc:
            raise CommandError(f"Could not read Excel file: {exc}") from exc

        try:
            imported = import_employees_from_dataframe(df)
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS(f"Imported {imported} employees."))
