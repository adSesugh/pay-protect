# Generated by Django 5.1 on 2024-10-11 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_user_notify_on_milestone_user_notify_on_payment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dispute',
            name='status',
            field=models.CharField(choices=[('PENDING', 'PENDING'), ('TREATED', 'TREATED')], default='PENDING', max_length=50),
        ),
    ]
