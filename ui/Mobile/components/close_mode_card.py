
import flet as ft
from ui.styles import CARD_STYLE
from ui.Mobile.utils.selection_dialog import SelectionDialog, SelectionOption
from core.i18n import i18n_manager, I18nText
from data.storage import load_user_data

CLOSE_MODE_OPTIONS = ["ask", "minimize", "quit"]

class CloseModeCard(ft.Container):
    
    
    def __init__(self):
        mobile_style = {**CARD_STYLE, "padding": 12}
        super().__init__(**mobile_style)
        
        user_data = load_user_data()
        self.selected_mode = user_data.get("close_mode", "ask")
        
        options = [
            SelectionOption(key=mode, label_key=f"close_{mode}")
            for mode in CLOSE_MODE_OPTIONS
        ]
        
        self.mode_selector = SelectionDialog(
            title_key="close_setting_label",
            options=options,
            on_select=self._on_mode_select,
            selected_key=self.selected_mode,
            selected_color=ft.Colors.RED,
            width=280,
            height=200,
            trigger_width=120,
        )

        self.content = ft.Row(
            controls=[
                ft.Row([
                    ft.Icon(ft.Icons.CLOSE, color=ft.Colors.RED_500, size=20),
                    I18nText(key="close_setting_label", size=14, weight=ft.FontWeight.W_500)
                ], spacing=8),
                self.mode_selector,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        i18n_manager.subscribe(self.update_ui)

    def _on_mode_select(self, mode_key: str):
        self.selected_mode = mode_key

    def did_mount(self):
        self.mode_selector.did_mount()

    def will_unmount(self):
        i18n_manager.unsubscribe(self.update_ui)
        self.mode_selector.will_unmount()

    def update_ui(self):
        if not self.page: return
        self.mode_selector.set_selected(self.selected_mode)
        self.update()

    def get_selected_mode(self):
        return self.selected_mode
