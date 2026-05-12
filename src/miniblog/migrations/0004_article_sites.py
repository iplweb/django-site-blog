from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sites", "0002_alter_domain_unique"),
        ("miniblog", "0003_alter_article_article_body"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="sites",
            field=models.ManyToManyField(
                blank=True,
                help_text=(
                    "Restrict this article to selected sites. "
                    "Leave empty to make it visible on all sites."
                ),
                related_name="articles",
                to="sites.site",
                verbose_name="Sites",
            ),
        ),
    ]
