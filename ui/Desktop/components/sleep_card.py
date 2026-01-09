import flet as ft
import datetime
import uuid
from ui.styles import AppColors, CARD_STYLE
from core import event_bus
from data.storage import load_user_data, save_user_data
from ui.Desktop.utils.confirmation import create_confirmation_dialog
from core.i18n import i18n_manager, I18nText

class SleepCard(ft.Container):
    def __init__(self):
        super().__init__(**CARD_STYLE)
        self.records = []
        self._record_to_delete = None
        self.error_message = None
        
        self._initialize_data()
        self._init_components()
        self.content = self._build_content()
        self._update_records_ui()

    def did_mount(self):
        if self.page and self.confirmation_dialog not in self.page.overlay:
            self.page.overlay.append(self.confirmation_dialog)
            self.page.update()

    def will_unmount(self):
        if self.page and self.confirmation_dialog in self.page.overlay:
            self.page.overlay.remove(self.confirmation_dialog)

    def _initialize_data(self):
        
        user_data = load_user_data()
        daily_sleep = user_data.get("daily_sleep", {})
        
        today = datetime.date.today().isoformat()
        if daily_sleep.get("date") == today:
            self.records = daily_sleep.get("records", [])
        else:
            self.records = []
            self._save_records()

    def _save_records(self):
        
        save_user_data({
            "daily_sleep": {
                "date": datetime.date.today().isoformat(),
                "records": self.records
            }
        })
        event_bus.publish(event_bus.SLEEP_ADDED)

    def _init_components(self):
        dropdown_height = 48
        time_field_width = 55
        time_field_height = 45
        

        self.bedtime_date = ft.Dropdown(
            hint_text=i18n_manager.t("hint_pleaseselect"),
            options=[
                ft.dropdown.Option(key="yesterday", text=i18n_manager.t("sleep_date_yesterday")),
                ft.dropdown.Option(key="today", text=i18n_manager.t("sleep_date_today")),
            ],
            height=dropdown_height, content_padding=8, text_size=13,
            border_radius=8, value="yesterday"
        )
        
        self.bedtime_hour = ft.TextField(
            hint_text="23", width=time_field_width, height=time_field_height, 
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER, border_radius=8
        )
        self.bedtime_minute = ft.TextField(
            hint_text="00", width=time_field_width, height=time_field_height, 
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER, border_radius=8
        )
        

        self.wakeup_date = ft.Dropdown(
            hint_text=i18n_manager.t("hint_pleaseselect"),
            options=[
                ft.dropdown.Option(key="yesterday", text=i18n_manager.t("sleep_date_yesterday")),
                ft.dropdown.Option(key="today", text=i18n_manager.t("sleep_date_today")),
            ],
            height=dropdown_height, content_padding=8, text_size=13,
            border_radius=8, value="today"
        )
        
        self.wakeup_hour = ft.TextField(
            hint_text="07", width=time_field_width, height=time_field_height, 
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER, border_radius=8
        )
        self.wakeup_minute = ft.TextField(
            hint_text="00", width=time_field_width, height=time_field_height, 
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER, border_radius=8
        )
        

        self.quality_selector = ft.Dropdown(
            hint_text=i18n_manager.t("hint_pleaseselect"),
            options=[
                ft.dropdown.Option(key="excellent", text=i18n_manager.t("sleep_quality_excellent")),
                ft.dropdown.Option(key="good", text=i18n_manager.t("sleep_quality_good")),
                ft.dropdown.Option(key="fair", text=i18n_manager.t("sleep_quality_fair")),
                ft.dropdown.Option(key="poor", text=i18n_manager.t("sleep_quality_poor")),
            ],
            height=dropdown_height, content_padding=8, text_size=13,
            border_radius=8, value="good"
        )
        

        self.error_text = ft.Text("", size=12, color=ft.Colors.RED_500, visible=False)
        

        self.records_column = ft.Column(spacing=10)
        

        self.confirmation_dialog = create_confirmation_dialog(
            "", self._on_confirm_delete, self._close_dialog
        )

    def _build_content(self):

        col1 = ft.Container(
            content=ft.Column([
                I18nText(key="sleep_bedtime", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.INDIGO_400),
                self.bedtime_date,
                ft.Row([
                    self.bedtime_hour,
                    ft.Text(":", size=18, weight=ft.FontWeight.BOLD),
                    self.bedtime_minute,
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=2)
            ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            padding=8,
            border_radius=8
        )
        
        col2 = ft.Container(
            content=ft.Column([
                I18nText(key="sleep_wakeup", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.ORANGE_500),
                self.wakeup_date,
                ft.Row([
                    self.wakeup_hour,
                    ft.Text(":", size=18, weight=ft.FontWeight.BOLD),
                    self.wakeup_minute,
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=2)
            ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            padding=8,
            border_radius=8
        )
        
        col3 = ft.Container(
            content=ft.Column([
                I18nText(key="sleep_quality", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_500),
                self.quality_selector,
                ft.ElevatedButton(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=16),
                            ft.Text(i18n_manager.t("sleep_add"), color=ft.Colors.WHITE)
                        ], tight=True, spacing=5),
                        padding=ft.padding.symmetric(horizontal=10, vertical=3)
                    ),
                    bgcolor=ft.Colors.INDIGO_400,
                    on_click=self._add_sleep_record
                )
            ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            padding=8,
            border_radius=8
        )
        
        return ft.Column([

            ft.Row([
                ft.Icon(ft.Icons.BEDTIME, color=ft.Colors.INDIGO_400),
                I18nText(key="sleep_title", size=18, weight=ft.FontWeight.W_600)
            ]),
            ft.Divider(height=10, color="transparent"),
            

            ft.Row([col1, col2, col3], spacing=10),
            

            ft.Container(content=self.error_text, alignment=ft.Alignment(0, 0)),
            
            ft.Divider(height=10, color=ft.Colors.GREY_300),
            

            self.records_column
        ], spacing=5)

    def _validate_time_order(self, bed_date_str, bed_hour, bed_minute, wake_date_str, wake_hour, wake_minute):
        
        today = datetime.date.today()
        

        if bed_date_str == "yesterday":
            bed_date = today - datetime.timedelta(days=1)
        else:
            bed_date = today
        

        if wake_date_str == "yesterday":
            wake_date = today - datetime.timedelta(days=1)
        else:
            wake_date = today
        
        bedtime = datetime.datetime.combine(bed_date, datetime.time(bed_hour, bed_minute))
        wakeup = datetime.datetime.combine(wake_date, datetime.time(wake_hour, wake_minute))
        
        if wakeup <= bedtime:
            return False, i18n_manager.t("sleep_error_invalid_time")
        

        duration = wakeup - bedtime
        duration_minutes = int(duration.total_seconds() / 60)
        
        if duration_minutes <= 0 or duration_minutes > 24 * 60:
            return False, i18n_manager.t("sleep_error_invalid_time")
        
        return True, ""

    def _show_error(self, message):
        
        self.error_text.value = message
        self.error_text.visible = True
        if self.page:
            self.error_text.update()

    def _hide_error(self):
        
        self.error_text.visible = False
        if self.page:
            self.error_text.update()

    def _add_sleep_record(self, e):
        
        try:
            self._hide_error()
            

            bed_hour = int(self.bedtime_hour.value or "23")
            bed_minute = int(self.bedtime_minute.value or "0")
            wake_hour = int(self.wakeup_hour.value or "7")
            wake_minute = int(self.wakeup_minute.value or "0")
            

            if not (0 <= bed_hour <= 23 and 0 <= bed_minute <= 59):
                self._show_error(i18n_manager.t("sleep_error_invalid_time"))
                return
            if not (0 <= wake_hour <= 23 and 0 <= wake_minute <= 59):
                self._show_error(i18n_manager.t("sleep_error_invalid_time"))
                return
            
            today = datetime.date.today()
            

            if self.bedtime_date.value == "yesterday":
                bed_date = today - datetime.timedelta(days=1)
            else:
                bed_date = today
            

            if self.wakeup_date.value == "yesterday":
                wake_date = today - datetime.timedelta(days=1)
            else:
                wake_date = today
            
            new_bedtime = datetime.datetime.combine(bed_date, datetime.time(bed_hour, bed_minute))
            new_wakeup = datetime.datetime.combine(wake_date, datetime.time(wake_hour, wake_minute))
            

            if new_wakeup <= new_bedtime:
                 self._show_error(i18n_manager.t("sleep_error_invalid_time"))
                 return

            duration = new_wakeup - new_bedtime
            duration_minutes = int(duration.total_seconds() / 60)
            
            if duration_minutes <= 0 or duration_minutes > 24 * 60:
                 self._show_error(i18n_manager.t("sleep_error_invalid_time"))
                 return

            for record in self.records:
                try:
                    r_bed = datetime.datetime.fromisoformat(record["bedtime"])
                    r_wake = datetime.datetime.fromisoformat(record["wakeup"])
                    

                    if max(new_bedtime, r_bed) < min(new_wakeup, r_wake):
                         self._show_error(i18n_manager.t("sleep_error_overlap"))
                         return
                except (ValueError, KeyError):
                    continue
            

            record = {
                "id": str(uuid.uuid4()),
                "bedtime": new_bedtime.isoformat(),
                "wakeup": new_wakeup.isoformat(),
                "duration_minutes": duration_minutes,
                "quality": self.quality_selector.value or "good"
            }
            
            self.records.append(record)
            self._save_records()
            self._update_records_ui()
            

            self.bedtime_hour.value = ""
            self.bedtime_minute.value = ""
            self.wakeup_hour.value = ""
            self.wakeup_minute.value = ""
            if self.page:
                self.update()
                
        except (ValueError, TypeError):
            self._show_error(i18n_manager.t("sleep_error_invalid_time"))

    def _delete_record(self, record_id):
        
        self._record_to_delete = record_id
        self.confirmation_dialog.title.value = i18n_manager.t("sleep_confirm_delete")
        self.confirmation_dialog.open = True
        if self.page:
            self.page.update()

    def _on_confirm_delete(self, e):
        
        if self._record_to_delete:
            self.records = [r for r in self.records if r["id"] != self._record_to_delete]
            self._save_records()
            self._update_records_ui()
        self._close_dialog()

    def _close_dialog(self, e=None):
        self.confirmation_dialog.open = False
        self._record_to_delete = None
        if self.page:
            self.page.update()

    def _format_duration(self, minutes):
        
        hours = minutes // 60
        mins = minutes % 60
        h_text = i18n_manager.t("sleep_hours")
        m_text = i18n_manager.t("sleep_minutes")
        if hours > 0 and mins > 0:
            return f"{hours}{h_text}{mins}{m_text}"
        elif hours > 0:
            return f"{hours}{h_text}"
        else:
            return f"{mins}{m_text}"

    def _get_quality_color(self, quality):
        
        colors = {
            "excellent": ft.Colors.GREEN_500,
            "good": ft.Colors.BLUE_500,
            "fair": ft.Colors.ORANGE_500,
            "poor": ft.Colors.RED_500
        }
        return colors.get(quality, ft.Colors.GREY_500)

    def _get_quality_text(self, quality):
        
        return i18n_manager.t(f"sleep_quality_{quality}")

    def _update_records_ui(self):
        
        self.records_column.controls.clear()
        
        if not self.records:
            self.records_column.controls.append(
                ft.Container(
                    content=I18nText(
                        key="sleep_no_record",
                        size=14,
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=20
                )
            )
        else:
            for record in self.records:
                try:
                    bedtime = datetime.datetime.fromisoformat(record["bedtime"])
                    wakeup = datetime.datetime.fromisoformat(record["wakeup"])
                    duration = record["duration_minutes"]
                    quality = record.get("quality", "good")
                    
                    record_card = ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.NIGHTLIGHT, color=ft.Colors.INDIGO_300, size=16),
                                    ft.Text(bedtime.strftime("%H:%M"), size=14, weight=ft.FontWeight.W_500),
                                    ft.Text("→", size=14),
                                    ft.Icon(ft.Icons.WB_SUNNY, color=ft.Colors.ORANGE_300, size=16),
                                    ft.Text(wakeup.strftime("%H:%M"), size=14, weight=ft.FontWeight.W_500),
                                ], spacing=5),
                                ft.Row([
                                    ft.Container(
                                        content=ft.Text(
                                            self._format_duration(duration),
                                            size=12,
                                            color=ft.Colors.WHITE
                                        ),
                                        bgcolor=ft.Colors.INDIGO_400,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        border_radius=10
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            self._get_quality_text(quality),
                                            size=12,
                                            color=ft.Colors.WHITE
                                        ),
                                        bgcolor=self._get_quality_color(quality),
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        border_radius=10
                                    ),
                                ], spacing=8)
                            ], spacing=5),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=ft.Colors.RED_300,
                                icon_size=20,
                                on_click=lambda e, rid=record["id"]: self._delete_record(rid),
                                tooltip=i18n_manager.t("sleep_delete")
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        bgcolor=ft.Colors.GREY_100,
                        padding=12,
                        border_radius=10
                    )
                    self.records_column.controls.append(record_card)
                except (ValueError, KeyError):
                    continue
        
        try:
            self.records_column.update()
        except Exception:
            pass
