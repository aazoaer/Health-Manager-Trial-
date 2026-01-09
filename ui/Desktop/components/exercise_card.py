import flet as ft
import datetime
import uuid
from ui.styles import AppColors, CARD_STYLE
from core import event_bus
from data.storage import load_user_data, save_user_data
from ui.Desktop.utils.confirmation import create_confirmation_dialog
from ui.Desktop.utils.selection_dialog import SelectionDialog, SelectionOption
from core.i18n import i18n_manager, I18nText

from core.calculations import EXERCISE_METS, get_calories_for_exercise, get_hourly_calories

try:
    from pypinyin import pinyin, Style
    PYPINYIN_AVAILABLE = True
except ImportError:
    PYPINYIN_AVAILABLE = False

def _get_pinyin_initials(text):
    if not PYPINYIN_AVAILABLE or not text: return ""
    try:
        initials = pinyin(text, style=Style.FIRST_LETTER)
        return "".join([p[0] for p in initials]).lower()
    except: return ""

def _get_full_pinyin(text):
    if not PYPINYIN_AVAILABLE or not text: return ""
    try:
        py = pinyin(text, style=Style.NORMAL)
        return "".join([p[0] for p in py]).lower()
    except: return ""

def _fuzzy_match_type(query, text):
    query_lower = query.lower()
    text_lower = text.lower()
    if query_lower == text_lower: return 100
    if text_lower.startswith(query_lower): return 90
    if query_lower in text_lower: return 80
    if PYPINYIN_AVAILABLE:
        initials = _get_pinyin_initials(text)
        if initials.startswith(query_lower): return 70
        if query_lower in initials: return 60
        full = _get_full_pinyin(text)
        if full.startswith(query_lower): return 50
        if query_lower in full: return 40
    return 0

_keys = list(EXERCISE_METS.keys())
_keys.sort(key=lambda x: (x == "other", x))
EXERCISE_TYPES = _keys

