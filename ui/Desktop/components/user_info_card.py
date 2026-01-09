import flet as ft
from ui.styles import AppColors, CARD_STYLE
from data.storage import load_user_data, save_user_data
from core.i18n import I18nText, i18n_manager

class UserInfoCard(ft.Container):

    AGE_RANGE = (3, 100)
    HEIGHT_RANGE = (50, 230)
    WEIGHT_RANGE = (10, 200)

    def __init__(self):
        style = CARD_STYLE.copy()
        style["width"] = 420
        style["height"] = 700
        style["padding"] = 20
        super().__init__(**style)
        
        self._init_components()
        self.content = self._build_content()
        self._load_data()

        i18n_manager.subscribe(self.update_ui)

    def will_unmount(self):
        i18n_manager.unsubscribe(self.update_ui)

    def update_ui(self):
        if not self.page:
            return

        self.age_input.label = i18n_manager.t("age_label")
        self.height_input.label = f"{i18n_manager.t('height_label')} (cm)"
        self.weight_input.label = f"{i18n_manager.t('weight_label')} (kg)"
        self.gender_dropdown.label = i18n_manager.t("gender_label")
        self.exercise_dropdown.label = i18n_manager.t("exercise_intensity_label")
        self.environment_dropdown.label = i18n_manager.t("environment_label")

        self.age_input.hint_text = f"{self.AGE_RANGE[0]}-{self.AGE_RANGE[1]}"
        self.height_input.hint_text = f"{self.HEIGHT_RANGE[0]}-{self.HEIGHT_RANGE[1]}"
        self.weight_input.hint_text = f"{self.WEIGHT_RANGE[0]}-{self.WEIGHT_RANGE[1]}"
        self.gender_dropdown.hint_text = i18n_manager.t("hint_pleaseselect")
        self.exercise_dropdown.hint_text = i18n_manager.t("hint_pleaseselect")
        self.environment_dropdown.hint_text = i18n_manager.t("hint_pleaseselect")

        self.gender_dropdown.options[0].text = i18n_manager.t("gender_male")
        self.gender_dropdown.options[1].text = i18n_manager.t("gender_female")

        for i, key in enumerate(["exercise_none", "exercise_low", "exercise_medium", "exercise_high", "exercise_pro"]):
            self.exercise_dropdown.options[i].text = i18n_manager.t(key)

        for i, key in enumerate(["env_ac", "env_cold", "env_hot"]):
            self.environment_dropdown.options[i].text = i18n_manager.t(key)

        if hasattr(self, 'message_key') and self.message_key:
            self.message_text.value = i18n_manager.t(self.message_key)

        self.page.update()

    def _init_components(self):
        input_width = 380
        input_height = 50

        self.age_input = ft.TextField(
            label=i18n_manager.t("age_label"),
            hint_text=f"{self.AGE_RANGE[0]}-{self.AGE_RANGE[1]}",
            width=input_width, height=input_height,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8,
            on_change=self._validate_age
        )
        
        self.height_input = ft.TextField(
            label=f"{i18n_manager.t('height_label')} (cm)",
            hint_text=f"{self.HEIGHT_RANGE[0]}-{self.HEIGHT_RANGE[1]}",
            width=input_width, height=input_height,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8,
            on_change=self._validate_height
        )
        
        self.weight_input = ft.TextField(
            label=f"{i18n_manager.t('weight_label')} (kg)",
            hint_text=f"{self.WEIGHT_RANGE[0]}-{self.WEIGHT_RANGE[1]}",
            width=input_width, height=input_height,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8,
            on_change=self._validate_weight
        )

        dropdown_width = 380
        self.gender_dropdown = ft.Dropdown(
            label=i18n_manager.t("gender_label"),
            hint_text=i18n_manager.t("hint_pleaseselect"),
            options=[
                ft.dropdown.Option("male", text=i18n_manager.t("gender_male")),
                ft.dropdown.Option("female", text=i18n_manager.t("gender_female")),
            ],
            height=45, content_padding=10, text_size=14, border_radius=8, width=dropdown_width
        )

        self.exercise_dropdown = ft.Dropdown(
            label=i18n_manager.t("exercise_intensity_label"),
            hint_text=i18n_manager.t("hint_pleaseselect"),
            options=[
                ft.dropdown.Option("sedentary", text=i18n_manager.t("exercise_none")),
                ft.dropdown.Option("light_active", text=i18n_manager.t("exercise_low")),
                ft.dropdown.Option("moderately_active", text=i18n_manager.t("exercise_medium")),
                ft.dropdown.Option("very_active", text=i18n_manager.t("exercise_high")),
                ft.dropdown.Option("extra_active", text=i18n_manager.t("exercise_pro")),
            ],
            height=45, content_padding=10, text_size=14, border_radius=8, width=dropdown_width
        )

        self.environment_dropdown = ft.Dropdown(
            label=i18n_manager.t("environment_label"),
            hint_text=i18n_manager.t("hint_pleaseselect"),
            options=[
                ft.dropdown.Option("ac_env", text=i18n_manager.t("env_ac")),
                ft.dropdown.Option("cold_env", text=i18n_manager.t("env_cold")),
                ft.dropdown.Option("hot_env", text=i18n_manager.t("env_hot")),
            ],
            height=45, content_padding=10, text_size=14, border_radius=8, width=dropdown_width
        )

        self.save_btn = ft.ElevatedButton(
            content=ft.Container(
                content=I18nText(key="save_button", size=14),
                padding=ft.padding.symmetric(horizontal=20, vertical=5)
            ),
            on_click=self._save_data,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: ft.Colors.GREEN_600, ft.ControlState.HOVERED: ft.Colors.GREEN_500},
                color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )
        self.message_text = ft.Text(size=12)
        self.message_key = ""

    def _validate_number(self, value, min_val, max_val):
        
        if not value:
            return True, None
        try:
            num = int(value)
            if num < min_val or num > max_val:

                return False, i18n_manager.t("error_range").format(min=min_val, max=max_val) if i18n_manager.t("error_range") != "error_range" else f"Range: {min_val}-{max_val}"
            return True, None
        except ValueError:

            return False, i18n_manager.t("error_invalid_number") if i18n_manager.t("error_invalid_number") != "error_invalid_number" else "Please enter a valid number"

    def _validate_age(self, e):
        valid, error = self._validate_number(e.control.value, *self.AGE_RANGE)
        e.control.error_text = error
        e.control.update()

    def _validate_height(self, e):
        valid, error = self._validate_number(e.control.value, *self.HEIGHT_RANGE)
        e.control.error_text = error
        e.control.update()

    def _validate_weight(self, e):
        valid, error = self._validate_number(e.control.value, *self.WEIGHT_RANGE)
        e.control.error_text = error
        e.control.update()

    def _build_content(self):
        return ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.PERSON, color=ft.Colors.PURPLE_500),
                I18nText(key="user_info_title", size=18, weight=ft.FontWeight.W_600)
            ]),
            ft.Divider(height=10, color="transparent"),
            
            ft.Column([
                self.age_input,
                self.gender_dropdown, 
                self.height_input,
                self.weight_input, 
                self.exercise_dropdown, 
                self.environment_dropdown,
            ], spacing=35),
            
            ft.Divider(height=15, color="transparent"),
            ft.Row([self.message_text, self.save_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ], spacing=0, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def _load_data(self):
        data = load_user_data()
        if data:
            self.age_input.value = str(data.get("age", ""))
            self.gender_dropdown.value = data.get("gender", "")
            self.height_input.value = str(data.get("height", ""))
            self.weight_input.value = str(data.get("weight", ""))
            
            self.exercise_dropdown.value = data.get("exercise_intensity")
            self.environment_dropdown.value = data.get("environment")

    def _set_message(self, key, color):
        self.message_key = key
        self.message_text.value = i18n_manager.t(key)
        self.message_text.color = color
        self.update()

    def _save_data(self, e):
        age_valid, age_err = self._validate_number(self.age_input.value, *self.AGE_RANGE)
        height_valid, height_err = self._validate_number(self.height_input.value, *self.HEIGHT_RANGE)
        weight_valid, weight_err = self._validate_number(self.weight_input.value, *self.WEIGHT_RANGE)

        self.age_input.error_text = age_err
        self.height_input.error_text = height_err
        self.weight_input.error_text = weight_err

        if not all([age_valid, height_valid, weight_valid]):
            self._set_message("error_invalid_number", ft.Colors.RED_500)
            return

        if not all([self.age_input.value, self.gender_dropdown.value, self.height_input.value, 
                    self.weight_input.value, self.exercise_dropdown.value, self.environment_dropdown.value]):
            self._set_message("fill_all_message", ft.Colors.RED_500)
            return

        data = {
            "age": self.age_input.value, "gender": self.gender_dropdown.value,
            "height": self.height_input.value, "weight": self.weight_input.value,
            "exercise_intensity": self.exercise_dropdown.value, "environment": self.environment_dropdown.value
        }
        
        if save_user_data(data):
            self._set_message("save_success_message", ft.Colors.GREEN_600)
        else:
            self._set_message("save_fail_message", ft.Colors.RED_500)
