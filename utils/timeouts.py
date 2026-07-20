"""Playwright va BasePage kutish vaqtlarining markaziy konfiguratsiyasi.

O'qish qoidasi:
- Barcha qiymatlar millisekundda: ``10_000`` = 10 sekund.
- ``PlaywrightTimeouts`` faqat Playwright'ning sof API defaultlari uchun.
- ``BasePageTimeouts`` loyiha yozgan ``BasePage`` helperlarining timeout va
  delay qiymatlari uchun.
- Timeout maksimal limit: shart tez bajarilsa to'liq vaqt kutilmaydi.
- Har bir qiymat ostidagi ``Ishlatadi`` ro'yxati qaysi funksiya/helperlarga
  ta'sir qilishini ko'rsatadi.
- Faqat bitta test/flowga tegishli vaqt bu global faylga qo'shilmaydi.
- HTTP client timeoutlari bu modulga kirmaydi: requests/urllib sekund ishlatadi.
"""


class PlaywrightTimeouts:
    """Playwright'ning sof API chaqiruvlari uchun global default timeoutlar."""

    # 10 s — Playwrightning umumiy action va assertion default timeouti.
    # Ishlatadi:
    # - conftest.py: expect.set_options() va barcha browser context set_default_timeout().
    # - Timeout berilmagan click(), fill(), press(), locator va expect() chaqiruvlari.
    # Ta'siri: oshirilsa deyarli barcha native Playwright action/assertionlar
    # sekinroq fail qiladi; eng keng ta'sirli Playwright sozlamasi.
    ACTION = 10_000

    # 20 s — browserning to'liq document navigation default timeouti.
    # Ishlatadi:
    # - conftest.py: barcha browser context set_default_navigation_timeout().
    # Ta'siri: timeout alohida berilmagan page.goto(), page.reload(),
    # page.go_back(), page.go_forward(), page.set_content() va
    # page.expect_navigation() operatsiyalariga.
    # Muhim: BasePage.navigate_to() bunga kirmaydi. U page.goto() emas,
    # Smartup menyusini bosib ilova ichidagi UI almashishini kutadigan helper.
    NAVIGATION = 20_000


class BasePageTimeouts:
    """Loyiha yozgan ``BasePage`` funksiyalari uchun maksimal kutish limitlari."""

    # 0.5 s — field locatorning ichki visibility probe'i.
    # Ishlatadi:
    # - BasePage._field_locator_by_label(): labelga tegishli input visible ekanini tekshiradi.
    # - BasePage.save_and_expect_heading(): transition yiqilganda error matnini qayta tekshiradi.
    # Ta'siri: oddiy click/fillga emas, faqat BasePage field/error discovery tezligiga.
    FIELD_PROBE = 500

    # 1 s — qisqa UI holati va ichki locator tekshiruvlari.
    # Ishlatadi:
    # - BasePage._visible_error_text(), BasePage._toggle_checkbox().reached().
    # - BasePage._field_container_by_label(), _field_locator_by_grid_header(),
    #   _field_locator_by_label().
    # Ta'siri: error/label/checkbox topilmasa har bir qisqa probe qancha kutishini belgilaydi.
    SHORT_CHECK = 1_000

    # 2 s — global loader appearance tekshiruvi.
    # Ishlatadi:
    # - BasePage.wait_for_loader(): loader umuman paydo bo'ladimi, shuni kutadi.
    # Ta'siri: loader chiqmasa ham har bir wait_for_loader()da shu vaqt real xarajat bo'lishi mumkin.
    LOADER_APPEAR = 2_000

    # 10 s — BasePage.text() helperining content visibility limiti.
    # Ishlatadi:
    # - BasePage.text(): root/content ko'rinishini kutadi.
    # Ta'siri: faqat timeout parametri berilmagan BasePage.text() chaqiruvlariga.
    TEXT = 10_000

    # 30 s — dropdown, picker va popup kabi interaktiv komponentlar.
    # Ishlatadi:
    # - BasePage.b_input(), BasePage.multiselect(), BasePage.date_picker().
    # Ta'siri: BasePage boshqaradigan option yoki calendar sekin ochilgandagi maksimal vaqt.
    COMPONENT = 10_000

    # 120 s — Smartup ichidagi katta UI transition timeouti.
    # Bu browserning yangi document ochishini emas, click/save dan keyin Smartup
    # interfeysi boshqa holatga o'tishini kutadi.
    # Ishlatadi:
    # - BasePage.navigate_to(): menyuni bosadi va loader tugashini kutadi;
    # - BasePage.save_and_expect_heading(): save natijasi/headingni kutadi;
    # - BasePage.expect_page(): URL, heading yoki sahifa belgisini kutadi;
    # - BasePage.switch_filial(): filial almashishi tugashini kutadi.
    # Muhim: page.goto()/reload kabi browser navigationlarga ta'sir qilmaydi.
    UI_TRANSITION = 30_000

    # 300 s — umumiy Smartup blocking loader yo'qolishining default limiti.
    # Ishlatadi:
    # - BasePage.wait_for_loader() timeout parametri berilmagan barcha chaqiruvlarda.
    # - Shu helperni ichkarida ishlatadigan grid_controller() va grid(checkbox="all")da.
    # Ta'siri: loader paydo bo'lib qolib ketsa test eng ko'pi bilan 5 minut kutadi.
    LOADER = 30_000

    # 50 ms — server-search inputiga har bir belgini yozish orasidagi real pauza.
    # Ishlatadi: BasePage.b_input(server_search=True).
    # Muhim: bu maksimal timeout emas; qiymat har bir belgi uchun real kutiladi.
    # Ta'siri: matn uzunligi × 50 ms miqdorida test vaqtiga bevosita qo'shiladi.
    TYPE_DELAY = 50
