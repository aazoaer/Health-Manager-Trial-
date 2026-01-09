import flet as ft
from ui.styles import AppColors
from ui.Desktop.utils.time_utils import get_current_date_str, get_current_time_str, get_timezone_str
from core.i18n import i18n_manager

class DateHeader(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = ft.padding.only(bottom=10)
        self.content = self._build_content()

    def _build_content(self):
        date_str = get_current_date_str()
        time_str = get_current_time_str()[:-3]
        timezone_str = get_timezone_str()
        
        return ft.Column([
            ft.Text(date_str, size=24, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
            ft.Text(f"{timezone_str} {i18n_manager.t('header_current_time')} {time_str}", size=14, color=AppColors.TEXT_SECONDARY),
        ])
