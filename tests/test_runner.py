import pytest
from tests.test_dashboard import test_dashboard
from tests.test_login import test_login


@pytest.mark.asyncio
async def test_authorization(page):
    await test_login(page)
    print('login page - success')
    await test_dashboard(page)
    print('dashboard page - success')

