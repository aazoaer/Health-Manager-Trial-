import flet as ft
import datetime
from ui.styles import AppColors, CARD_STYLE
from core import event_bus
from data.storage import load_user_data
from core.i18n import i18n_manager, I18nText

class ExerciseStatsCard(ft.Container):
    def __init__(self):
        super().__init__(**CARD_STYLE)
        self.total_duration = 0
        self.total_calories = 0
        
        self._initialize_data()
        self._init_components()
        self.content = self._build_content()
        self._update_ui(initial_load=True)
        
        event_bus.subscribe(event_bus.EXERCISE_ADDED, self._on_exercise_changed)

    def will_unmount(self):
        pass

    def _initialize_data(self):
        
        user_data = load_user_data()
        daily_exercises = user_data.get("daily_exercises", {})
        
        today = datetime.date.today().isoformat()
        if daily_exercises.get("date") == today:
            records = daily_exercises.get("records", [])
            self.total_duration = sum(r.get("duration_minutes", 0) for r in records)
            self.total_calories = sum(r.get("calories", 0) for r in records)
        else:
            self.total_duration = 0
            self.total_calories = 0

    def _on_exercise_changed(self):
        
        self._initialize_data()
        self._update_ui()

    def _init_components(self):
        self.duration_text = ft.Text(
            "0",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.TEAL_600
        )
        
        self.calories_text = ft.Text(
            "0",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.ORANGE_600
        )

    def _build_content(self):
        return ft.Column([

            ft.Row([
                ft.Icon(ft.Icons.INSIGHTS, color=ft.Colors.TEAL_500),
                I18nText(key="exercise_stats_title", size=18, weight=ft.FontWeight.W_600)
            ]),
            ft.Divider(height=20, color="transparent"),
            

            ft.Row([

                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.TIMER, color=ft.Colors.TEAL_400, size=30),
                        self.duration_text,
                        I18nText(key="exercise_total_duration", size=12, color=ft.Colors.GREY_500)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                    padding=15,
                    bgcolor=ft.Colors.TEAL_50,
                    border_radius=12
                ),
                ft.Container(width=15),

                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT, color=ft.Colors.ORANGE_400, size=30),
                        self.calories_text,
                        I18nText(key="exercise_total_calories", size=12, color=ft.Colors.GREY_500)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                    padding=15,
                    bgcolor=ft.Colors.ORANGE_50,
                    border_radius=12
                )
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        ], spacing=5)

    def _update_ui(self, initial_load=False):
        

        if self.total_duration >= 60:
            hours = self.total_duration // 60
            mins = self.total_duration % 60
            self.duration_text.value = f"{hours}h {mins}m"
        else:
            self.duration_text.value = f"{self.total_duration} {i18n_manager.t('exercise_min')}"
        
        self.calories_text.value = f"{self.total_calories} {i18n_manager.t('exercise_kcal')}"
        
        if not initial_load:
            try:
                self.update()
            except Exception:
                pass
