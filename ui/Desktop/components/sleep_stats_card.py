import flet as ft
import datetime
from ui.styles import AppColors, CARD_STYLE
from core import event_bus
from data.storage import load_user_data
from core.i18n import i18n_manager, I18nText

class SleepStatsCard(ft.Container):
    def __init__(self):
        super().__init__(**CARD_STYLE)
        self.sleep_goal_hours = 8
        self.today_sleep_minutes = 0
        self.week_avg_minutes = 0
        
        self._initialize_data()
        self._init_components()
        self.content = self._build_content()
        self._update_ui(initial_load=True)
        
        event_bus.subscribe(event_bus.SLEEP_ADDED, self._on_sleep_changed)

    def will_unmount(self):
        pass

    def _initialize_data(self):
        
        user_data = load_user_data()
        daily_sleep = user_data.get("daily_sleep", {})
        
        today = datetime.date.today().isoformat()
        if daily_sleep.get("date") == today:
            records = daily_sleep.get("records", [])
            self.today_sleep_minutes = sum(r.get("duration_minutes", 0) for r in records)
        else:
            self.today_sleep_minutes = 0
        

        self.week_avg_minutes = self.today_sleep_minutes

    def _on_sleep_changed(self):
        
        self._initialize_data()
        self._update_ui()

    def _init_components(self):
        self.progress_bar = ft.ProgressBar(
            value=0,
            color=ft.Colors.INDIGO_400,
            bgcolor=ft.Colors.INDIGO_100,
            height=12,
            border_radius=6
        )
        
        self.sleep_text = ft.Text(
            "0h 0m / 8h",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.INDIGO_600
        )
        
        self.goal_achieved_container = ft.Container(
            content=I18nText(
                key="sleep_goal_achieved",
                size=12,
                color=ft.Colors.GREEN_700,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            padding=ft.padding.only(top=10),
            visible=False,
            alignment=ft.Alignment(0, 0)
        )
        
        self.week_avg_text = ft.Text(
            "0h 0m",
            size=14,
            color=ft.Colors.GREY_600
        )

    def _build_content(self):
        return ft.Column([

            ft.Row([
                ft.Icon(ft.Icons.INSIGHTS, color=ft.Colors.INDIGO_400),
                I18nText(key="sleep_stats_title", size=18, weight=ft.FontWeight.W_600)
            ]),
            ft.Divider(height=15, color="transparent"),
            

            ft.Container(
                content=self.sleep_text,
                alignment=ft.Alignment(0, 0)
            ),
            ft.Container(height=10),
            self.progress_bar,
            self.goal_achieved_container,
            
            ft.Divider(height=20, color="transparent"),
            

            ft.Row([

                ft.Container(
                    content=ft.Column([
                        I18nText(key="sleep_goal", size=12, color=ft.Colors.GREY_500),
                        ft.Text(
                            f"{self.sleep_goal_hours} {i18n_manager.t('sleep_hours')}",
                            size=16,
                            weight=ft.FontWeight.W_600,
                            color=ft.Colors.INDIGO_600
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    expand=True,
                    alignment=ft.Alignment(0, 0)
                ),
                ft.VerticalDivider(width=1, color=ft.Colors.GREY_300),

                ft.Container(
                    content=ft.Column([
                        I18nText(key="sleep_avg_week", size=12, color=ft.Colors.GREY_500),
                        self.week_avg_text
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    expand=True,
                    alignment=ft.Alignment(0, 0)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        ], spacing=5)

    def _format_duration(self, minutes):
        
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m"

    def _update_ui(self, initial_load=False):
        
        goal_minutes = self.sleep_goal_hours * 60
        progress = min(self.today_sleep_minutes / goal_minutes, 1.0) if goal_minutes > 0 else 0
        
        self.progress_bar.value = progress
        self.sleep_text.value = f"{self._format_duration(self.today_sleep_minutes)} / {self.sleep_goal_hours}h"
        self.week_avg_text.value = self._format_duration(self.week_avg_minutes)
        

        if progress >= 1.0:
            self.goal_achieved_container.visible = True
            self.progress_bar.color = ft.Colors.GREEN_400
            self.sleep_text.color = ft.Colors.GREEN_700
        else:
            self.goal_achieved_container.visible = False
            self.progress_bar.color = ft.Colors.INDIGO_400
            self.sleep_text.color = ft.Colors.INDIGO_600
        
        self.week_avg_text.weight = ft.FontWeight.W_600
        self.week_avg_text.color = ft.Colors.INDIGO_600
        
        if not initial_load:
            try:
                self.update()
            except Exception:
                pass
