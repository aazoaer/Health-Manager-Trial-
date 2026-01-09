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
        super().__init__(**CARD_STYLE)
        self.expand = True
        self.padding = 20
        
        self.current_year = datetime.date.today().year
        self.current_month = datetime.date.today().month
        self.today = datetime.date.today()
        self.month_data = {}
        
        self.charts_column = ft.Column(spacing=20, scroll=ft.ScrollMode.AUTO)
        
        self.content = self._build_content()
        self._load_month_data()
        self._build_charts()
        

        event_bus.subscribe(event_bus.USER_DATA_SAVED, self._on_data_changed)
        event_bus.subscribe(event_bus.WATER_ADDED, self._on_data_changed)
        event_bus.subscribe(event_bus.SLEEP_ADDED, self._on_data_changed)
        event_bus.subscribe(event_bus.EXERCISE_ADDED, self._on_data_changed)

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
            I18nText(key="calendar_monthly_trends", size=16, weight=ft.FontWeight.BOLD),
            ft.Divider(height=10, color="transparent"),
            self._build_advanced_chart("💧 " + i18n_manager.t("calendar_water_trend"), "water", ft.Colors.BLUE_400, target=1.0),
            self._build_advanced_chart("🍎 " + i18n_manager.t("calendar_nutrition_trend"), "nutrition_score", ft.Colors.ORANGE_400, target=1.0),
            self._build_advanced_chart("😴 " + i18n_manager.t("calendar_sleep_trend"), "sleep_grade", ft.Colors.INDIGO_400, target=1.0),
            self._build_advanced_chart("💪 " + i18n_manager.t("calendar_exercise_trend"), "exercise_score", ft.Colors.TEAL_400, target=1.0),
        ]

    def _build_advanced_chart(self, title: str, data_key: str, color: ft.Colors, target: float = 0.8):
        days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
        

        bar_width = 8
        max_height = 90
        
        bars = []
        

        for day in range(1, days_in_month + 1):
            date_obj = datetime.date(self.current_year, self.current_month, day)
            date_str = date_obj.isoformat()
            

            if date_obj > self.today:
                bars.append(ft.Container(height=1, bgcolor=ft.Colors.TRANSPARENT, expand=1))
                continue
                
            summary = self.month_data.get(date_str, {})
            

            value = 0.0
            has_record = False
            
            if data_key == "water":
                intake = summary.get("water_intake", 0)
                goal = summary.get("water_goal", 2000) or 2000
                if intake > 0:
                    value = intake / goal
                    has_record = True
                
            elif data_key == "sleep_grade":
                grade = summary.get(data_key, "F")
                if summary.get("sleep_duration", 0) > 0:
                     grade_map = {"A": 1.0, "B": 0.8, "C": 0.6, "D": 0.4, "F": 0.2}
                     value = grade_map.get(grade, 0.2)
                     has_record = True
                     
            else:
                score = summary.get(data_key, 0)
                if score > 0:
                    value = score / 100.0
                    has_record = True
            

            if not has_record:
                bars.append(ft.Container(
                    height=max_height, 
                    bgcolor=ft.Colors.GREY_200, 
                    border_radius=2,
                    expand=1
                ))
            else:

                display_value = min(value, 1.0)
                bar_height = max(display_value * max_height, 2)
                
                bars.append(ft.Container(
                    height=bar_height, 
                    bgcolor=color, 
                    border_radius=2,
                    expand=1
                ))

        line_top = max_height - (target * max_height)
        
        standard_line = ft.Container(
            border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_400)),

            height=1,
            width=None,
            bgcolor=ft.Colors.GREY_400,
            opacity=0.5
        )

        

        

        chart_width = days_in_month * (bar_width + 2)
        

        
        chart_stack = ft.Stack(
            controls=[

                ft.Container(
                    content=ft.Row(
                        controls=bars,
                        spacing=2,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.END
                    ),
                    height=max_height,
                ),

                ft.Container(
                     top=line_top,
                     left=0,
                     right=0,
                     height=1,
                     bgcolor=ft.Colors.GREY_400,
                     opacity=0.5,
                )
            ],
            height=max_height
        )

        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=13, weight=ft.FontWeight.W_500),
                chart_stack
            ], spacing=15),
            padding=10, border_radius=8
        )
