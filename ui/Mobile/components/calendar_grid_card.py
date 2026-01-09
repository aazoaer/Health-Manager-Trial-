
import flet as ft
import datetime
import calendar
import asyncio
from ui.styles import AppColors, CARD_STYLE
from data.storage import load_month_summaries
from core.i18n import i18n_manager, I18nText
from core import event_bus

class CalendarGridCard(ft.Container):
    
    
    def __init__(self, on_month_change=None):
        mobile_style = {**CARD_STYLE, "padding": 12}
        super().__init__(**mobile_style)
        self.expand = True
        self.on_month_change = on_month_change
        self.current_year = datetime.date.today().year
        self.current_month = datetime.date.today().month
        self.today = datetime.date.today()
        self.month_data = {}
        
        self._init_components()
        self.content = self._build_content()
        self._load_month_data()
        self._update_calendar()
        
        event_bus.subscribe(event_bus.USER_DATA_SAVED, self._on_data_changed)
        event_bus.subscribe(event_bus.WATER_ADDED, self._on_data_changed)

    def did_mount(self):
        from data.storage import update_today_summary
        try:
            update_today_summary()
        except Exception:
            pass
        asyncio.create_task(self.refresh_data())

    def will_unmount(self):
        if self.page and self.details_dialog in self.page.overlay:
            try:
                self.page.overlay.remove(self.details_dialog)
            except Exception:
                pass
        event_bus.unsubscribe(event_bus.USER_DATA_SAVED, self._on_data_changed)
        event_bus.unsubscribe(event_bus.WATER_ADDED, self._on_data_changed)

    def _on_data_changed(self, *args, **kwargs):
        if not self.page: return
        asyncio.create_task(self.refresh_data())

    def _init_components(self):
        self.month_label = ft.Text(
            "", size=16, weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        self.calendar_grid = ft.Column(spacing=2)
        
        self.details_content = ft.Column(spacing=8)
        self.details_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(i18n_manager.t("calendar_details_title"), size=16),
            content=ft.Container(
                content=self.details_content,
                width=300, height=200
            ),
            actions=[ft.TextButton("OK", on_click=self._close_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
            content_padding=15
        )

    def _build_content(self):
        weekday_keys = ["weekday_mon", "weekday_tue", "weekday_wed", 
                        "weekday_thu", "weekday_fri", "weekday_sat", "weekday_sun"]
        
        weekday_row = ft.Row(
            controls=[
                ft.Container(
                    content=I18nText(key=k, size=10, weight=ft.FontWeight.BOLD, 
                                    color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                    expand=1, alignment=ft.Alignment(0, 0)
                ) for k in weekday_keys
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=2
        )
        
        return ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CALENDAR_MONTH, color=ft.Colors.PURPLE_500, size=20),
                I18nText(key="calendar_title", size=16, weight=ft.FontWeight.W_600)
            ], spacing=6),
            
            ft.Divider(height=10, color="transparent"),
            
            ft.Row([
                ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, icon_color=ft.Colors.PURPLE_500, on_click=self._prev_month, icon_size=20),
                ft.Container(content=self.month_label, expand=True, alignment=ft.Alignment(0, 0)),
                ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, icon_color=ft.Colors.PURPLE_500, on_click=self._next_month, icon_size=20),
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Divider(height=8, color="transparent"),
            weekday_row,
            ft.Divider(height=4, color="transparent"),
            self.calendar_grid
        ], spacing=4)

    def _load_month_data(self):
        self.month_data = load_month_summaries(self.current_year, self.current_month)

    def _prev_month(self, e):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._load_month_data()
        self._update_calendar()
        if self.on_month_change:
            self.on_month_change(self.current_year, self.current_month)

    def _next_month(self, e):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._load_month_data()
        self._update_calendar()
        if self.on_month_change:
            self.on_month_change(self.current_year, self.current_month)

    async def refresh_data(self):
        self._load_month_data()
        self._update_calendar()
        self.update()

    def _update_calendar(self):
        self.month_label.value = f"{self.current_year}-{self.current_month:02d}"
        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdayscalendar(self.current_year, self.current_month)
        
        self.calendar_grid.controls.clear()
        for week in month_days:
            week_row = ft.Row(spacing=2, alignment=ft.MainAxisAlignment.CENTER)
            for day in week:
                if day == 0:
                    cell = ft.Container(expand=1, height=45)
                else:
                    date_str = f"{self.current_year:04d}-{self.current_month:02d}-{day:02d}"
                    summary = self.month_data.get(date_str, {})
                    cell = self._build_day_cell(day, date_str, summary)
                week_row.controls.append(cell)
            self.calendar_grid.controls.append(week_row)
        
        try:
             self.update()
        except:
             pass

    def _build_day_cell(self, day, date_str, summary):
        is_today = (date_str == self.today.isoformat())
        has_data = bool(summary)
        
        indicators = []
        has_any_activity = False
        if has_data:
            has_any_activity = (summary.get("water_intake", 0) > 0)

        if has_data and has_any_activity:
            water_color = ft.Colors.BLUE_400 if summary.get("water_achieved") else ft.Colors.RED_400
            indicators.append(ft.Container(width=6, height=6, border_radius=3, bgcolor=water_color))

            
        elif has_data and not has_any_activity:
             pass 
             
        indicator_row = ft.Row(controls=indicators, spacing=2, alignment=ft.MainAxisAlignment.CENTER) if indicators else ft.Container(height=6)
        
        return ft.Container(
            content=ft.Column([
                ft.Text(str(day), size=12, weight=ft.FontWeight.BOLD if is_today else ft.FontWeight.NORMAL,
                       color=ft.Colors.PURPLE_700 if is_today else ft.Colors.BLACK),
                indicator_row
            ], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=1, height=45,
            bgcolor=ft.Colors.PURPLE_100 if is_today else None,
            border=ft.border.all(1, ft.Colors.PURPLE_400) if is_today else None,
            border_radius=8, alignment=ft.Alignment(0, 0), padding=ft.padding.only(top=2),
            on_click=lambda e: self._show_details(date_str, summary), ink=True
        )

    def _show_details(self, date_str, summary):
        if self.page and self.details_dialog not in self.page.overlay:
            self.page.overlay.append(self.details_dialog)
            
        self.details_dialog.title.value = f"{i18n_manager.t('calendar_details_title')} - {date_str}"
        self.details_content.controls.clear()
        
        if not summary:
            self.details_content.controls.append(ft.Container(content=I18nText(key="calendar_no_data", size=12, color=ft.Colors.GREY_500), alignment=ft.Alignment(0,0), expand=True))
        else:
            self._add_detail_row(ft.Icons.WATER_DROP, ft.Colors.BLUE_400, "calendar_water_intake", 
                               f"{summary.get('water_intake',0)}/{summary.get('water_goal',2000)} ml", ft.Colors.BLUE_50)

        self.details_dialog.open = True
        self.page.update()

    def _add_detail_row(self, icon, icon_color, title_key, value_text, bg_color):
        self.details_content.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(icon, color=icon_color, size=16),
                    ft.Text(i18n_manager.t(title_key), weight=ft.FontWeight.BOLD, size=12),
                    ft.Container(expand=True),
                    ft.Text(value_text, size=12, weight=ft.FontWeight.BOLD)
                ]),
                bgcolor=bg_color, padding=8, border_radius=6
            )
        )

    def _close_dialog(self, e):
        self.details_dialog.open = False
        self.page.update()
