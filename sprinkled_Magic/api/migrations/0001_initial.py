from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Application', '0006_order_updated_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiToken',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('key',        models.CharField(max_length=40, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user',       models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='api_token',
                    to='Application.register_model',
                )),
            ],
        ),
    ]
