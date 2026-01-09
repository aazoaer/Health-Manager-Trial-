import flet as ft
import datetime
from ui.styles import CARD_STYLE
from data.storage import load_user_data
from core.calculations import calculate_nutrition_goals, calculate_water_goal
from core import event_bus
from core.i18n import i18n_manager, I18nText

class TodayOverviewCard(ft.Container):
    def __init__(self):
        super().__init__(**CARD_STYLE)
        self.padding = 20
        self._init_advice_map()
        
        self._init_components()
        self.content = self._build_content()
        self._update_data()
        

        event_bus.subscribe(event_bus.USER_DATA_SAVED, self._on_data_changed)
        event_bus.subscribe(event_bus.WATER_ADDED, self._on_data_changed)
        event_bus.subscribe(event_bus.SLEEP_ADDED, self._on_data_changed)
        event_bus.subscribe(event_bus.EXERCISE_ADDED, self._on_data_changed)
        
    def did_mount(self):
        pass

    def will_unmount(self):
        pass

    def _init_advice_map(self):
        self.advice_map = {
            "calories": {
                "low": (i18n_manager.t("overview_calories_low_tag"), i18n_manager.t("overview_calories_low_reason"), i18n_manager.t("overview_calories_low_suggestion")),
                "high": (i18n_manager.t("overview_calories_high_tag"), i18n_manager.t("overview_calories_high_reason"), i18n_manager.t("overview_calories_high_suggestion"))
            },
            "protein": {
                "low": (i18n_manager.t("overview_protein_low_tag"), i18n_manager.t("overview_protein_low_reason"), i18n_manager.t("overview_protein_low_suggestion")),
                "high": (i18n_manager.t("overview_protein_high_tag"), i18n_manager.t("overview_protein_high_reason"), i18n_manager.t("overview_protein_high_suggestion"))
            },
            "total_fat": {
                "low": (i18n_manager.t("overview_fat_low_tag"), i18n_manager.t("overview_fat_low_reason"), i18n_manager.t("overview_fat_low_suggestion")),
                "high": (i18n_manager.t("overview_fat_high_tag"), i18n_manager.t("overview_fat_high_reason"), i18n_manager.t("overview_fat_high_suggestion"))
            },
            "fiber": {
                "low": (i18n_manager.t("overview_fiber_low_tag"), i18n_manager.t("overview_fiber_low_reason"), i18n_manager.t("overview_fiber_low_suggestion")),
                "high": (i18n_manager.t("overview_fiber_high_tag"), i18n_manager.t("overview_fiber_high_reason"), i18n_manager.t("overview_fiber_high_suggestion"))
            },
            "sugars": {
                "high": (i18n_manager.t("overview_sugars_high_tag"), i18n_manager.t("overview_sugars_high_reason"), i18n_manager.t("overview_sugars_high_suggestion"))
            },
            "sodium": {
                "high": (i18n_manager.t("overview_sodium_high_tag"), i18n_manager.t("overview_sodium_high_reason"), i18n_manager.t("overview_sodium_high_suggestion"))
            },
            "calcium": {
                "low": (i18n_manager.t("overview_calcium_low_tag"), i18n_manager.t("overview_calcium_low_reason"), i18n_manager.t("overview_calcium_low_suggestion"))
            },
            "vitamin_c": {
                "low": (i18n_manager.t("overview_vitamin_c_low_tag"), i18n_manager.t("overview_vitamin_c_low_reason"), i18n_manager.t("overview_vitamin_c_low_suggestion"))
            },
            "vitamin_d": {
                "low": (i18n_manager.t("overview_vitamin_d_low_tag"), i18n_manager.t("overview_vitamin_d_low_reason"), i18n_manager.t("overview_vitamin_d_low_suggestion"))
            }
        }

    def _init_components(self):

        self.water_text = ft.Text(size=14, weight=ft.FontWeight.BOLD)
        self.water_progress = ft.ProgressBar(color=ft.Colors.BLUE_400, bgcolor=ft.Colors.BLUE_50, expand=True)
        

        self.sleep_text = ft.Text(size=14, weight=ft.FontWeight.BOLD)
        self.sleep_progress = ft.ProgressBar(color=ft.Colors.INDIGO_400, bgcolor=ft.Colors.INDIGO_50, expand=True)
        

        self.exercise_text = ft.Text(size=14, weight=ft.FontWeight.BOLD)
        self.exercise_progress = ft.ProgressBar(color=ft.Colors.TEAL_400, bgcolor=ft.Colors.TEAL_50, expand=True)
        
        self.advice_wrap = ft.Row(wrap=True, spacing=10, run_spacing=10)

    def _build_content(self):
        return ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.ASSESSMENT_OUTLINED, color=ft.Colors.INDIGO_500),
                I18nText(key="overview_title", size=18, weight=ft.FontWeight.W_600)
            ]),
            ft.Divider(height=10, color="transparent"),
            

            ft.Row([
                ft.Icon(ft.Icons.WATER_DROP, color=ft.Colors.BLUE_400, size=16),
                I18nText(key="overview_water_status", size=12, color=ft.Colors.GREY_700),
                ft.Container(expand=True),
                self.water_text
            ]),
            ft.Row([self.water_progress]),
            
            ft.Divider(height=5, color="transparent"),
            

            ft.Row([
                ft.Icon(ft.Icons.BEDTIME, color=ft.Colors.INDIGO_400, size=16),
                I18nText(key="overview_sleep_status", size=12, color=ft.Colors.GREY_700),
                ft.Container(expand=True),
                self.sleep_text
            ]),
            ft.Row([self.sleep_progress]),
            
            ft.Divider(height=5, color="transparent"),
            

            ft.Row([
                ft.Icon(ft.Icons.FITNESS_CENTER, color=ft.Colors.TEAL_400, size=16),
                I18nText(key="overview_exercise_status", size=12, color=ft.Colors.GREY_700),
                ft.Container(expand=True),
                self.exercise_text
            ]),
            ft.Row([self.exercise_progress]),
            
            ft.Divider(),
            

            I18nText(key="overview_health_advice", size=14, color=ft.Colors.GREY_700),
            ft.Column(
                [self.advice_wrap],
                scroll=ft.ScrollMode.HIDDEN,
                expand=True,
                height=150
            )
        ], spacing=5)

    def _on_data_changed(self, *args, **kwargs):
        if not self.page:
            return
        self._update_data()
        self.update()

    def _update_data(self):
        user_data = load_user_data()
        if not user_data:
            return

        today = datetime.date.today().isoformat()

        water_intake = int(user_data.get("water_intake", 0))
        water_goal = calculate_water_goal(user_data)
        self.water_text.value = f"{water_intake}/{water_goal}ml"
        self.water_progress.value = min(water_intake / water_goal, 1.0) if water_goal > 0 else 0

        daily_sleep = user_data.get("daily_sleep", {})
        sleep_duration = 0
        if daily_sleep.get("date") == today:
            records = daily_sleep.get("records", [])
            sleep_duration = sum(r.get("duration_minutes", 0) for r in records)
        
        sleep_goal = 480
        sleep_hours = sleep_duration // 60
        sleep_mins = sleep_duration % 60
        self.sleep_text.value = f"{sleep_hours}h{sleep_mins}m"
        self.sleep_progress.value = min(sleep_duration / sleep_goal, 1.0) if sleep_goal > 0 else 0

        daily_exercises = user_data.get("daily_exercises", {})
        exercise_duration = 0
        if daily_exercises.get("date") == today:
            records = daily_exercises.get("records", [])
            exercise_duration = sum(r.get("duration_minutes", 0) for r in records)
        

        

        exercise_intensity = user_data.get("exercise_intensity", "sedentary")
        age = int(user_data.get("age", 30))
        

        if "very_active" in exercise_intensity or "extra_active" in exercise_intensity or "high_active" in exercise_intensity:
            exercise_goal = 60
        elif "moderately_active" in exercise_intensity or "medium_active" in exercise_intensity:
            exercise_goal = 45
        elif "light_active" in exercise_intensity or "low_active" in exercise_intensity:
            exercise_goal = 30
        else:
            exercise_goal = 20
        

        if age >= 65:
            exercise_goal = max(15, exercise_goal - 15)
        elif age < 18:
            exercise_goal = max(30, exercise_goal + 15)
        
        self.exercise_text.value = f"{exercise_duration}/{exercise_goal}min"
        self.exercise_progress.value = min(exercise_duration / exercise_goal, 1.0) if exercise_goal > 0 else 0

        self.advice_wrap.controls.clear()
        
        goals = calculate_nutrition_goals(user_data)
        
        current_intake = {}
        daily_meals = user_data.get("daily_meals", {})
        if isinstance(daily_meals, dict):
            meals = daily_meals.get("meals", [])
            for meal in meals:
                nutrients = meal.get('level1', {})
                for key, value in nutrients.items():
                    current_intake[key] = current_intake.get(key, 0) + value

        has_advice = False
        for key, advice_info in self.advice_map.items():
            if key not in goals: continue
            
            current = current_intake.get(key, 0)
            target_range = goals[key]["range"]
            min_val = target_range[0]
            max_val = target_range[2]
            
            status = None
            if current < min_val and "low" in advice_info:
                status = "low"
            elif current > max_val and "high" in advice_info:
                status = "high"
            
            if status:
                has_advice = True
                tag, reason, suggestion = advice_info[status]
                color = ft.Colors.ORANGE_700 if status == "low" else ft.Colors.RED_700
                bg_color = ft.Colors.ORANGE_50 if status == "low" else ft.Colors.RED_50
                border_color = ft.Colors.ORANGE_200 if status == "low" else ft.Colors.RED_200
                
                card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"{key.replace('_', ' ').title()} {tag}", weight=ft.FontWeight.BOLD, color=color, size=12),
                        ]),
                        ft.Text(f"{reason}", size=11, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"{i18n_manager.t('overview_advice_suggestion')} {suggestion}", size=11, weight=ft.FontWeight.BOLD, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                    ], spacing=2),
                    padding=8,
                    bgcolor=bg_color,
                    border_radius=5,
                    border=ft.border.all(1, border_color),
                    width=180,
                    height=90
                )
                self.advice_wrap.controls.append(card)

        if not has_advice:
            self.advice_wrap.controls.append(
                ft.Container(
                    content=I18nText(key="overview_good_status", color=ft.Colors.GREEN_700),
                    padding=10,
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=5,
                    width=300
                )
            )
