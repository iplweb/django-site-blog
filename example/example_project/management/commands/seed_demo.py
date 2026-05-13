from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from siteblog.models import Article

SITES = [
    {"domain": "example.com", "name": "Example.com"},
    {"domain": "mac-mini", "name": "Mac Mini intranet"},
    # Loopback hosts so `runserver` + a browser at http://localhost:8000/
    # works out of the box (no /etc/hosts edits needed). Django's
    # _get_site_by_host strips the port and re-matches, so "localhost"
    # also covers "localhost:8000". These hosts get no site-restricted
    # articles, so they only see the OR-default ("visible everywhere")
    # posts.
    {"domain": "localhost", "name": "Localhost (loopback)"},
    {"domain": "127.0.0.1", "name": "127.0.0.1 (loopback)"},
]

# Each entry: (slug, title, body, status, list-of-site-domains-or-empty).
# An empty list of sites means "visible on every site" (the package's
# OR-default semantics).
#
# Bodies use the `<!-- split -->` marker so the list view shows just the
# excerpt (everything before the marker) with a "Read more" link, while
# the detail view shows the full content. They also exercise the
# `|safe` rendering path with rich HTML (bold, italic, lists, code,
# blockquotes, links, headings).
# NOTE on the split marker: `model_utils` only recognises `<!-- split -->`
# when it appears on a line **by itself**. The marker is therefore wrapped
# in literal "\n" newlines below so the saved body splits cleanly into
# excerpt + remainder.
WELCOME_BODY = """\
<p>Welcome! <strong>django-site-blog</strong> is a tiny, reusable Django app for blog or news articles with first-class <em>multi-site</em> support.</p>
<p>This article has no site restriction, so it shows up <strong>everywhere</strong> &mdash; on example.com, on mac-mini, and on every other host you wire up.</p>

<!-- split -->

<h2>How site scoping works</h2>
<p>Articles with an <em>empty</em> <code>sites</code> M2M are visible on every site. Articles with at least one site selected are restricted to those sites only. This is sometimes called <strong>inverted-default</strong> semantics.</p>
<blockquote>An empty selection means &ldquo;all sites&rdquo;, not &ldquo;no sites&rdquo;.</blockquote>
<p>The whole filter is one OR query:</p>
<p><code>Article.objects.filter(Q(sites__isnull=True) | Q(sites__id=current_site.id))</code></p>
"""

RELEASE_NOTES_BODY = """\
<p>Cross-site announcement &mdash; both <strong>example.com</strong> and <strong>mac-mini</strong> see this one.</p>

<!-- split -->

<h2>What changed</h2>
<ul>
  <li>Added per-host filtering via <code>CurrentSiteMiddleware</code>.</li>
  <li>Made <em>excerpt + read more</em> the default on the list view.</li>
  <li>Wired a richer demo so you can see <strong>bold</strong>, <em>italic</em>, <a href="https://docs.djangoproject.com/">links</a>, lists and <code>inline code</code> in action.</li>
</ul>
"""

EXAMPLE_COM_ONLY_BODY = """\
<p>This post is restricted to <strong>example.com</strong>. Visit via the <code>mac-mini</code> hostname and it disappears from both the list and the detail view.</p>

<!-- split -->

<h2>Q3 roadmap</h2>
<ol>
  <li><strong>Tags</strong> &mdash; light-weight categorisation.</li>
  <li><strong>RSS feed</strong> &mdash; per-site, naturally.</li>
  <li><strong>OG metadata</strong> &mdash; nicer link previews.</li>
</ol>
<p>Want to follow along? <a href="https://example.com/feed/">Subscribe to the public feed</a>.</p>
"""

EXAMPLE_COM_CHANGELOG_BODY = """\
<p>Another <strong>example.com-only</strong> post, to show that filtering applies to the list view as well as the detail view.</p>

<!-- split -->

<h2>2026-05</h2>
<ul>
  <li>Rewrote the demo project with a proper home page.</li>
  <li>Added the <em>splitter</em> marker to demo articles.</li>
  <li>Made the admin link reachable from the homepage.</li>
</ul>
"""

MAC_MINI_ONLY_BODY = """\
<p>Intranet-only post. Visible on <strong>mac-mini</strong>, hidden on <strong>example.com</strong>.</p>

<!-- split -->

<h2>Heads-up</h2>
<p>The backup job runs nightly at <code>03:00</code>. If you see <em>stale</em> data in the morning, check the <code>cron</code> log first.</p>
<blockquote>Reminder: this content never reaches the public site &mdash; <code>sites=[mac-mini]</code> keeps it inside the intranet.</blockquote>
"""

DRAFT_POST_BODY = """\
<p>Drafts <strong>404</strong> on the public detail URL regardless of site.</p>

<!-- split -->

<p>Their <code>get_absolute_url()</code> returns the admin change URL instead, so editor preview links keep working.</p>
"""

ARTICLES = [
    ("welcome", "Welcome to django-site-blog", WELCOME_BODY, "published", []),
    (
        "release-notes",
        "Release notes (visible everywhere)",
        RELEASE_NOTES_BODY,
        "published",
        [],
    ),
    (
        "example-com-only",
        "Public roadmap (example.com only)",
        EXAMPLE_COM_ONLY_BODY,
        "published",
        ["example.com"],
    ),
    (
        "example-com-changelog",
        "Public changelog (example.com only)",
        EXAMPLE_COM_CHANGELOG_BODY,
        "published",
        ["example.com"],
    ),
    (
        "mac-mini-only",
        "Internal memo (mac-mini only)",
        MAC_MINI_ONLY_BODY,
        "published",
        ["mac-mini"],
    ),
    ("draft-post", "Draft (never public)", DRAFT_POST_BODY, "draft", []),
]


class Command(BaseCommand):
    help = "Seed demo Sites and Articles. Safe to re-run."

    def handle(self, *args, **options):
        # The sites app's post_migrate signal pre-creates a Site with id=1
        # and domain="example.com" on a fresh DB. Reuse it where possible so
        # we don't end up with two example.com rows.
        sites_by_domain = {}
        for entry in SITES:
            site, created = Site.objects.update_or_create(
                domain=entry["domain"],
                defaults={"name": entry["name"]},
            )
            sites_by_domain[entry["domain"]] = site
            self.stdout.write(
                f"  Site {'created' if created else 'updated'}: "
                f"{site.domain} ({site.name})"
            )

        for slug, title, body, status, site_domains in ARTICLES:
            # NOTE: we deliberately avoid `Article.objects.update_or_create`
            # because Django ships it with `save(update_fields=...)` set to
            # the explicit defaults only. `SplitField.pre_save` mutates a
            # *different* field (`_article_body_excerpt`) on the instance,
            # which Django then drops from the UPDATE statement, leaving the
            # excerpt column stale. Plain `save()` writes every field.
            article, created = Article.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "article_body": body,
                    "status": status,
                },
            )
            if not created:
                article.title = title
                article.article_body = body
                article.status = status
                article.save()
            article.sites.set([sites_by_domain[d] for d in site_domains])
            scope = ", ".join(site_domains) if site_domains else "all sites"
            self.stdout.write(
                f"  Article {'created' if created else 'updated'}: "
                f"{slug} [{status}, {scope}]"
            )

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
