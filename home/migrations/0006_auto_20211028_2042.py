# Generated by Django 3.2.7 on 2021-10-28 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_deposit_oldid'),
    ]

    operations = [
        migrations.CreateModel(
            name='CashBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remark', models.CharField(blank=True, max_length=300, null=True)),
                ('transactionType', models.CharField(blank=True, max_length=300, null=True)),
                ('amount', models.FloatField(default=0.0)),
                ('balanceThatTime', models.FloatField(default=0.0)),
                ('availableBalance', models.FloatField(default=0.0)),
                ('isDeleted', models.BooleanField(default=False)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('lastUpdatedOn', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'D) CashBook List',
            },
        ),
        migrations.AlterModelOptions(
            name='deposititem',
            options={'verbose_name_plural': 'C) Deposit Item List'},
        ),
    ]
