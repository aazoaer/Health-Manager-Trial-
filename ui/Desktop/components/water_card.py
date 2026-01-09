import flet as ft
import datetime
from ui.styles import AppColors, CARD_STYLE
from core import event_bus
from data.storage import load_user_data, save_user_data
from core.calculations import calculate_water_goal
from ui.Desktop.utils.confirmation import create_confirmation_dialog
from core.i18n import i18n_manager, I18nText

class WaterCard(ft.Container):
    def __init__(self):
        super().__init__(**CARD_STYLE)
        self.water_intake = 0
        self.water_goal = 2000
        self.water_records = []
        self._amount_to_change = 0
        self._action_to_confirm = None

        self._initialize_data()
        self._init_components()
        self.content = self._build_content()
        self.update_ui(initial_load=True)
        event_bus.subscribe(event_bus.USER_DATA_SAVED, self._on_user_data_saved)

    def did_mount(self):

        self._initialize_data()
        self.update_ui()
        self._update_records_ui()

        if self.page and self.confirmation_dialog not in self.page.overlay:
            self.page.overlay.append(self.confirmation_dialog)
            self.page.update()

    def will_unmount(self):
        if self.page and self.confirmation_dialog in self.page.overlay:
            self.page.overlay.remove(self.confirmation_dialog)
        event_bus.unsubscribe(event_bus.USER_DATA_SAVED, self._on_user_data_saved)

    def _init_components(self):
        initial_progress = min(self.water_intake / self.water_goal, 1.0) if self.water_goal > 0 else 0
        self.water_progress = ft.ProgressBar(color=AppColors.WATER_PROGRESS, bgcolor=AppColors.WATER_BG, value=initial_progress)
        self.water_text = ft.Text(f"{self.water_intake} / {self.water_goal} ml", size=20, weight=ft.FontWeight.BOLD, color=AppColors.WATER_TEXT)
        self.cup_selector = ft.Dropdown(
            label=i18n_manager.t("water_select_label"), hint_text=i18n_manager.t("hint_pleaseselect"),
            options=[
                ft.dropdown.Option(key="100", text=i18n_manager.t("water_cup_small")),
                ft.dropdown.Option(key="150", text=i18n_manager.t("water_cup_half")),
                ft.dropdown.Option(key="200", text=i18n_manager.t("water_cup_single")),
                ft.dropdown.Option(key="250", text=i18n_manager.t("water_cup_large")),
                ft.dropdown.Option(key="300", text=i18n_manager.t("water_cup_mug"))
            ],
            width=330, height=45, content_padding=10, text_size=13,
            border_radius=8, bgcolor=ft.Colors.GREY_50,
        )
        self.congrats_text = ft.Container(
            content=I18nText(key="water_congrats", size=12, color=ft.Colors.GREEN_700, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            padding=ft.padding.only(top=10), visible=False, alignment=ft.Alignment(0, 0)
        )
        

        self.timestamp_text = ft.Text("", size=11, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER)
        

        self.records_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=200)

        self.confirmation_dialog = create_confirmation_dialog(
            "", self._on_confirm_action, self._close_dialog
        )

    def _build_content(self):
        self.title_text = I18nText(key="water_title", size=18, weight=ft.FontWeight.W_600)
        self.reset_button = ft.IconButton(icon=ft.Icons.REFRESH, icon_color=ft.Colors.GREY_400, on_click=self._handle_reset_click, tooltip=i18n_manager.t("water_reset"))
        self.subtract_button = ft.IconButton(icon=ft.Icons.REMOVE_CIRCLE, icon_color=ft.Colors.RED_300, icon_size=36, on_click=self._handle_subtract_click, tooltip=i18n_manager.t("water_subtract"))
        self.add_button = ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=ft.Colors.BLUE_500, icon_size=36, on_click=self._handle_add_click, tooltip=i18n_manager.t("water_add"))
        
        return ft.Column([
            ft.Row([
                ft.Row([ft.Icon(ft.Icons.WATER_DROP, color=ft.Colors.BLUE_500), self.title_text]),
                self.reset_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=20, color="transparent"),
            ft.Container(content=self.water_text, alignment=ft.Alignment(0, 0)),
            self.water_progress, self.congrats_text,
            ft.Divider(height=20, color="transparent"),
            ft.Row([
                self.subtract_button,
                ft.Container(width=10), self.cup_selector, ft.Container(width=10),
                self.add_button,
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(
                content=self.timestamp_text,
                alignment=ft.Alignment(0, 0),
                padding=ft.padding.only(top=5)
            ),
            ft.Divider(height=10),
            I18nText(key="water_today_records", size=14, color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            self.records_list
        ], spacing=5)

    def _initialize_data(self):
        user_data = load_user_data()
        if not user_data:
            self.water_goal = 2000
            self.water_intake = 0
            self.water_records = []
            return

        self.water_goal = calculate_water_goal(user_data)
        

        last_drink_str = user_data.get("last_drink_timestamp")
        today = datetime.date.today()
        
        should_reset = False
        if last_drink_str:
            try:
                last_drink_date = datetime.datetime.fromisoformat(last_drink_str).date()
                if last_drink_date != today:
                    should_reset = True
            except (ValueError, TypeError):
                should_reset = True
        else:

            should_reset = user_data.get("water_intake", 0) > 0
        
        if should_reset:
            self.water_intake = 0
            self.water_records = []
            self._save_data()
        else:
            self.water_intake = int(user_data.get("water_intake", 0))

            records_data = user_data.get("water_records", [])
            if isinstance(records_data, dict):
                self.water_records = records_data.get("records", [])
            else:
                self.water_records = records_data
            

            if not self.water_records and self.water_intake > 0 and last_drink_str:
                self.water_records = [{
                    "timestamp": last_drink_str,
                    "amount": self.water_intake
                }]

    def _on_user_data_saved(self, *args, **kwargs):

        user_data = load_user_data()
        self.water_goal = calculate_water_goal(user_data)
        self.update_ui()

    def _open_dialog(self, title: str, action):
        self.confirmation_dialog.title.value = title
        self._action_to_confirm = action
        self.confirmation_dialog.open = True
        if self.page:
            self.page.update()

    def _close_dialog(self, e=None):
        self.confirmation_dialog.open = False
        if self.page:
            self.page.update()

    def _on_confirm_action(self, e):
        if self._action_to_confirm:
            self._action_to_confirm()
        self._close_dialog()

    def _handle_add_click(self, e):
        if not self.cup_selector.value:
            self.cup_selector.error_text = i18n_manager.t("hint_pleaseselect"); self.cup_selector.update(); return
        self._amount_to_change = int(self.cup_selector.value)
        self._open_dialog(i18n_manager.t("water_confirm_drink"), self._execute_add)

    def _handle_subtract_click(self, e):
        if not self.cup_selector.value:
            self.cup_selector.error_text = i18n_manager.t("hint_pleaseselect"); self.cup_selector.update(); return
        self._amount_to_change = int(self.cup_selector.value)
        self._open_dialog(i18n_manager.t("water_confirm_subtract"), self._execute_subtract)

    def _handle_reset_click(self, e):
        self._open_dialog(i18n_manager.t("water_confirm_reset"), self._execute_reset)

    def _execute_add(self):
        self.water_intake += self._amount_to_change
        timestamp = datetime.datetime.now().isoformat()
        self.water_records.append({
            "timestamp": timestamp,
            "amount": self._amount_to_change
        })
        self.cup_selector.error_text = None
        self.cup_selector.update()
        self._save_data()
        self._update_timestamp()
        self.update_ui()
        self._update_records_ui()
        event_bus.publish(event_bus.WATER_ADDED)

    def _execute_subtract(self):

        if self.water_records:
            last_record = self.water_records[-1]
            if last_record["amount"] > self._amount_to_change:
                last_record["amount"] -= self._amount_to_change
            else:
                self.water_records.pop()
        
        self.water_intake = max(0, self.water_intake - self._amount_to_change)
        self.cup_selector.error_text = None
        self.cup_selector.update()
        self._save_data()
        self.update_ui()
        self._update_records_ui()

    def _execute_reset(self):
        self.water_intake = 0
        self.water_records = []
        self._save_data()
        self.update_ui()
        self._update_records_ui()

    def _save_data(self):
        save_user_data({
            "water_intake": self.water_intake,
            "water_records": {
                "date": datetime.date.today().isoformat(),
                "records": self.water_records
            },
            "reminder_active": False,
            "last_drink_timestamp": datetime.datetime.now().isoformat() if self.water_records else None
        })

    def _update_timestamp(self):
        
        now = datetime.datetime.now()
        self.timestamp_text.value = f"{i18n_manager.t('water_last_record')}: {now.strftime('%H:%M:%S')}"
        if self.page:
            self.timestamp_text.update()
    
    def _update_records_ui(self):
        
        self.records_list.controls.clear()
        
        if not self.water_records:
            self.records_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        i18n_manager.t("water_no_records"),
                        size=12,
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=10
                )
            )
        else:
            for record in reversed(self.water_records[-10:]):
                try:
                    timestamp = datetime.datetime.fromisoformat(record["timestamp"])
                    time_str = timestamp.strftime("%H:%M")
                    amount = record["amount"]
                    
                    record_item = ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.WATER_DROP, color=ft.Colors.BLUE_400, size=16),
                            ft.Text(time_str, size=13, weight=ft.FontWeight.W_500),
                            ft.Container(expand=True),
                            ft.Text(f"{amount} ml", size=13, color=ft.Colors.BLUE_600, weight=ft.FontWeight.BOLD)
                        ]),
                        bgcolor=ft.Colors.BLUE_50,
                        padding=8,
                        border_radius=8
                    )
                    self.records_list.controls.append(record_item)
                except (ValueError, KeyError):
                    continue
        
        if self.page:
            self.records_list.update()

    def update_ui(self, initial_load=False):
        progress = min(self.water_intake / self.water_goal, 1.0) if self.water_goal > 0 else 0
        self.water_progress.value = progress
        self.water_text.value = f"{self.water_intake} / {self.water_goal} ml"
        self.congrats_text.visible = progress >= 1.0
        
        if progress >= 1.0:
            self.water_progress.color, self.water_text.color = AppColors.WATER_COMPLETE, ft.Colors.GREEN_700
        else:
            self.water_progress.color, self.water_text.color = AppColors.WATER_PROGRESS, AppColors.WATER_TEXT

        if not initial_load and hasattr(self, '_page') and self._page is not None:
            self.update()
