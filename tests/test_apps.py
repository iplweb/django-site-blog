def test_app_imports():
    import miniblog

    assert miniblog


def test_appconfig_loads():
    from django.apps import apps

    config = apps.get_app_config("miniblog")
    assert config.name == "miniblog"
