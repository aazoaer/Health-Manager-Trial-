
import flet as ft
import datetime
import asyncio
from ui.styles import CARD_STYLE
from core import event_bus
from ui.Mobile.utils.time_utils import get_timezone_str, get_current_time_str
from data.storage import load_user_data, save_user_data
from core.i18n import i18n_manager, I18nText

def get_half_hour_period_id(dt: datetime.datetime) -> int:
    return dt.hour * 2 + (1 if dt.minute >= 30 else 0)

def get_day_period_key(dt: datetime.datetime) -> tuple:
    return (dt.date().isoformat(), get_half_hour_period_id(dt))

def should_trigger_reminder(last_drink_time: datetime.datetime = None) -> bool:
    now = datetime.datetime.now()
    if last_drink_time is None:
        return True
    current_key = get_day_period_key(now)
    last_drink_key = get_day_period_key(last_drink_time)
    return current_key != last_drink_key

def is_reminder_time(dt: datetime.datetime) -> bool:
    return dt.minute in [0, 30]

class ReminderCard(ft.Container):
    
    _last_notified_period = None
    
    def __init__(self):
        mobile_style = {**CARD_STYLE, "padding": 12}
        super().__init__(**mobile_style)
        
        self.running = True
        self.timezone_str = get_timezone_str()
        self.last_checked_period = None
        
        self.is_warning = self._check_reminder_needed()
        self._init_components()
        self.content = self._build_content()
        event_bus.subscribe(event_bus.WATER_ADDED, self._on_water_added)

    def did_mount(self):
        self.running = True
        self.is_warning = self._check_reminder_needed()
        self.warning_container.visible = self.is_warning
        
        if self.is_warning:
            save_user_data({"reminder_active": True})
            current_period = get_half_hour_period_id(datetime.datetime.now())
            if ReminderCard._last_notified_period != current_period:
                ReminderCard._last_notified_period = current_period
                self._show_system_notification()
        else:
            save_user_data({"reminder_active": False})
        
        if self.page:
            self.warning_container.update()
        
        asyncio.create_task(self.update_clock())

    def will_unmount(self):
        self.running = False
        event_bus.unsubscribe(event_bus.WATER_ADDED, self._on_water_added)

    def _check_reminder_needed(self) -> bool:
        user_data = load_user_data()
        last_drink_str = user_data.get("last_drink_timestamp")
        if not last_drink_str:
            return True
        try:
            last_drink_time = datetime.datetime.fromisoformat(last_drink_str)
            return should_trigger_reminder(last_drink_time)
        except (ValueError, TypeError):
            return True

    def _init_components(self):
        self.countdown_text = ft.Text(
            value="--:--", 
            size=36,
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLUE_600
        )
        self.time_text = ft.Text(
            f"{self.timezone_str} {i18n_manager.t('reminder_current_time')} 00:00:00", 
            size=11, 
            color=ft.Colors.GREY_500
        )
        self.warning_text = I18nText(
            key="reminder_warning", 
            color=ft.Colors.WHITE, 
            size=14, 
            weight=ft.FontWeight.BOLD
        )
        self.warning_container = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.WHITE, size=24),
                self.warning_text
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.Colors.RED_500, 
            padding=8, 
            border_radius=8,
            visible=self.is_warning
        )

    def _build_content(self):
        return ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.ACCESS_ALARM, color=ft.Colors.ORANGE_500, size=20),
                I18nText(key="reminder_title", size=16, weight=ft.FontWeight.W_600)
            ], spacing=6),
            
            ft.Divider(height=8, color="transparent"),
            
            ft.Container(
                content=ft.Column([
                    self.countdown_text, 
                    self.time_text
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                alignment=ft.Alignment(0, 0)
            ),
            
            ft.Divider(height=12, color="transparent"),
            
            ft.Container(
                content=self.warning_container,
                height=40
            )
        ], spacing=4)

    async def update_clock(self):
        while self.running:
            try:
                now = datetime.datetime.now()
                current_period = get_half_hour_period_id(now)
                
                target_minute = 30 if now.minute < 30 else 0
                target_hour = now.hour if now.minute < 30 else (now.hour + 1) % 24
                target_time = now.replace(
                    hour=target_hour, minute=target_minute, 
                    second=0, microsecond=0
                )
                if target_hour < now.hour:
                    target_time += datetime.timedelta(days=1)
                
                minutes, seconds = divmod(int((target_time - now).total_seconds()), 60)
                
                if self.last_checked_period != current_period:
                    self.last_checked_period = current_period
                    if not self.is_warning:
                        need_reminder = self._check_reminder_needed()
                        if need_reminder:
                            self.is_warning = True
                            self.warning_container.visible = True
                            save_user_data({"reminder_active": True})
                            if self.page:
                                self.warning_container.update()
                                self._show_system_notification()
                
                if self.page:
                    self.countdown_text.value = f"{minutes:02d}:{seconds:02d}"
                    self.time_text.value = f"{self.timezone_str} {i18n_manager.t('reminder_current_time')} {get_current_time_str()}"
                    self.countdown_text.update()
                    self.time_text.update()

            except Exception:
                pass
            await asyncio.sleep(1)

    def _on_water_added(self, *args, **kwargs):
        self.is_warning = False
        self.warning_container.visible = False
        try:
            if self.page:
                self.warning_container.update()
        except Exception:
            pass

    def _show_system_notification(self):
        try:
            from core.notification import send_notification
            send_notification()
        except Exception:
            pass
        try:
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(i18n_manager.t("reminder_warning"), color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.RED_500,
                    duration=5000
                )
                self.page.snack_bar.open = True
                self.page.update()
        except Exception:
            pass
