"""Opt-in view text assertion shared by both DOM implementations."""

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


def expect_text_or_readonly_value(page, content, value, *, timeout):
    """Retry rendered text and visible readonly input values without changing DOM."""
    if not isinstance(value, str):
        raise TypeError('text(include_input_values=True): expected value string bo‘lishi kerak')
    handle = content.element_handle(timeout=timeout)
    try:
        matched = page.wait_for_function(
            r"""({root, value}) => {
                if (!root || !root.isConnected) return false;
                const visible = element => {
                    const style = getComputedStyle(element);
                    return style.visibility !== 'hidden' && style.display !== 'none'
                        && element.getClientRects().length > 0;
                };
                const values = [root.innerText || '', ...Array.from(
                    root.querySelectorAll('input[readonly]:not([type="hidden"]), textarea[readonly]')
                ).filter(visible).map(element => element.value)];
                const normalize = text => text.replace(/\s+/g, ' ').trim();
                return values.some(actual => normalize(actual).includes(normalize(value)));
            }""",
            arg={'root': handle, 'value': value},
            timeout=timeout,
        )
        matched.dispose()
    except PlaywrightTimeoutError as exc:
        raise AssertionError(f'text(): matn yoki ko‘rinadigan readonly qiymat topilmadi: {value!r}') from exc
    finally:
        if handle is not None:
            handle.dispose()
