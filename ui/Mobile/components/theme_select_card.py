
import flet as ft
from ui.styles import get_card_style, theme_manager, CARD_STYLE
from ui.Mobile.utils.selection_dialog import SelectionDialog, SelectionOption
from core.i18n import i18n_manager, I18nText

THEME_OPTIONS = ["system", "light", "dark"]

class ThemeSelectCard(ft.Container):
    
    
    def __init__(self):
        mobile_style = {**CARD_STYLE, "padding": 12}
        super().__init__(**mobile_style)
        
        self.selected_theme = theme_manager.theme_mode
        
        options = [
            SelectionOption(key=theme, label_key=f"theme_{theme}")
            for theme in THEME_OPTIONS
        ]
        
        self.theme_selector = SelectionDialog(
            title_key="theme_setting_label",
            options=options,
            on_select=self._on_theme_select,
            selected_key=self.selected_theme,
            selected_color=ft.Colors.PURPLE,
            width=280,
            height=200,
            trigger_width=120,
        )

        self.content = ft.Row(
            controls=[
                ft.Row([
                    ft.Icon(ft.Icons.PALETTE, color=ft.Colors.PURPLE_500, size=20),
                    I18nText(key="theme_setting_label", size=14, weight=ft.FontWeight.W_500)
                ], spacing=8),
                self.theme_selector,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        i18n_manager.subscribe(self.update_ui)

    def _on_theme_select(self, theme_key: str):
        self.selected_theme = theme_key

    def did_mount(self):
        theme_manager.subscribe(self._on_theme_updated)
        self.theme_selector.did_mount()

    def will_unmount(self):
        i18n_manager.unsubscribe(self.update_ui)
        theme_manager.unsubscribe(self._on_theme_updated)
        self.theme_selector.will_unmount()

    def update_ui(self):
        if not self.page: return
        self.theme_selector.set_selected(self.selected_theme)
        self.update()

    def _on_theme_updated(self):
        if self.page:
            style = get_card_style()
            self.bgcolor = style["bgcolor"]
            self.shadow = style["shadow"]
            self.update()

    def get_selected_theme(self):
        return self.selected_theme
