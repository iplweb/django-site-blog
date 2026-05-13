import django.contrib.sites.managers
import django.db.models.manager
import django.utils.timezone
import model_utils.fields
from django.db import migrations, models


# `model_utils.fields.SplitField` (>=5) injects an `_<name>_excerpt`
# TextField via ``contribute_to_class`` at runtime. The database side of the
# migration picks that up automatically when the SchemaEditor reifies the
# model, so ``CREATE TABLE`` already contains both columns. The migration
# **state** however is built from the explicit field list and would not
# otherwise know about the excerpt column — which leads ``makemigrations``
# to keep generating spurious ``AddField`` operations and breaks the model
# graph for downstream apps. ``SeparateDatabaseAndState`` is the standard
# fix: ship the same ``CreateModel`` to both sides, but only the *state*
# variant declares ``_article_body_excerpt`` explicitly. The database
# variant omits it so the SchemaEditor doesn't try to create the column
# twice.
COMMON_FIELDS = [
    (
        "id",
        models.BigAutoField(
            auto_created=True,
            primary_key=True,
            serialize=False,
            verbose_name="ID",
        ),
    ),
    (
        "created",
        model_utils.fields.AutoCreatedField(
            default=django.utils.timezone.now,
            editable=False,
            verbose_name="created",
        ),
    ),
    (
        "modified",
        model_utils.fields.AutoLastModifiedField(
            default=django.utils.timezone.now,
            editable=False,
            verbose_name="modified",
        ),
    ),
    (
        "status",
        model_utils.fields.StatusField(
            choices=[("draft", "draft"), ("published", "published")],
            default="draft",
            max_length=100,
            no_check_for_status=True,
            verbose_name="status",
        ),
    ),
    (
        "status_changed",
        model_utils.fields.MonitorField(
            default=django.utils.timezone.now,
            monitor="status",
            verbose_name="status changed",
        ),
    ),
    ("title", models.TextField(verbose_name="Title")),
    (
        "article_body",
        model_utils.fields.SplitField(
            help_text=(
                'Use the split marker "&lt;!-- split --&gt;" in '
                "case you want to displaythe shorter version of "
                "the article body"
            ),
            verbose_name="Article body",
        ),
    ),
]

TAIL_FIELDS = [
    (
        "published_on",
        models.DateTimeField(
            default=django.utils.timezone.now,
            verbose_name="Published on",
        ),
    ),
    ("slug", models.SlugField(unique=True)),
    (
        "sites",
        models.ManyToManyField(
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

OPTIONS = {
    "verbose_name": "Article",
    "verbose_name_plural": "Articles",
    "ordering": ("-published_on", "title"),
}

MANAGERS = [
    ("objects", django.db.models.manager.Manager()),
    (
        "on_site",
        django.contrib.sites.managers.CurrentSiteManager("sites"),
    ),
]


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.CreateModel(
                    name="Article",
                    fields=COMMON_FIELDS + TAIL_FIELDS,
                    options=OPTIONS,
                    managers=MANAGERS,
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name="Article",
                    fields=(
                        COMMON_FIELDS
                        + [
                            (
                                "_article_body_excerpt",
                                models.TextField(editable=False),
                            ),
                        ]
                        + TAIL_FIELDS
                    ),
                    options=OPTIONS,
                    managers=MANAGERS,
                ),
            ],
        ),
    ]
