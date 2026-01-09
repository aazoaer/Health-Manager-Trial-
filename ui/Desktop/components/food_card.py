import flet as ft
from ui.styles import AppColors, CARD_STYLE
from core.search import search_food
from data.storage import load_user_data, save_user_data
from core.i18n import i18n_manager, I18nText
from ui.Desktop.components.custom_food_dialog import CustomFoodDialog
import copy
import datetime

class FoodCard(ft.Container):
    def __init__(self, nutrition_goals_card_ref):
        super().__init__(**CARD_STYLE)
        self.nutrition_goals_card_ref = nutrition_goals_card_ref
        self.meals = []
        self.selected_food_data = None
        self.margin = ft.margin.only(top=20)
        self._is_selecting = False
        
        self._initialize_data()
        self._init_components()
        self.content = self._build_content()

    def did_mount(self):
        
        if self.page:
            if self.details_dialog not in self.page.overlay:
                self.page.overlay.append(self.details_dialog)
            if self.custom_food_dialog not in self.page.overlay:
                self.page.overlay.append(self.custom_food_dialog)
            self.update_meals_ui()
            self.page.update()

    def will_unmount(self):
        if self.page:
            if self.details_dialog in self.page.overlay:
                self.page.overlay.remove(self.details_dialog)
            if self.custom_food_dialog in self.page.overlay:
                self.page.overlay.remove(self.custom_food_dialog)

    def _initialize_data(self):
        
        user_data = load_user_data()
        daily_meals_data = user_data.get("daily_meals", {})
        
        if isinstance(daily_meals_data, dict):
            last_date_str = daily_meals_data.get("date")
            today_str = datetime.date.today().isoformat()

            if last_date_str == today_str:
                self.meals = daily_meals_data.get("meals", [])
            else:

                self.meals = []
                self._save_meals()
        else:

            self.meals = []

    def _save_meals(self):
        
        today_str = datetime.date.today().isoformat()
        save_user_data({
            "daily_meals": {
                "date": today_str,
                "meals": self.meals
            }
        })

    def _init_components(self):

        control_height = 45

        common_padding = 10

        control_width = 300

        self.food_name_input = ft.TextField(
            label=i18n_manager.t("food_search_placeholder"),
            expand=True,
            height=control_height,
            text_size=14,
            content_padding=common_padding,
            border_radius=8,
            on_change=self._on_search_change
        )

        self.quantity_input = ft.TextField(
            label=i18n_manager.t("food_quantity_label"),
            width=control_width,
            height=control_height,
            text_size=14,
            content_padding=common_padding,
            border_radius=8,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        self.unit_dropdown = ft.Dropdown(
            label=i18n_manager.t("food_unit_label"),
            width=control_width,
            height=control_height,
            content_padding=common_padding,
            text_size=13,
            border_radius=8,
            bgcolor=ft.Colors.GREY_50,
            options=[]
        )

        self.search_results_container = ft.Container(
            content=ft.ListView(spacing=2, padding=0),
            visible=False,
            bgcolor=ft.Colors.WHITE,
            border_radius=5,

        )

        self.meals_list = ft.ListView(spacing=10, height=300, padding=ft.padding.only(right=10))

        self.details_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(i18n_manager.t("food_details_title")),
            content=ft.Container(
                content=ft.Column(height=300, scroll=ft.ScrollMode.ADAPTIVE),
                width=600
            ),
            actions=[ft.TextButton(i18n_manager.t("food_details_close"), on_click=self._close_details_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        

        self.custom_food_dialog = CustomFoodDialog(on_save_callback=self._add_custom_food)

    def _build_content(self):
        return ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.RESTAURANT, color=AppColors.FOOD_ICON),
                I18nText(key="food_title", size=18, weight=ft.FontWeight.W_600),
            ]),

            ft.Divider(height=10, color="transparent"),

            ft.Row([self.food_name_input]),
            

            ft.Row([self.quantity_input]),

            ft.Row(
                [
                    self.unit_dropdown,
                    ft.IconButton(
                        icon=ft.Icons.ADD_CIRCLE,
                        icon_color=AppColors.ADD_BUTTON,
                        icon_size=30,
                        on_click=self.add_meal,
                        tooltip=i18n_manager.t("food_add_tooltip")
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            

            ft.Container(
                content=ft.TextButton(
                    content=ft.Text(i18n_manager.t("food_custom_add")),
                    icon=ft.Icons.EDIT,
                    on_click=self._open_custom_dialog
                ),
                alignment=ft.Alignment(-1, 0)
            ),

            self.search_results_container,
            ft.Divider(),
            I18nText(key="food_today_records", size=14, color=AppColors.TEXT_SECONDARY),
            self.meals_list
        ])

    def _on_search_change(self, e):
        if self._is_selecting: return

        query = self.food_name_input.value
        self.selected_food_data = None

        if not query:
            self.search_results_container.visible = False
            self.search_results_container.content.controls.clear()
            if self.page: self.update()
            return

        results = search_food(query)
        self.search_results_container.content.controls.clear()

        if results:
            for food in results:
                details_button = ft.IconButton(
                    icon=ft.Icons.INFO_OUTLINE,
                    icon_color=ft.Colors.BLUE_400,
                    tooltip=i18n_manager.t("food_view_details"),
                    on_click=lambda _, f=food: self._show_details(f),
                )
                
                result_item = ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(f"{food['name']}", size=14, weight=ft.FontWeight.BOLD, expand=True),
                            details_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=5,
                    on_click=lambda _, f=food: self._select_food(f),
                    ink=True
                )
                self.search_results_container.content.controls.append(result_item)
            

            item_height = 50
            max_items = 5
            count = len(results)
            
            if count > max_items:
                self.search_results_container.height = max_items * item_height
            else:
                self.search_results_container.height = count * item_height
                
            self.search_results_container.visible = True
        else:
            self.search_results_container.visible = False

        if self.page: self.update()

    def _show_details(self, food):
        

        

        nutrients = food.get('level1', {})
        if not nutrients:
            nutrients = {
                'calories': food.get('calories', 0), 'protein': food.get('protein', 0),
                'total_fat': food.get('fat', 0), 'total_carbs': food.get('carbs', 0),
                'fiber': food.get('fiber', 0), 'sugars': food.get('sugar', 0),
                'sodium': food.get('sodium', 0), 'calcium': food.get('calcium', 0),
                'vitamin_c': food.get('vitamin_c', 0), 'vitamin_d': food.get('vitamin_d', 0)
            }

        details_content = [
            ft.Text(food.get('name', i18n_manager.t("food_unknown")), size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([ft.Text(i18n_manager.t("food_calories"), weight=ft.FontWeight.BOLD), ft.Text(f"{nutrients.get('calories', 0)} kcal")]),
            ft.Row([ft.Text(i18n_manager.t("food_protein"), weight=ft.FontWeight.BOLD), ft.Text(f"{nutrients.get('protein', 0)} g")]),
            ft.Row([ft.Text(i18n_manager.t("food_fat"), weight=ft.FontWeight.BOLD), ft.Text(f"{nutrients.get('total_fat', 0)} g")]),
            ft.Row([ft.Text(i18n_manager.t("food_carbs"), weight=ft.FontWeight.BOLD), ft.Text(f"{nutrients.get('total_carbs', 0)} g")]),
            ft.Row([ft.Text(i18n_manager.t("food_fiber"), weight=ft.FontWeight.BOLD), ft.Text(f"{nutrients.get('fiber', 0)} g")]),
            ft.Row([ft.Text(i18n_manager.t("food_sugar"), weight=ft.FontWeight.BOLD), ft.Text(f"{nutrients.get('sugars', 0)} g")]),
            ft.Row([ft.Text(i18n_manager.t("food_sodium"), weight=ft.FontWeight.BOLD), ft.Text(f"{nutrients.get('sodium', 0)} mg")]),
            ft.Row([ft.Text(i18n_manager.t("food_calcium"), weight=ft.FontWeight.BOLD), ft.Text(f"{nutrients.get('calcium', 0)} mg")]),
            ft.Row([ft.Text(i18n_manager.t("food_vitamin_c"), weight=ft.FontWeight.BOLD), ft.Text(f"{nutrients.get('vitamin_c', 0)} mg")]),
            ft.Row([ft.Text(i18n_manager.t("food_vitamin_d"), weight=ft.FontWeight.BOLD), ft.Text(f"{nutrients.get('vitamin_d', 0)} µg")]),
        ]
        

        self.details_dialog.content.content.controls = details_content
        self.details_dialog.open = True
        if self.page: self.page.update()

    def _close_details_dialog(self, e):
        self.details_dialog.open = False
        if self.page: self.page.update()
    
    def _open_custom_dialog(self, e):
        
        self.custom_food_dialog.open = True
        if self.page:
            self.page.update()
    
    def _add_custom_food(self, custom_food):
        
        self.meals.append(custom_food)
        self._save_meals()
        self.update_meals_ui()
        if self.nutrition_goals_card_ref:
            self.nutrition_goals_card_ref._update_from_meals()

    def _select_food(self, food):
        
        try:
            self._is_selecting = True

            self.selected_food_data = food
            self.food_name_input.value = food['name']

            new_options = []
            if 'portions' in food and food.get('portions'):
                new_options = [
                    ft.dropdown.Option(key=portion['unit_name'], text=portion['unit_name'])
                    for portion in food['portions']
                ]
                if new_options:
                    self.unit_dropdown.value = new_options[0].key
                    self.quantity_input.value = "1"
            else:
                new_options.append(ft.dropdown.Option(key="g", text="g"))
                self.unit_dropdown.value = "g"
                self.quantity_input.value = "100"

            self.unit_dropdown.options = new_options
            self.search_results_container.visible = False
            self.search_results_container.content.controls.clear()

            if self.page: self.update()
        finally:
            self._is_selecting = False

    def add_meal(self, e):
        if not self.selected_food_data:
            self.food_name_input.error_text = i18n_manager.t("food_error_select")
            self.food_name_input.update()
            return

        try:
            user_quantity = float(self.quantity_input.value)
            if user_quantity <= 0: raise ValueError()
        except (ValueError, TypeError):
            self.quantity_input.error_text = i18n_manager.t("food_error_invalid")
            self.quantity_input.update()
            return

        selected_unit_name = self.unit_dropdown.value
        if not selected_unit_name:
            self.unit_dropdown.error_text = i18n_manager.t("food_error_unit")
            self.unit_dropdown.update()
            return

        total_grams = 0
        gram_weight = 1
        if 'portions' in self.selected_food_data and self.selected_food_data.get('portions'):
            for portion in self.selected_food_data['portions']:
                if portion['unit_name'] == selected_unit_name:
                    gram_weight = portion['gram_weight']
                    break
            total_grams = user_quantity * gram_weight
        elif selected_unit_name == 'g':
            total_grams = user_quantity

        if total_grams <= 0:
            self.quantity_input.error_text = i18n_manager.t("food_error_invalid")
            self.quantity_input.update()
            return

        scale = total_grams / 100.0
        scaled_meal = copy.deepcopy(self.selected_food_data)
        
        if 'level1' not in scaled_meal:
            scaled_meal['level1'] = {}
            db_to_level1_map = {
                'calories': 'calories', 'protein': 'protein', 'fat': 'total_fat',
                'carbs': 'total_carbs', 'fiber': 'fiber', 'sugar': 'sugars',
                'sodium': 'sodium', 'calcium': 'calcium', 'vitamin_c': 'vitamin_c',
                'vitamin_d': 'vitamin_d'
            }
            for db_key, l1_key in db_to_level1_map.items():
                original_value = self.selected_food_data.get(db_key, 0)
                if isinstance(original_value, (int, float)):
                    scaled_meal['level1'][l1_key] = round(original_value * scale, 2)
        else:
            for level in ['level1', 'level2']:
                if level in scaled_meal:
                    for category in scaled_meal[level]:
                        if isinstance(scaled_meal[level][category], dict):
                            for key, value in scaled_meal[level][category].items():
                                if isinstance(value, (int, float)):
                                    scaled_meal[level][category][key] = round(value * scale, 2)
                        elif isinstance(scaled_meal[level][category], (int, float)):
                             scaled_meal[level][category] = round(scaled_meal[level][category] * scale, 2)

        scaled_meal['serving_eaten'] = {"value": user_quantity, "unit": selected_unit_name}
        self.meals.append(scaled_meal)
        
        self._save_meals()
        
        self.food_name_input.value = ""
        self.quantity_input.value = ""
        self.unit_dropdown.options = []
        self.unit_dropdown.value = None
        self.selected_food_data = None
        self.food_name_input.error_text = None
        self.quantity_input.error_text = None
        self.unit_dropdown.error_text = None
        self.food_name_input.focus()

        self.update_meals_ui()
        if self.nutrition_goals_card_ref:
            self.nutrition_goals_card_ref._update_from_meals()

    def _delete_meal(self, meal_to_delete):
        
        self.meals.remove(meal_to_delete)
        self._save_meals()
        self.update_meals_ui()
        if self.nutrition_goals_card_ref:
            self.nutrition_goals_card_ref._update_from_meals()

    def _build_nutrient_badge(self, label, value, unit, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=10, color=ft.Colors.GREY_600),
                ft.Text(f"{value}{unit}", size=12, weight=ft.FontWeight.BOLD, color=color)
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=5,
            bgcolor=ft.Colors.with_opacity(0.1, color),
            border_radius=5,
        )

    def update_meals_ui(self):
        self.meals_list.controls.clear()
        for meal in reversed(self.meals):
            l1 = meal.get('level1', {})
            
            delete_button = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color=ft.Colors.GREY_400,
                tooltip=i18n_manager.t("food_delete"),
                on_click=lambda _, m=meal: self._delete_meal(m),
                icon_size=18
            )

            macro_row = ft.Row([
                self._build_nutrient_badge(i18n_manager.t("nutrient_calories"), l1.get('calories', 0), "kcal", ft.Colors.RED),
                self._build_nutrient_badge(i18n_manager.t("nutrient_protein"), l1.get('protein', 0), "g", ft.Colors.BLUE),
                self._build_nutrient_badge(i18n_manager.t("nutrient_fat"), l1.get('total_fat', 0), "g", ft.Colors.ORANGE),
                self._build_nutrient_badge(i18n_manager.t("nutrient_carbs"), l1.get('total_carbs', 0), "g", ft.Colors.GREEN),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            
            details_map = [
                (i18n_manager.t("nutrient_fiber"), "fiber", "g"), (i18n_manager.t("nutrient_sugar"), "sugars", "g"), (i18n_manager.t("nutrient_sodium"), "sodium", "mg"),
                (i18n_manager.t("nutrient_calcium"), "calcium", "mg"), (i18n_manager.t("nutrient_vitamin_c"), "vitamin_c", "mg"), (i18n_manager.t("nutrient_vitamin_d"), "vitamin_d", "µg")
            ]
            detail_controls = []
            for label, key, unit in details_map:
                val = l1.get(key, 0)
                if val > 0:
                    detail_controls.append(
                        ft.Container(
                            content=ft.Text(f"{label}: {val}{unit}", size=11, color=ft.Colors.GREY_700),
                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            bgcolor=ft.Colors.GREY_100,
                            border_radius=4
                        )
                    )
            details_row = ft.Row(detail_controls, wrap=True, spacing=5, run_spacing=5)
            
            serving_eaten = meal.get('serving_eaten', {})
            serving_text = f"{i18n_manager.t('food_serving')} {serving_eaten.get('value', '')} {serving_eaten.get('unit', '')}"

            item = ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Text(meal["name"], size=16, weight=ft.FontWeight.BOLD, expand=True),
                            delete_button
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Row(
                        [
                            ft.Text(serving_text, size=12, color=ft.Colors.BLACK)
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Divider(height=5, color="transparent"),
                    macro_row,
                    ft.Divider(height=5, color="transparent"),
                    details_row
                ]),
                padding=15,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, ft.Colors.GREY_200),
                border_radius=8,
                shadow=ft.BoxShadow(
                    spread_radius=1, blur_radius=3,
                    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK), offset=ft.Offset(0, 2),
                )
            )
            self.meals_list.controls.append(item)
        if self.page: self.update()
