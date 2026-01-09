
import flet as ft
import datetime
import calendar
import asyncio
from ui.styles import AppColors, CARD_STYLE
from data.storage import load_month_summaries
from core.i18n import i18n_manager, I18nText
from core import event_bus

class CalendarChartCard(ft.Container):
    
    
    def __init__(self):
        mobile_style = {**CARD_STYLE, "padding": 12}
        super().__init__(**mobile_style)
        self.expand = True
        
        self.current_year = datetime.date.today().year
        self.current_month = datetime.date.today().month
        self.today = datetime.date.today()
        self.month_data = {}
        
        self.charts_column = ft.Column(spacing=15)
        
        self.content = self._build_content()
        self._load_month_data()
        self._build_charts()
        
        event_bus.subscribe(event_bus.USER_DATA_SAVED, self._on_data_changed)
        event_bus.subscribe(event_bus.WATER_ADDED, self._on_data_changed)

    def will_unmount(self):
        event_bus.unsubscribe(event_bus.USER_DATA_SAVED, self._on_data_changed)
        event_bus.unsubscribe(event_bus.WATER_ADDED, self._on_data_changed)

    def _build_content(self):
        return self.charts_column

    def _on_data_changed(self, *args, **kwargs):
        if not self.page: return
        asyncio.create_task(self.refresh_data())

    def update_month(self, year, month):
        self.current_year = year
        self.current_month = month
        asyncio.create_task(self.refresh_data())

    async def refresh_data(self):
        self._load_month_data()
        self._build_charts()
        self.update()

    def _load_month_data(self):
        self.month_data = load_month_summaries(self.current_year, self.current_month)

    def _build_charts(self):
        self.charts_column.controls = [
            I18nText(key="calendar_monthly_trends", size=14, weight=ft.FontWeight.BOLD),
            ft.Divider(height=8, color="transparent"),

            ft.Row([
                ft.Column([
                    self._build_mini_chart("💧 " + i18n_manager.t("calendar_water_trend"), "water", ft.Colors.BLUE_400),
                    self._build_mini_chart("🍎 " + i18n_manager.t("calendar_nutrition_trend"), "nutrition_score", ft.Colors.ORANGE_400),
                    self._build_mini_chart("😴 " + i18n_manager.t("calendar_sleep_trend"), "sleep_grade", ft.Colors.INDIGO_400),
                    self._build_mini_chart("💪 " + i18n_manager.t("calendar_exercise_trend"), "exercise_score", ft.Colors.TEAL_400),
                ], spacing=12, expand=True)
            ], scroll=ft.ScrollMode.HIDDEN) 
        ]

    def _build_mini_chart(self, title: str, data_key: str, color: ft.Colors):

        days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
        max_height = 40
        
        bars = []
        for day in range(1, days_in_month + 1):
            date_str = datetime.date(self.current_year, self.current_month, day).isoformat()
            if datetime.date(self.current_year, self.current_month, day) > self.today:
                bars.append(ft.Container(expand=1, height=1))
                continue
                
            summary = self.month_data.get(date_str, {})
            value = 0.0
            

            if data_key == "water":
                intake = summary.get("water_intake", 0)
                goal = summary.get("water_goal", 2000) or 2000
                if intake > 0: value = min(intake / goal, 1.0)
            elif data_key == "sleep_grade":
                grade = summary.get(data_key, "F")
                if summary.get("sleep_duration", 0) > 0:
                    grade_map = {"A": 1.0, "B": 0.8, "C": 0.6, "D": 0.4, "F": 0.2}
                    value = grade_map.get(grade, 0.2)
            else:
                score = summary.get(data_key, 0)
                if score > 0: value = score / 100.0

            if value > 0:
                bars.append(ft.Container(
                    expand=1, 
                    height=max(value * max_height, 2), 
                    bgcolor=color, 
                    border_radius=1
                ))
            else:
                bars.append(ft.Container(
                    expand=1, 
                    height=max_height, 
                    bgcolor=ft.Colors.GREY_100, 
                    border_radius=1
                ))

        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=11, weight=ft.FontWeight.W_500),
                ft.Container(
                    content=ft.Row(
                        controls=bars,
                        spacing=1,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.END
                    ),
                    height=max_height,
                )
            ], spacing=4),
            padding=6,
            bgcolor=ft.Colors.with_opacity(0.05, color),
            border_radius=8
        )
