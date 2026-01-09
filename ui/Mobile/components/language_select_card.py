
import flet as ft
from ui.styles import AppColors, CARD_STYLE
from ui.Mobile.utils.selection_dialog import SelectionDialog, SelectionOption
from core.i18n import i18n_manager, I18nText

class LanguageSelectCard(ft.Container):
    
    
    def __init__(self):
        mobile_style = {**CARD_STYLE, "padding": 12}
        super().__init__(**mobile_style)
        
        self.selected_code = i18n_manager.current_lang
        options = self._build_language_options()
        
        self.language_selector = SelectionDialog(
            title_key="language_setting_label",
            options=options,
            on_select=self._on_language_select,
            selected_key=self.selected_code,
            selected_color=ft.Colors.BLUE,
            width=280,
            height=350,
            trigger_width=120,
        )

        self.content = ft.Row(
            controls=[
                ft.Row([
                    ft.Icon(ft.Icons.LANGUAGE, color=ft.Colors.BLUE_500, size=20),
                    I18nText(key="language_setting_label", size=14, weight=ft.FontWeight.W_500)
                ], spacing=8),
                self.language_selector,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        i18n_manager.subscribe(self.update_ui)

    def _build_language_options(self) -> list:
        sort_order = [
            'en_US', 'zh_CN', 'zh_TW', 'es_ES', 'fr_FR', 'ar_SA', 'ru_RU', 
            'pt_PT', 'de_DE', 'ja_JP', 'it_IT', 'ko_KR'
        ]
        
        def get_sort_index(code):
            try: return sort_order.index(code)
            except ValueError: return 999

        sorted_codes = sorted(
            i18n_manager.translations.keys(),
            key=lambda k: get_sort_index(k)
        )
        
        options = []
        for code in sorted_codes:
            data = i18n_manager.translations.get(code, {})
            name = data.get("language_name", code)
            if code == "zh_TW": name = "Traditional Chinese"
            
            options.append(SelectionOption(key=code, label=name))
        
        return options

    def _on_language_select(self, code: str):
        self.selected_code = code

    def did_mount(self):
        self.language_selector.did_mount()

    def will_unmount(self):
        i18n_manager.unsubscribe(self.update_ui)
        self.language_selector.will_unmount()
            
    def get_selected_language(self):
        return self.selected_code

    def update_ui(self):
        if not self.page: return
        pass
