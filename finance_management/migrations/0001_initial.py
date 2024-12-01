# Generated by Django 4.2.16 on 2024-11-27 14:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(max_length=20, unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(choices=[('INCOME', 'Income'), ('EXPENSE', 'Expense')], max_length=10)),
                ('category', models.CharField(choices=[('FINE', 'Library Fine'), ('MEMBERSHIP', 'Membership Fee'), ('SALARY', 'Staff Salary'), ('MAINTENANCE', 'Maintenance'), ('BOOKS', 'Book Purchase'), ('UTILITIES', 'Utilities'), ('OTHER', 'Other')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(choices=[('CASH', 'Cash'), ('CARD', 'Card'), ('ONLINE', 'Online'), ('BANK_TRANSFER', 'Bank Transfer')], max_length=15)),
                ('description', models.TextField()),
                ('reference_number', models.CharField(blank=True, max_length=50, null=True)),
                ('status', models.CharField(default='COMPLETED', max_length=20)),
                ('recorded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt_number', models.CharField(max_length=20, unique=True)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('payer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('transaction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='finance_management.transaction')),
            ],
        ),
        migrations.CreateModel(
            name='Fine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('reason', models.TextField()),
                ('date_issued', models.DateTimeField(auto_now_add=True)),
                ('due_date', models.DateTimeField()),
                ('paid', models.BooleanField(default=False)),
                ('payment_date', models.DateTimeField(blank=True, null=True)),
                ('transaction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='finance_management.transaction')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
