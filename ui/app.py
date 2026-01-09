import flet as ft
import asyncio
from datetime import datetime
import sys
import os
from ui.styles import AppColors, is_mobile
from ui.Desktop.components.navigation import AppNavigationRail
from ui.Mobile.components.navigation import MobileNavigationBar

from ui.Desktop.components.water_card import WaterCard as DesktopWaterCard
from ui.Mobile.components.water_card import WaterCard as MobileWaterCard
from ui.Desktop.components.food_card import FoodCard
from ui.Desktop.components.nutrition_goals_card import NutritionGoalsCard

from ui.Desktop.views.home_view import HomeView
from ui.Desktop.views.water_view import WaterView as DesktopWaterView
from ui.Mobile.views.water_view import WaterView as MobileWaterView
from ui.Desktop.views.food_view import FoodView
from ui.Desktop.views.sleep_view import SleepView
from ui.Desktop.views.exercise_view import ExerciseView
from ui.Desktop.views.calendar_view import CalendarView as DesktopCalendarView
from ui.Mobile.views.calendar_view import CalendarView as MobileCalendarView
from ui.Desktop.views.setting_view import SettingView as DesktopSettingView
from ui.Mobile.views.setting_view import SettingView as MobileSettingView

from ui.Desktop.components.reminder_card import is_reminder_time, should_trigger_reminder
from core.i18n import i18n_manager
from core.system_tray import SystemTray
from core.notification import send_notification, flash_window
from data.database import init_db

class HealthApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.is_running = True
        self.loop = asyncio.get_running_loop()
        self.last_reminder_minute = None
        self.system_tray = None
        

        self.is_mobile_layout = True
        self.main_layout = None 
        
        init_db()
        self._setup_page()
        self._init_shared_components()
        self._init_views()
        self._setup_window_controls()
        self._setup_close_handler()
        self._build_ui()
        self._setup_system_tray()
        self.page.update()
        

        
        self.reminder_task = asyncio.create_task(self._reminder_check_loop())

    def _setup_page(self):
        self.page.title = i18n_manager.t("app_title")
        self.page.bgcolor = AppColors.BACKGROUND
        self.page.padding = 0
        self.page.fonts = {
            "Microsoft YaHei": "Microsoft YaHei"
        }
        self.page.theme = ft.Theme(font_family="Microsoft YaHei")
        
        from data.storage import load_user_data
        user_data = load_user_data()
        theme_mode = user_data.get("theme_mode", "system")
        if theme_mode == "light":
            self.page.theme_mode = ft.ThemeMode.LIGHT
        elif theme_mode == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.SYSTEM
        
        if not self.page.web:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(project_root, 'assests', 'resource', 'icon', 'Health_App.ico')
            if os.path.exists(icon_path):
                self.page.window.icon = icon_path

    def _init_shared_components(self):
        if self.is_mobile_layout:
            self.water_card = MobileWaterCard()

        else:
            self.water_card = DesktopWaterCard()
            self.nutrition_goals_card = NutritionGoalsCard(food_card_ref=None)
            self.food_card = FoodCard(nutrition_goals_card_ref=self.nutrition_goals_card)
            self.nutrition_goals_card.food_card_ref = self.food_card

    def _init_views(self):
        if self.is_mobile_layout:

            self.views = {
                1: MobileWaterView(water_card=self.water_card),
                5: MobileCalendarView(),
                6: MobileSettingView()
            }
            self.current_view_index = 1
        else:
            self.views = {
                0: HomeView(),
                1: DesktopWaterView(water_card=self.water_card),
                2: FoodView(nutrition_goals_card=self.nutrition_goals_card, food_card=self.food_card),
                3: SleepView(),
                4: ExerciseView(),
                5: DesktopCalendarView(),
                6: DesktopSettingView()
            }
            self.current_view_index = 0

    def _setup_window_controls(self):
        if not self.page.web:
            self.page.window.prevent_close = True
            self.page.window.on_event = self._on_window_event

    def _setup_close_handler(self):
        exit_title = ft.Text(
            i18n_manager.t("exit_dialog_title"),
            size=20,
            weight=ft.FontWeight.W_600,
            text_align=ft.TextAlign.CENTER
        )
        exit_content = ft.Text(
            i18n_manager.t("exit_dialog_content"),
            size=15
        )
        
        self.remember_checkbox = ft.Checkbox(
            label=i18n_manager.t("remember_choice"),
            value=False
        )
        
        dialog_content = ft.Column([
            exit_content,
            ft.Container(height=10),
            self.remember_checkbox
        ], tight=True)
        
        self.exit_dialog = ft.AlertDialog(
            modal=True,
            title=exit_title,
            content=dialog_content,
            shape=ft.RoundedRectangleBorder(radius=20),
            actions=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.MINIMIZE, color=ft.Colors.WHITE, size=20),
                            ft.Text(i18n_manager.t("exit_background"), color=ft.Colors.WHITE, weight=ft.FontWeight.W_500)
                        ],
                        tight=True,
                        spacing=8
                    ),
                    bgcolor=ft.Colors.BLUE_600,
                    padding=ft.padding.symmetric(vertical=12, horizontal=24),
                    border_radius=12,
                    on_click=self._minimize_to_tray,
                    shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLUE_200, spread_radius=1)
                ),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.EXIT_TO_APP, color=ft.Colors.WHITE, size=20),
                            ft.Text(i18n_manager.t("exit_quit"), color=ft.Colors.WHITE, weight=ft.FontWeight.W_500)
                        ],
                        tight=True,
                        spacing=8
                    ),
                    bgcolor=ft.Colors.RED_600,
                    padding=ft.padding.symmetric(vertical=12, horizontal=24),
                    border_radius=12,
                    on_click=self._quit_app,
                    shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.RED_200, spread_radius=1)
                ),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.CANCEL, color=ft.Colors.WHITE, size=20),
                            ft.Text(i18n_manager.t("cancel_button"), color=ft.Colors.WHITE, weight=ft.FontWeight.W_500)
                        ],
                        tight=True,
                        spacing=8
                    ),
                    bgcolor=ft.Colors.GREY_600,
                    padding=ft.padding.symmetric(vertical=12, horizontal=24),
                    border_radius=12,
                    on_click=self._close_exit_dialog,
                    shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.GREY_300, spread_radius=1)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            content_padding=30,
        )

    def _on_window_event(self, e):
        event_type_str = str(e.type)
        if "CLOSE" in event_type_str.upper():
            from data.storage import load_user_data
            user_data = load_user_data()
            close_mode = user_data.get("close_mode", "ask")
            
            if close_mode == "minimize":
                self._minimize_to_tray()
            elif close_mode == "quit":
                self._quit_app()
            else:
                self._show_exit_dialog()

    def _show_exit_dialog(self):
        if self.exit_dialog not in self.page.overlay:
            self.page.overlay.append(self.exit_dialog)
        self.exit_dialog.open = True
        self.page.update()

    def _close_exit_dialog(self, e=None):
        self.exit_dialog.open = False
        self.page.update()

    def _minimize_to_tray(self, e=None):

        if hasattr(self, 'remember_checkbox') and self.remember_checkbox.value:
            from data.storage import save_user_data
            save_user_data({"close_mode": "minimize"})
        
        self.exit_dialog.open = False
        self.page.update()
        
        if not self.page.web:
            self.page.window.visible = False
            self.page.window.skip_task_bar = True
            self.page.update()

    def _quit_app(self, e=None):
        try:
            if hasattr(self, 'remember_checkbox') and self.remember_checkbox.value:
                from data.storage import save_user_data
                save_user_data({"close_mode": "quit"})
                
            if self.page:
                self.page.window.prevent_close = False
                self.page.window.close()
        except:
            pass
            
        sys.exit(0)

    def _show_window_from_tray(self):
        if not self.page.window.visible:
            self.page.window.visible = True
            self.page.window.skip_task_bar = False
            self.page.update()
            
    def _navigate_from_tray(self, index):
        self._show_window_from_tray()
        self.loop.call_soon_threadsafe(self._on_nav_change, index)
            
    def _quit_from_tray(self):
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self._quit_app)
        else:
            os._exit(0)

    def _setup_system_tray(self):
        if self.page.web:
            return
        
        self.system_tray = SystemTray(
            page=self.page,
            on_show_window=self._show_window_from_tray,
            on_quit=self._quit_from_tray,
            on_navigate=self._navigate_from_tray
        )
        self.system_tray.start()

    async def _reminder_check_loop(self):
        while self.is_running:
            try:
                now = datetime.now()
                current_minute = now.minute
                
                if is_reminder_time(now) and current_minute != self.last_reminder_minute:
                    self.last_reminder_minute = current_minute
                    
                    from data.storage import load_user_data
                    user_data = load_user_data()
                    last_drink_str = user_data.get("last_drink_timestamp")
                    last_drink = None
                    if last_drink_str:
                        try:
                            last_drink = datetime.fromisoformat(last_drink_str)
                        except (ValueError, TypeError):
                            pass
                            
                    if should_trigger_reminder(last_drink):
                        self._send_notification()
                
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                await asyncio.sleep(1)

    def _send_notification(self):
        try:
            send_notification()
            
            if not self.page.web and self.page.window.visible:
                flash_window(self.page.title)
        except Exception:
            pass

    def _build_ui(self):

        if self.current_view_index not in self.views:
             self.current_view_index = 1 if self.is_mobile_layout else 0
        
        self.content_area = ft.Container(
            content=self.views[self.current_view_index],
            expand=True,
            bgcolor=AppColors.BACKGROUND
        )

        self.navigation_rail = None
        self.mobile_nav_bar = None
        
        if self.is_mobile_layout:
            self.mobile_nav_bar = MobileNavigationBar(on_destination_selected=self._on_nav_change)
            self.mobile_nav_bar.set_selection(self.current_view_index)
        else:
            self.navigation_rail = AppNavigationRail(on_destination_selected=self._on_nav_change)
            self.navigation_rail.set_selection(self.current_view_index)

        self._build_layout()

    def _build_layout(self):
        
        self.page.controls.clear()
        
        if self.is_mobile_layout:

            self.main_layout = ft.Column(
                controls=[
                    self.content_area,
                    self.mobile_nav_bar
                ],
                expand=True,
                spacing=0
            )
        else:

            self.main_layout = ft.Row(
                controls=[
                    self.navigation_rail,
                    self.content_area
                ],
                expand=True
            )
        
        self.page.add(self.main_layout)

    def _on_nav_change(self, index: int):
        
        if index == self.current_view_index:
            return
        
        self.current_view_index = index

        if self.is_mobile_layout:
            if hasattr(self, 'mobile_nav_bar') and self.mobile_nav_bar:
                self.mobile_nav_bar.set_selection(index)
        else:
            if hasattr(self, 'navigation_rail') and self.navigation_rail:
                self.navigation_rail.set_selection(index)

        loading_indicator = ft.Container(
            content=ft.Column(
                [
                    ft.ProgressRing(width=40, height=40, stroke_width=3),
                    ft.Text(i18n_manager.t("loading"), size=14, color=ft.Colors.GREY_500)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            expand=True,
            alignment=ft.Alignment(0, 0)
        )
        self.content_area.content = loading_indicator
        self.page.update()
        

        async def load_view():
            await asyncio.sleep(0.01)
            if index in self.views:
                self.content_area.content = self.views[index]
                self.page.update()
        
        asyncio.create_task(load_view())
