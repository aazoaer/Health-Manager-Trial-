import flet as ft
from ui.styles import AppColors, CARD_STYLE
from data.storage import load_user_data
from core import event_bus
from core.i18n import i18n_manager, I18nText

class WaterFormulaCard(ft.Container):
    def __init__(self):
        super().__init__(**CARD_STYLE)
        self.padding = 25
        self._init_components()
        self.content = self._build_content()
        
        self._update_calculation(update_ui=False)
        
        event_bus.subscribe(event_bus.USER_DATA_SAVED, self._on_user_data_saved)

    def _init_components(self):
        self.header = ft.Row([
            ft.Icon(ft.Icons.FUNCTIONS, color=ft.Colors.INDIGO_500),
            I18nText(key="water_formula_title", size=18, weight=ft.FontWeight.W_600, color=ft.Colors.INDIGO_900)
        ])

        self.steps_column = ft.Column(spacing=15)
        
        self.result_text = ft.Text(
            value="0 ml", 
            size=24, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLUE_600
        )

    def _build_content(self):
        return ft.Column([
            self.header,
            ft.Divider(height=20, color=ft.Colors.GREY_200),
            I18nText(key="water_formula_formula_title", size=12, color=ft.Colors.GREY_500),
            ft.Container(
                content=I18nText(key="water_formula_formula", 
                               size=13, weight=ft.FontWeight.BOLD, font_family="Consolas, monospace", 
                               color=ft.Colors.INDIGO_400),
                bgcolor=ft.Colors.INDIGO_50,
                padding=10,
                border_radius=5,
                margin=ft.margin.only(bottom=10)
            ),
            self.steps_column,
            ft.Divider(height=20, color=ft.Colors.GREY_200),
            ft.Row([
                I18nText(key="water_formula_result", size=16, weight=ft.FontWeight.W_600),
                self.result_text
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ])

    def _create_step_row(self, label, formula, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=16, color=color),
                    ft.Text(label, size=14, weight=ft.FontWeight.W_500),
                ], spacing=8),
                ft.Text(
                    formula, 
                    size=13, 
                    color=ft.Colors.GREY_700, 
                    font_family="Consolas, monospace",
                    no_wrap=False
                ),
                ft.Text(
                    f"{value:+d} ml" if isinstance(value, int) else value, 
                    size=14, 
                    weight=ft.FontWeight.BOLD, 
                    color=ft.Colors.GREEN_600 if isinstance(value, int) and value > 0 else (ft.Colors.RED_400 if isinstance(value, int) and value < 0 else ft.Colors.GREY_800)
                )
            ], spacing=5),
            padding=ft.padding.symmetric(vertical=8, horizontal=5)
        )

    def _on_user_data_saved(self, *args, **kwargs):
        self._update_calculation(update_ui=True)

    def _update_calculation(self, user_data=None, update_ui=True):
        if user_data is None:
            user_data = load_user_data()
        
        if not user_data:
            self.steps_column.controls = [I18nText(key="water_formula_no_data", color=ft.Colors.GREY_500)]
            self.result_text.value = i18n_manager.t("water_formula_default")
            if update_ui and hasattr(self, '_page') and self._page is not None:
                self.update()
            return

        try:
            weight = float(user_data.get("weight", 0))
            age = int(user_data.get("age", 0))
            height = float(user_data.get("height", 0))
            exercise = user_data.get("exercise_intensity", "")
            environment = user_data.get("environment", "")

            if weight <= 0:
                return

            coefficient = 30
            age_desc = i18n_manager.t("water_formula_age_adult")
            if 3 <= age <= 12:
                coefficient = 50
                age_desc = i18n_manager.t("water_formula_age_child")
            elif 13 <= age <= 17:
                coefficient = 40
                age_desc = i18n_manager.t("water_formula_age_teen")
            elif 18 <= age <= 55:
                coefficient = 33
                age_desc = i18n_manager.t("water_formula_age_young")
            elif 56 <= age <= 65:
                coefficient = 28
                age_desc = i18n_manager.t("water_formula_age_middle")
            elif age >= 66:
                coefficient = 23
                age_desc = i18n_manager.t("water_formula_age_elderly")
            
            base_intake = int(weight * coefficient)
            
            height_adj = 0
            height_desc = i18n_manager.t("water_formula_height_standard")
            if height >= 175:
                height_adj = 250
                height_desc = i18n_manager.t("water_formula_height_tall")
            elif height <= 155:
                height_adj = -150
                height_desc = i18n_manager.t("water_formula_height_short")

            exercise_adj = 0
            ex_desc = i18n_manager.t("water_formula_exercise_none")

            if "light_active" in exercise:
                exercise_adj = 400
                ex_desc = i18n_manager.t("water_formula_exercise_light")
            elif "moderately_active" in exercise:
                exercise_adj = 750
                ex_desc = i18n_manager.t("water_formula_exercise_moderate")
            elif "very_active" in exercise or "extra_active" in exercise or "high_active" in exercise:
                exercise_adj = 1000
                ex_desc = i18n_manager.t("water_formula_exercise_heavy")

            env_adj = 0
            env_desc = i18n_manager.t("water_formula_env_normal")

            if "hot_env" in environment:
                env_adj = 400
                env_desc = i18n_manager.t("water_formula_env_hot")
            elif "ac_env" in environment:
                env_adj = 200
                env_desc = i18n_manager.t("water_formula_env_dry")

            total = base_intake + height_adj + exercise_adj + env_adj
            final_total = int(round(total / 10) * 10)

            self.steps_column.controls = [
                self._create_step_row(
                    i18n_manager.t("water_formula_base"), 
                    f"{weight}kg × {coefficient} ({age_desc})", 
                    base_intake, 
                    ft.Icons.SCALE, 
                    ft.Colors.BLUE_400
                ),
                self._create_step_row(
                    i18n_manager.t("water_formula_height"), 
                    f"{height}cm ({height_desc})", 
                    height_adj, 
                    ft.Icons.HEIGHT, 
                    ft.Colors.TEAL_400
                ),
                self._create_step_row(
                    i18n_manager.t("water_formula_exercise"), 
                    f"{ex_desc}", 
                    exercise_adj, 
                    ft.Icons.DIRECTIONS_RUN, 
                    ft.Colors.ORANGE_400
                ),
                self._create_step_row(
                    i18n_manager.t("water_formula_environment"), 
                    f"{env_desc}", 
                    env_adj, 
                    ft.Icons.WB_SUNNY, 
                    ft.Colors.AMBER_500
                ),
            ]
            
            self.result_text.value = f"{final_total} ml"
            
            if update_ui and hasattr(self, '_page') and self._page is not None:
                self.update()

        except (ValueError, TypeError):
            pass
