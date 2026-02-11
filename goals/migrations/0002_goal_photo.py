# Generated migration for Goal photo fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goals', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='goals/'),
        ),
        migrations.AddField(
            model_name='goal',
            name='photo_b64',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='goal',
            name='photo_mime',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
