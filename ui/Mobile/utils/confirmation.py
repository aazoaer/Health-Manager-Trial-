import flet as ft
from core.i18n import i18n_manager

def create_confirmation_dialog(title: str, on_confirm, on_cancel) -> ft.AlertDialog:
    
    return ft.AlertDialog(
        modal=True,
        title=ft.Text(title, text_align=ft.TextAlign.CENTER, size=18, weight=ft.FontWeight.W_500),
        shape=ft.RoundedRectangleBorder(radius=15),
        actions=[

            ft.Container(
                content=ft.Row(
                    [ft.Icon(ft.Icons.CHECK, color=ft.Colors.WHITE), ft.Text(i18n_manager.t("confirm_button"), color=ft.Colors.WHITE)],
                    tight=True
                ),
                bgcolor=ft.Colors.GREEN_500,
                padding=ft.padding.symmetric(vertical=10, horizontal=20),
                border_radius=10,
                on_click=on_confirm,
                tooltip=i18n_manager.t("confirm_button")
            ),

            ft.Container(
                content=ft.Row(
                    [ft.Icon(ft.Icons.CLOSE, color=ft.Colors.WHITE), ft.Text(i18n_manager.t("cancel_button"), color=ft.Colors.WHITE)],
                    tight=True
                ),
                bgcolor=ft.Colors.RED_500,
                padding=ft.padding.symmetric(vertical=10, horizontal=20),
                border_radius=10,
                on_click=on_cancel,
                tooltip=i18n_manager.t("cancel_button")
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        content_padding=25,
    )
