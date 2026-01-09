import flet as ft
from ui.styles import get_card_style
from core.i18n import i18n_manager, I18nText
from data.storage import load_user_data

class ChinaAIModeCard(ft.Container):
    def __init__(self):
        style = get_card_style()
        super().__init__(**style)
        

        user_data = load_user_data()
        current_mode = user_data.get("china_ai_mode", False)
        
        self.mode_switch = ft.Switch(
            value=current_mode,
            active_color=ft.Colors.GREEN_500,
        )
        
        self.content = ft.Row(
            controls=[
                ft.Row([
                    ft.Icon(ft.Icons.PUBLIC, color=ft.Colors.ORANGE_500),
                    I18nText(key="china_ai_mode_label", size=16, weight=ft.FontWeight.W_500),
                    ft.Text(
                        f"({i18n_manager.t('china_ai_mode_note')})",
                        size=12,
                        color=ft.Colors.GREY_500,
                    )
                ], spacing=8),
                self.mode_switch,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        i18n_manager.subscribe(self.update_ui)

    def will_unmount(self):
        i18n_manager.unsubscribe(self.update_ui)

    def update_ui(self):
        if not self.page:
            return

        if hasattr(self, 'content') and self.content.controls:
            row = self.content.controls[0]
            if isinstance(row, ft.Row) and len(row.controls) > 2:
                row.controls[2].value = f"({i18n_manager.t('china_ai_mode_note')})"
        self.update()

    def get_selected_mode(self):
        
        return self.mode_switch.value
