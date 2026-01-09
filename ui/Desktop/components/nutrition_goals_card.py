import flet as ft
from ui.styles import CARD_STYLE
from core.calculations import calculate_nutrition_goals
from data.storage import load_user_data
from core import event_bus
from core.i18n import i18n_manager, I18nText

class _GoalBar(ft.Container):
    
    def __init__(self, label: str, unit: str, goal_range: list):
        super().__init__()
        self.label = label
        self.unit = unit
        self.goal_range = goal_range
        self.current_value = 0

        self.height = 50 
        self.content = self._build()

    def _build(self):
        self.progress_text = ft.Text(f"0 / {self.goal_range[1]:.1f} {self.unit}", size=12, color=ft.Colors.BLACK87)
        
        self.left_spacer = ft.Container(expand=0) 
        self.right_spacer = ft.Container(expand=1) 

        pointer_icon = ft.Icon(ft.Icons.ARROW_DROP_UP, size=24, color=ft.Colors.BLACK)

        min_val, ideal_val, max_val = self.goal_range
        self.display_max = max_val * 1.1 if max_val > 0 else 100
        
        expand_low = int((min_val / self.display_max) * 1000)
        expand_good = int(((max_val - min_val) / self.display_max) * 1000)
        expand_high = int(((self.display_max - max_val) / self.display_max) * 1000)
        
        if expand_low + expand_good + expand_high == 0:
            expand_good = 1

        self.progress_stack = ft.Stack(
            [
                ft.Container(
                    content=ft.Row([
                        ft.Container(bgcolor=ft.Colors.RED_200, height=16, expand=expand_low),
                        ft.Container(bgcolor=ft.Colors.GREEN_200, height=16, expand=expand_good),
                        ft.Container(bgcolor=ft.Colors.RED_200, height=16, expand=expand_high),
                    ], spacing=0),
                    left=0,
                    right=0,
                    top=0,
                    height=16,
                    border_radius=8,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE
                ),
                
                ft.Container(
                    content=ft.Row(
                        [
                            self.left_spacer,
                            ft.Container(
                                content=pointer_icon,
                                width=0, 
                                alignment=ft.Alignment(0, 0)
                            ),
                            self.right_spacer,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=0,
                    ),
                    left=0,
                    right=0,
                    top=12, 
                )
            ],
            height=40 
        )

        return ft.Column([
            ft.Row([
                ft.Text(self.label, weight=ft.FontWeight.BOLD, size=14),
                self.progress_text
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.progress_stack
        ], spacing=5)

    def update_value(self, value: float):
        self.current_value = value
        self.progress_text.value = f"{value:.1f} / {self.goal_range[1]:.1f} {self.unit}"
        
        if self.display_max <= 0:
            progress_percent = 0
        else:
            progress_percent = max(0, min(1, value / self.display_max))
        
        self.left_spacer.expand = int(progress_percent * 1000)
        self.right_spacer.expand = int((1 - progress_percent) * 1000)
        
        if self.page:
            self.update()

class NutritionGoalsCard(ft.Container):
    def __init__(self, food_card_ref):
        super().__init__(**CARD_STYLE)
        self.food_card_ref = food_card_ref
        self.is_expanded = False
        self.goals = {}
        self.goal_bars = {}

        self._initialize_goals()
        self._init_components()
        self.content = self._build()
        
    def did_mount(self):
        self._update_from_meals()
        event_bus.subscribe(event_bus.USER_DATA_SAVED, self._on_user_data_changed)

    def will_unmount(self):
        event_bus.unsubscribe(event_bus.USER_DATA_SAVED, self._on_user_data_changed)

    def _initialize_goals(self):
        user_data = load_user_data()
        self.goals = calculate_nutrition_goals(user_data)

    def _on_user_data_changed(self, *args, **kwargs):
        if not self.page:
            return

        user_data = load_user_data()
        self.goals = calculate_nutrition_goals(user_data)
        self._update_goal_bars()
        self._update_from_meals()

    def _update_from_meals(self):
        current_totals = self._calculate_totals()
        for key, bar in self.goal_bars.items():
            bar.update_value(current_totals.get(key, 0))
        if self.page:
            self.update()

    def _calculate_totals(self):
        totals = {}
        if self.food_card_ref and hasattr(self.food_card_ref, 'meals'):
            for meal in self.food_card_ref.meals:
                nutrients = meal.get('level1', {})
                for key, value in nutrients.items():
                    totals[key] = totals.get(key, 0) + value
        return totals

    def _init_components(self):
        self.arrow_button = ft.IconButton(
            icon=ft.Icons.ADD_CIRCLE,
            on_click=self._toggle_expand
        )
        self.title = I18nText(key="nutrient_title", size=18, weight=ft.FontWeight.W_600)
        
        self.header = ft.Row(
            [self.title, self.arrow_button],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        self.expandable_content = ft.Column(visible=self.is_expanded, spacing=10)
        
        nutrient_label_map = {
            "calories": i18n_manager.t("nutrient_calories"),
            "protein": i18n_manager.t("nutrient_protein"),
            "total_fat": i18n_manager.t("nutrient_fat"),
            "total_carbs": i18n_manager.t("nutrient_carbs"),
            "fiber": i18n_manager.t("nutrient_fiber"),
            "sugars": i18n_manager.t("nutrient_sugar"),
            "sodium": i18n_manager.t("nutrient_sodium"),
            "calcium": i18n_manager.t("nutrient_calcium"),
            "vitamin_c": i18n_manager.t("nutrient_vitamin_c"),
            "vitamin_d": i18n_manager.t("nutrient_vitamin_d"),
        }
        for key, data in self.goals.items():
            label = nutrient_label_map.get(key, key.replace("_", " ").title())
            bar = _GoalBar(label=label, unit=data["unit"], goal_range=data["range"])
            self.goal_bars[key] = bar
            self.expandable_content.controls.append(bar)

    def _build(self):
        return ft.Column(
            [
                self.header,
                self.expandable_content
            ],
            spacing=10
        )

    def _toggle_expand(self, e):
        self.is_expanded = not self.is_expanded
        self.expandable_content.visible = self.is_expanded
        self.arrow_button.icon = ft.Icons.REMOVE_CIRCLE if self.is_expanded else ft.Icons.ADD_CIRCLE
        self.update()

    def _update_goal_bars(self):
        self.expandable_content.controls.clear()
        self.goal_bars.clear()
        nutrient_label_map = {
            "calories": i18n_manager.t("nutrient_calories"),
            "protein": i18n_manager.t("nutrient_protein"),
            "total_fat": i18n_manager.t("nutrient_fat"),
            "total_carbs": i18n_manager.t("nutrient_carbs"),
            "fiber": i18n_manager.t("nutrient_fiber"),
            "sugars": i18n_manager.t("nutrient_sugar"),
            "sodium": i18n_manager.t("nutrient_sodium"),
            "calcium": i18n_manager.t("nutrient_calcium"),
            "vitamin_c": i18n_manager.t("nutrient_vitamin_c"),
            "vitamin_d": i18n_manager.t("nutrient_vitamin_d"),
        }
        for key, data in self.goals.items():
            label = nutrient_label_map.get(key, key.replace("_", " ").title())
            bar = _GoalBar(label=label, unit=data["unit"], goal_range=data["range"])
            self.goal_bars[key] = bar
            self.expandable_content.controls.append(bar)
        if self.page:
            self.update()
