"""Regression-only b_input context binding; shared helper contract is unchanged."""
from functools import wraps
from inspect import signature

from .controller import ACTIVE_SESSIONS
from .reads import LookupContext, GridSettingsContext


def bind_lookup_context(monkeypatch):
    from utils.base_pages.angular_base_page import AngularBasePage
    original = AngularBasePage.b_input
    parameters = signature(original)

    @wraps(original)
    def scoped_input(base, *args, **kwargs):
        controller = ACTIVE_SESSIONS.get(base.page)
        if controller is None or controller.recovering:
            return original(base, *args, **kwargs)
        arguments = parameters.bind(base, *args, **kwargs).arguments
        selecting = 'value' in arguments or arguments.get('search_text') or arguments.get('select_first') or arguments.get('clear')
        if not selecting:
            return original(base, *args, **kwargs)
        # Use the existing helper to resolve the input, not a second copy of its
        # label/model/root logic. The probe does not clear or select anything.
        target = {key: arguments[key] for key in ('label', 'ng_model', 'placeholder', 'index', 'root', 'timeout') if key in arguments}
        field = original(base, **target)
        select = field.locator('xpath=ancestor::smt-data-select[1]')
        if select.count() != 1:
            return original(base, *args, **kwargs)
        previous = controller.lookup
        controller.lookup = LookupContext(field, select.get_attribute('smtkeyfield'))
        try:
            return original(base, *args, **kwargs)
        finally:
            controller.lookup = previous

    monkeypatch.setattr(AngularBasePage, 'b_input', scoped_input)


def bind_grid_settings_context(monkeypatch):
    """Track existing helper stages; the shared helper implementation is untouched."""
    from utils.base_pages.angular_base_page import AngularBasePage
    original_setting = AngularBasePage.grid_setting
    original_controller = AngularBasePage.grid_controller

    @wraps(original_setting)
    def scoped_setting(base, *, menu_name, field_name, search_name=None, **kwargs):
        controller = ACTIVE_SESSIONS.get(base.page)
        if controller is None or controller.recovering:
            return original_setting(base, menu_name=menu_name, field_name=field_name,
                                    search_name=search_name, **kwargs)
        previous = controller.grid_settings
        controller.grid_settings = GridSettingsContext(menu_name, field_name, search_name)
        try:
            return original_setting(base, menu_name=menu_name, field_name=field_name,
                                    search_name=search_name, **kwargs)
        finally:
            controller.grid_settings = previous

    @wraps(original_controller)
    def scoped_controller(base, *args, **kwargs):
        controller = ACTIVE_SESSIONS.get(base.page)
        result = original_controller(base, *args, **kwargs)
        if (controller is not None and not controller.recovering
                and controller.grid_settings is not None and kwargs.get('open_setting')):
            controller.grid_settings.menu_open_count += 1
        return result

    monkeypatch.setattr(AngularBasePage, 'grid_setting', scoped_setting)
    monkeypatch.setattr(AngularBasePage, 'grid_controller', scoped_controller)