class ExerciseCard(ft.Container):
    def __init__(self):
        super().__init__(**CARD_STYLE)
        self.records = []
        self._record_to_delete = None
        self.user_weight = 70
        self.all_exercise_types = EXERCISE_TYPES
        self.filtered_exercise_types = EXERCISE_TYPES
        
        self._initialize_data()
        self._init_components()
        self.content = self._build_content()
        self._update_records_ui()

    def did_mount(self):
        if self.page and self.confirmation_dialog not in self.page.overlay:
            self.page.overlay.append(self.confirmation_dialog)
        if self.page and self.type_dialog not in self.page.overlay:
            self.page.overlay.append(self.type_dialog)

        self.intensity_selector.did_mount()
        if self.page:
            self.page.update()

    def will_unmount(self):
        if self.page and self.confirmation_dialog in self.page.overlay:
            self.page.overlay.remove(self.confirmation_dialog)
        if self.page and self.type_dialog in self.page.overlay:
            self.type_dialog.open = False
            self.page.overlay.remove(self.type_dialog)

        self.intensity_selector.will_unmount()

    def _initialize_data(self):
        
        user_data = load_user_data()
        

        try:
            self.user_weight = float(user_data.get("weight", 70))
        except (ValueError, TypeError):
            self.user_weight = 70
        
        daily_exercises = user_data.get("daily_exercises", {})
        
        today = datetime.date.today().isoformat()
        if daily_exercises.get("date") == today:
            self.records = daily_exercises.get("records", [])
        else:
            self.records = []
            self._save_records()

    def _save_records(self):
        
        save_user_data({
            "daily_exercises": {
                "date": datetime.date.today().isoformat(),
                "records": self.records
            }
        })
        event_bus.publish(event_bus.EXERCISE_ADDED)

    def _calculate_calories(self, exercise_type, duration_minutes, intensity):
        
        if exercise_type == "other":

            try:
                hourly_rate = float(self.hourly_kcal_input.value or "0")
            except ValueError:
                hourly_rate = 0
            return int(round(hourly_rate * (duration_minutes / 60)))
        else:
            return get_calories_for_exercise(exercise_type, duration_minutes, intensity, self.user_weight)

    def _init_components(self):

        self.selected_type = "running"

        self.selected_intensity = "medium"
        

        self.type_display_text = ft.Text(
            i18n_manager.t(f"exercise_type_{self.selected_type}"),
            size=14
        )
        

        self.type_selector_container = ft.Container(
            content=self.type_display_text,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=14),
            on_click=self._open_type_dialog,
            ink=True,
        )
        

        self.type_search_box = ft.TextField(
            hint_text=i18n_manager.t("search_placeholder"),
            prefix_icon=ft.Icons.SEARCH,
            height=40,
            text_size=14,
            content_padding=10,
            on_change=self._on_search_type
        )
        

        self.type_list_view = ft.ListView(spacing=0, height=300)

        self.type_dialog = ft.AlertDialog(
            title=ft.Text(i18n_manager.t("exercise_type")),
            content=ft.Container(
                content=ft.Column([
                    self.type_search_box,
                    ft.Divider(),
                    self.type_list_view
                ], spacing=10),
                width=450,
                height=400,
                padding=0
            ),
            actions=[ft.TextButton(i18n_manager.t("cancel_button"), on_click=self._close_type_dialog)],
            modal=True,
        )
        

        self.duration_input = ft.TextField(
            label=f"{i18n_manager.t('exercise_duration')} ({i18n_manager.t('exercise_min')})",
            hint_text="0",
            value="0",
            height=50,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8,
        )
        

        intensity_options = [
            SelectionOption(key="low", label_key="exercise_intensity_low"),
            SelectionOption(key="medium", label_key="exercise_intensity_medium"),
            SelectionOption(key="high", label_key="exercise_intensity_high"),
        ]
        self.intensity_selector = SelectionDialog(
            title_key="exercise_intensity",
            options=intensity_options,
            on_select=self._on_intensity_select,
            selected_key=self.selected_intensity,
            selected_color=ft.Colors.ORANGE,
            width=300,
            height=200,
        )
        

        self.custom_type_input = ft.TextField(
            label=i18n_manager.t("exercise_custom_type"),
            hint_text=i18n_manager.t("exercise_custom_type_hint"),
            height=50,
            border_radius=8,
            visible=False,
        )
        

        initial_hourly = get_hourly_calories("running", "medium", self.user_weight)
        self.hourly_kcal_input = ft.TextField(
            label=f"{i18n_manager.t('exercise_hourly_kcal')} ({i18n_manager.t('exercise_kcal')}/h)",
            hint_text="0",
            value=str(initial_hourly),
            height=50,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8,
        )
        

        self.records_column = ft.Column(spacing=10)
        

        self.confirmation_dialog = create_confirmation_dialog(
            "", self._on_confirm_delete, self._close_dialog
        )

    def _open_type_dialog(self, e):
        
        self.type_search_box.value = ""
        self.filtered_exercise_types = self.all_exercise_types
        self._update_type_list()
        self.type_dialog.open = True
        if self.page:
            self.page.update()

    def _on_search_type(self, e):
        
        search_term = self.type_search_box.value
        if not search_term:
            self.filtered_exercise_types = self.all_exercise_types
        else:
            search_term = search_term.lower()
            scored_results = []
            
            for t in self.all_exercise_types:
                t_name = i18n_manager.t(f"exercise_type_{t}")
                

                score = _fuzzy_match_type(search_term, t_name)
                

                if score < 80:
                    key_score = _fuzzy_match_type(search_term, t)
                    if key_score > score:
                        score = key_score
                        
                if score > 0:
                    scored_results.append((score, t))
            

            scored_results.sort(key=lambda x: (-x[0], x[1] == "other", x[1]))
            
            self.filtered_exercise_types = [t for score, t in scored_results]
        
        self._update_type_list()

    def _update_type_list(self):
        
        items = []
        for t in self.filtered_exercise_types:
            is_selected = t == self.selected_type
            items.append(
                ft.ListTile(
                    title=ft.Text(i18n_manager.t(f"exercise_type_{t}")),
                    leading=ft.Icon(ft.Icons.CHECK, color=ft.Colors.TEAL) if is_selected else ft.Icon(ft.Icons.CIRCLE_OUTLINED, size=10, opacity=0),
                    on_click=lambda e, type_key=t: self._select_type(type_key),
                    content_padding=ft.padding.symmetric(horizontal=10),
                )
            )
        self.type_list_view.controls = items
        if self.page:
            self.type_list_view.update()

    def _select_type(self, type_key):
        
        self.selected_type = type_key
        self.type_display_text.value = i18n_manager.t(f"exercise_type_{type_key}")
        

        self.custom_type_input.visible = (type_key == "other")
        

        
        if self.page:
            self.type_display_text.update()
            self.custom_type_input.update()
            
        self._close_type_dialog(None)
        self._update_hourly_display()

    def _close_type_dialog(self, e):
        self.type_dialog.open = False
        if self.page:
            self.page.update()

    def _on_intensity_select(self, intensity_key):
        
        self.selected_intensity = intensity_key
        self._update_hourly_display()

    def _copy_ai_prompt(self, e):
        

        if self.selected_type == "other" and hasattr(self, 'custom_type_input'):
            exercise_name = self.custom_type_input.value or i18n_manager.t("exercise_type_other")
        else:
            exercise_name = i18n_manager.t(f"exercise_type_{self.selected_type}")
        intensity_name = i18n_manager.t(f"exercise_intensity_{self.selected_intensity}")
        priority_text = "How many calories are burned per hour doing"
        prompt = f"{priority_text} {exercise_name} ({intensity_name})? Assuming weight {self.user_weight} kg."
        
        try:

            import subprocess
            process = subprocess.Popen('clip', stdin=subprocess.PIPE, shell=True)
            process.communicate(input=prompt.encode('utf-16-le'))
        except Exception:
            pass
        

        try:
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(i18n_manager.t("hint_copied")),
                    duration=2000
                )
                self.page.snack_bar.open = True
                self.page.update()
        except Exception:
            pass

    def _build_content(self):
        return ft.Column([

            ft.Row([
                ft.Icon(ft.Icons.FITNESS_CENTER, color=ft.Colors.TEAL_500),
                I18nText(key="exercise_title", size=18, weight=ft.FontWeight.W_600)
            ]),
            ft.Divider(height=15, color="transparent"),
            

            ft.Row([
                ft.Container(content=self.type_selector_container, expand=2),
                ft.Container(content=self.duration_input, expand=1),
                ft.Container(content=self.intensity_selector, expand=1),
                ft.Container(content=self.hourly_kcal_input, expand=1),
                ft.IconButton(
                    icon=ft.Icons.CONTENT_COPY,
                    icon_color=ft.Colors.GREY_600,
                    tooltip=i18n_manager.t("hint_copy_prompt"),
                    on_click=self._copy_ai_prompt
                ),
                ft.IconButton(
                    icon=ft.Icons.OPEN_IN_NEW,
                    icon_color=ft.Colors.BLUE_500,
                    tooltip=i18n_manager.t("exercise_ask_ai"),
                    on_click=self._open_ai_url
                )
            ], spacing=10),
            
            ft.Divider(height=10, color="transparent"),
            

            self.custom_type_input,
            
            ft.Divider(height=10, color="transparent"),
            

            ft.Row([
                ft.ElevatedButton(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=16),
                            ft.Text(i18n_manager.t("exercise_add"), color=ft.Colors.WHITE)
                        ], tight=True, spacing=5),
                        padding=ft.padding.symmetric(horizontal=10, vertical=3)
                    ),
                    bgcolor=ft.Colors.TEAL_500,
                    on_click=self._add_exercise_record
                )
            ], alignment=ft.MainAxisAlignment.START),
            
            ft.Divider(height=15, color=ft.Colors.GREY_300),
            

            self.records_column
        ], spacing=5)

    def _add_exercise_record(self, e):
        
        try:
            exercise_type = self.selected_type
            if not exercise_type:
                return
            
            duration = int(self.duration_input.value or "0")
            if duration <= 0 or duration > 600:
                self.duration_input.error_text = i18n_manager.t("food_error_invalid")
                self.duration_input.update()
                return
            
            intensity = self.selected_intensity
            

            try:
                hourly_rate = float(self.hourly_kcal_input.value or "0")
                if hourly_rate < 0:
                    self.hourly_kcal_input.error_text = i18n_manager.t("food_error_invalid")
                    self.hourly_kcal_input.update()
                    return
            except ValueError:
                self.hourly_kcal_input.error_text = i18n_manager.t("food_error_invalid")
                self.hourly_kcal_input.update()
                return
            

            duration_hours = duration / 60
            calories = round(hourly_rate * duration_hours)
            

            record = {
                "id": str(uuid.uuid4()),
                "type": exercise_type,
                "duration_minutes": duration,
                "intensity": intensity,
                "calories": calories,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            self.records.append(record)
            self._save_records()
            self._update_records_ui()
            

            self.selected_type = "running"
            self.type_display_text.value = i18n_manager.t("exercise_type_running")
            self.selected_intensity = "medium"
            self.intensity_selector.set_selected("medium")
            self.duration_input.value = "0"
            self.duration_input.error_text = None
            self.hourly_kcal_input.error_text = None
            initial_hourly = get_hourly_calories("running", "medium", self.user_weight)
            self.hourly_kcal_input.value = str(initial_hourly)
            if self.page:
                self.update()
                
        except (ValueError, TypeError):
            pass

    def _update_hourly_display(self, e=None):
        
        exercise_type = self.selected_type
        

        intensity = self.selected_intensity
        hourly = get_hourly_calories(exercise_type, intensity, self.user_weight)
        self.hourly_kcal_input.value = str(hourly)
        
        if self.page:
            self.hourly_kcal_input.update()

    def _open_ai_url(self, e):
        
        import webbrowser
        user_data = load_user_data()
        china_mode = user_data.get("china_ai_mode", False)
        
        if china_mode:
            webbrowser.open("https://chat.deepseek.com/")
        else:
            webbrowser.open("https://chatgpt.com/?temporary-chat=true")

    def _delete_record(self, record_id):
        
        self._record_to_delete = record_id
        self.confirmation_dialog.title.value = i18n_manager.t("exercise_confirm_delete")
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

    def _get_exercise_icon(self, exercise_type):
        
        icons = {
            "running": ft.Icons.DIRECTIONS_RUN,
            "walking": ft.Icons.DIRECTIONS_WALK,
            "cycling": ft.Icons.DIRECTIONS_BIKE,
            "swimming": ft.Icons.POOL,
            "yoga": ft.Icons.SELF_IMPROVEMENT,
            "strength": ft.Icons.FITNESS_CENTER,
            "hiit": ft.Icons.FLASH_ON,
            "dance": ft.Icons.MUSIC_NOTE,
            "basketball": ft.Icons.SPORTS_BASKETBALL,
            "football": ft.Icons.SPORTS_SOCCER,
            "badminton": ft.Icons.SPORTS_TENNIS,
            "tennis": ft.Icons.SPORTS_TENNIS,
            "other": ft.Icons.SPORTS
        }
        return icons.get(exercise_type, ft.Icons.SPORTS)

    def _get_intensity_color(self, intensity):
        
        colors = {
            "low": ft.Colors.GREEN_500,
            "medium": ft.Colors.ORANGE_500,
            "high": ft.Colors.RED_500
        }
        return colors.get(intensity, ft.Colors.GREY_500)

    def _update_records_ui(self):
        
        self.records_column.controls.clear()
        
        if not self.records:
            self.records_column.controls.append(
                ft.Container(
                    content=I18nText(
                        key="exercise_no_record",
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
                    exercise_type = record["type"]
                    duration = record["duration_minutes"]
                    intensity = record.get("intensity", "medium")
                    calories = record.get("calories", 0)
                    
                    record_card = ft.Container(
                        content=ft.Row([
                            ft.Row([
                                ft.Icon(
                                    self._get_exercise_icon(exercise_type),
                                    color=ft.Colors.TEAL_500,
                                    size=24
                                ),
                                ft.Column([
                                    ft.Text(
                                        i18n_manager.t(f"exercise_type_{exercise_type}"),
                                        size=14,
                                        weight=ft.FontWeight.W_500
                                    ),
                                    ft.Row([
                                        ft.Container(
                                            content=ft.Text(
                                                f"{duration} {i18n_manager.t('exercise_min')}",
                                                size=11,
                                                color=ft.Colors.WHITE
                                            ),
                                            bgcolor=ft.Colors.TEAL_400,
                                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                            border_radius=8
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                i18n_manager.t(f"exercise_intensity_{intensity}"),
                                                size=11,
                                                color=ft.Colors.WHITE
                                            ),
                                            bgcolor=self._get_intensity_color(intensity),
                                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                            border_radius=8
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                f"🔥 {calories} {i18n_manager.t('exercise_kcal')}",
                                                size=11,
                                                color=ft.Colors.ORANGE_800
                                            ),
                                            bgcolor=ft.Colors.ORANGE_100,
                                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                            border_radius=8
                                        ),
                                    ], spacing=6)
                                ], spacing=4)
                            ], spacing=10),
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
