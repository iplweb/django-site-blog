def test_app_imports():
    import siteblog

    assert siteblog


def test_appconfig_loads():
    from django.apps import apps

    config = apps.get_app_config("siteblog")
    assert config.name == "siteblog"
