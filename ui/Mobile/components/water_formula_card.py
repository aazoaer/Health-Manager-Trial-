
import flet as ft
from ui.styles import AppColors, CARD_STYLE
from data.storage import load_user_data
from core import event_bus
from core.i18n import i18n_manager, I18nText

class WaterFormulaCard(ft.Container):
    
    
    def __init__(self):
        mobile_style = {**CARD_STYLE, "padding": 12}
        super().__init__(**mobile_style)
        
        self._init_components()
        self.content = self._build_content()
        self._update_calculation(update_ui=False)
        event_bus.subscribe(event_bus.USER_DATA_SAVED, self._on_user_data_saved)

    def _init_components(self):

        self.result_text = ft.Text(
            value="0 ml", 
            size=18, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLUE_600
        )

        self.steps_column = ft.Column(spacing=8)

    def _build_content(self):
        return ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.FUNCTIONS, color=ft.Colors.INDIGO_500, size=20),
                I18nText(key="water_formula_title", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.INDIGO_900)
            ], spacing=6),
            
            ft.Divider(height=12, color=ft.Colors.GREY_200),
            

            ft.Container(
                content=I18nText(
                    key="water_formula_formula", 
                    size=11, 
                    weight=ft.FontWeight.BOLD, 
                    font_family="Consolas, monospace", 
                    color=ft.Colors.INDIGO_400
                ),
                bgcolor=ft.Colors.INDIGO_50,
                padding=6,
                border_radius=4,
                margin=ft.margin.only(bottom=6)
            ),
            
            self.steps_column,
            
            ft.Divider(height=12, color=ft.Colors.GREY_200),
            
            ft.Row([
                I18nText(key="water_formula_result", size=14, weight=ft.FontWeight.W_600),
                self.result_text
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ], spacing=4)

    def _create_step_row(self, label, formula, value, icon, color):

        return ft.Container(
            content=ft.Row([

                ft.Row([
                    ft.Icon(icon, size=14, color=color),
                    ft.Text(label, size=12, weight=ft.FontWeight.W_500),
                ], spacing=6, expand=1),
                

                ft.Text(
                    f"{value:+d}" if isinstance(value, int) else str(value), 
                    size=12, 
                    weight=ft.FontWeight.BOLD, 
                    color=ft.Colors.GREEN_600 if isinstance(value, int) and value > 0 else (ft.Colors.RED_400 if isinstance(value, int) and value < 0 else ft.Colors.GREY_800)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(vertical=4, horizontal=2)
        )

    def _on_user_data_saved(self, *args, **kwargs):
        self._update_calculation(update_ui=True)

    def _update_calculation(self, user_data=None, update_ui=True):
        if user_data is None:
            user_data = load_user_data()
        
        if not user_data:
            self.steps_column.controls = [I18nText(key="water_formula_no_data", size=11, color=ft.Colors.GREY_500)]
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
            if 3 <= age <= 12: coefficient = 50
            elif 13 <= age <= 17: coefficient = 40
            elif 18 <= age <= 55: coefficient = 33
            elif 56 <= age <= 65: coefficient = 28
            elif age >= 66: coefficient = 23
            
            base_intake = int(weight * coefficient)
            

            height_adj = 0
            if height >= 175: height_adj = 250
            elif height <= 155: height_adj = -150

            exercise_adj = 0
            if "light_active" in exercise: exercise_adj = 400
            elif "moderately_active" in exercise: exercise_adj = 750
            elif "very_active" in exercise or "extra_active" in exercise or "high_active" in exercise: exercise_adj = 1000

            env_adj = 0
            if "hot_env" in environment: env_adj = 400
            elif "ac_env" in environment: env_adj = 200

            total = base_intake + height_adj + exercise_adj + env_adj
            final_total = int(round(total / 10) * 10)

            self.steps_column.controls = [
                self._create_step_row(i18n_manager.t("water_formula_base"), "", base_intake, ft.Icons.SCALE, ft.Colors.BLUE_400),
                self._create_step_row(i18n_manager.t("water_formula_height"), "", height_adj, ft.Icons.HEIGHT, ft.Colors.TEAL_400),
                self._create_step_row(i18n_manager.t("water_formula_exercise"), "", exercise_adj, ft.Icons.DIRECTIONS_RUN, ft.Colors.ORANGE_400),
                self._create_step_row(i18n_manager.t("water_formula_environment"), "", env_adj, ft.Icons.WB_SUNNY, ft.Colors.AMBER_500),
            ]
            
            self.result_text.value = f"{final_total} ml"
            
            if update_ui and hasattr(self, '_page') and self._page is not None:
                self.update()

        except (ValueError, TypeError):
            pass
