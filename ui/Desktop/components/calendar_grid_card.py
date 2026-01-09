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
        super().__init__(**CARD_STYLE)
        self.width = 430
        self.padding = 40
        
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
        event_bus.subscribe(event_bus.SLEEP_ADDED, self._on_data_changed)
        event_bus.subscribe(event_bus.EXERCISE_ADDED, self._on_data_changed)

    def did_mount(self):

        from data.storage import update_today_summary
        try:
            update_today_summary()
        except Exception:
            pass
        asyncio.create_task(self.refresh_data())

    def will_unmount(self):
        if self.page and self.details_dialog in self.page.overlay:
            self.page.overlay.remove(self.details_dialog)

    def _on_data_changed(self, *args, **kwargs):
        if not self.page: return
        asyncio.create_task(self.refresh_data())

    def _init_components(self):
        self.month_label = ft.Text(
            "", size=18, weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        self.calendar_grid = ft.Column(spacing=2)
        

        self.details_content = ft.Column(spacing=10)
        self.details_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(i18n_manager.t("calendar_details_title")),
            content=ft.Container(
                content=self.details_content,
                width=350, height=280
            ),
            actions=[ft.TextButton("OK", on_click=self._close_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def _build_content(self):
        weekday_keys = ["weekday_mon", "weekday_tue", "weekday_wed", 
                        "weekday_thu", "weekday_fri", "weekday_sat", "weekday_sun"]
        
        weekday_row = ft.Row(
            controls=[
                ft.Container(
                    content=I18nText(key=k, size=12, weight=ft.FontWeight.BOLD, 
                                    color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                    width=50, alignment=ft.Alignment(0, 0)
                ) for k in weekday_keys
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=2
        )
        
        return ft.Column([

            ft.Row([
                ft.Icon(ft.Icons.CALENDAR_MONTH, color=ft.Colors.PURPLE_500),
                I18nText(key="calendar_title", size=18, weight=ft.FontWeight.W_600)
            ]),
            ft.Divider(height=15, color="transparent"),
            

            ft.Row([
                ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, icon_color=ft.Colors.PURPLE_500, on_click=self._prev_month),
                ft.Container(content=self.month_label, expand=True, alignment=ft.Alignment(0, 0)),
                ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, icon_color=ft.Colors.PURPLE_500, on_click=self._next_month),
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Divider(height=10, color="transparent"),
            weekday_row,
            ft.Divider(height=5, color="transparent"),
            self.calendar_grid
        ], spacing=5)

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
                    cell = ft.Container(width=50, height=55)
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
            has_any_activity = (summary.get("water_intake", 0) > 0 or 
                              summary.get("nutrition_score", 0) > 0 or 
                              summary.get("sleep_duration", 0) > 0 or 
                              summary.get("exercise_duration", 0) > 0)

        if has_data and has_any_activity:

            water_color = ft.Colors.BLUE_400 if summary.get("water_achieved") else ft.Colors.RED_400
            indicators.append(ft.Container(width=8, height=8, border_radius=4, bgcolor=water_color))
            

            score = summary.get("nutrition_score", 0)
            color = ft.Colors.GREEN_400 if score >= 80 else ft.Colors.ORANGE_400 if score >= 60 else ft.Colors.RED_400 if score > 0 else ft.Colors.GREY_300
            indicators.append(ft.Container(width=8, height=8, border_radius=4, bgcolor=color))
            

            grade_colors = {"A": ft.Colors.GREEN_400, "B": ft.Colors.BLUE_400, "C": ft.Colors.ORANGE_400, "D": ft.Colors.RED_400, "F": ft.Colors.GREY_300}
            indicators.append(ft.Container(width=8, height=8, border_radius=4, bgcolor=grade_colors.get(summary.get("sleep_grade", "F"), ft.Colors.GREY_300)))
            

            ex_score = summary.get("exercise_score", 0)
            ex_color = ft.Colors.GREEN_400 if ex_score >= 80 else ft.Colors.ORANGE_400 if ex_score >= 50 else ft.Colors.RED_400 if ex_score > 0 else ft.Colors.GREY_300
            indicators.append(ft.Container(width=8, height=8, border_radius=4, bgcolor=ex_color))
        elif has_data and not has_any_activity:
             for _ in range(4): indicators.append(ft.Container(width=8, height=8, border_radius=4, bgcolor=ft.Colors.GREY_300))
             
        indicator_row = ft.Row(controls=indicators, spacing=2, alignment=ft.MainAxisAlignment.CENTER) if indicators else ft.Container(height=10)
        
        return ft.Container(
            content=ft.Column([
                ft.Text(str(day), size=14, weight=ft.FontWeight.BOLD if is_today else ft.FontWeight.NORMAL,
                       color=ft.Colors.PURPLE_700 if is_today else ft.Colors.BLACK),
                indicator_row
            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=50, height=55,
            bgcolor=ft.Colors.PURPLE_100 if is_today else None,
            border=ft.border.all(2, ft.Colors.PURPLE_400) if is_today else None,
            border_radius=8, alignment=ft.Alignment(0, 0), padding=ft.padding.only(top=5),
            on_click=lambda e: self._show_details(date_str, summary), ink=True
        )

    def _show_details(self, date_str, summary):
        if self.page and self.details_dialog not in self.page.overlay:
            self.page.overlay.append(self.details_dialog)
            
        self.details_dialog.title.value = f"{i18n_manager.t('calendar_details_title')} - {date_str}"
        self.details_content.controls.clear()
        
        if not summary:
            self.details_content.controls.append(ft.Container(content=I18nText(key="calendar_no_data", color=ft.Colors.GREY_500), alignment=ft.Alignment(0,0), expand=True))
        else:

            self._add_detail_row(ft.Icons.WATER_DROP, ft.Colors.BLUE_400, "calendar_water_intake", 
                               f"{summary.get('water_intake',0)}/{summary.get('water_goal',2000)} ml", ft.Colors.BLUE_50)
            self._add_detail_row(ft.Icons.RESTAURANT, ft.Colors.ORANGE_400, "calendar_nutrition_score", 
                               f"{summary.get('nutrition_score',0)}", ft.Colors.ORANGE_50)
            self._add_detail_row(ft.Icons.BEDTIME, ft.Colors.INDIGO_400, "calendar_sleep_grade", 
                               f"{summary.get('sleep_duration',0)//60}h {summary.get('sleep_duration',0)%60}m ({summary.get('sleep_grade','F')})", ft.Colors.INDIGO_50)
            self._add_detail_row(ft.Icons.FITNESS_CENTER, ft.Colors.TEAL_500, "calendar_exercise_score", 
                               f"{summary.get('exercise_score',0)} ({summary.get('exercise_calories',0)} kcal)", ft.Colors.TEAL_50)

        self.details_dialog.open = True
        self.page.update()

    def _add_detail_row(self, icon, icon_color, title_key, value_text, bg_color):
        self.details_content.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(icon, color=icon_color),
                    ft.Text(i18n_manager.t(title_key), weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Text(value_text, size=14, weight=ft.FontWeight.BOLD)
                ]),
                bgcolor=bg_color, padding=10, border_radius=8
            )
        )

    def _close_dialog(self, e):
        self.details_dialog.open = False
        self.page.update()
