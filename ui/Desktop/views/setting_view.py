import flet as ft
import sys
from core.i18n import I18nText, i18n_manager
from ui.Desktop.components.language_select_card import LanguageSelectCard
from ui.Desktop.components.theme_select_card import ThemeSelectCard
from ui.Desktop.components.close_mode_card import CloseModeCard
from ui.Desktop.components.china_ai_mode_card import ChinaAIModeCard
from data.storage import save_user_data, load_user_data

class SettingView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = ft.padding.all(20)
        
        self.language_card = LanguageSelectCard()
        self.theme_card = ThemeSelectCard()
        self.close_mode_card = CloseModeCard()
        self.china_ai_mode_card = ChinaAIModeCard()
        

        self._load_initial_values()
        
        apply_button_text = I18nText(key="apply_button_text")
        self.apply_button = ft.ElevatedButton(
            content=ft.Container(
                content=apply_button_text,
                padding=ft.padding.symmetric(horizontal=15, vertical=5)
            ),
            icon=ft.Icons.CHECK,
            on_click=self._handle_apply,
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
        )
        
        self.content = ft.Column(
            controls=[
                I18nText(key="settings_title", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                self.language_card,
                self.theme_card,
                self.close_mode_card,
                self.china_ai_mode_card,
                ft.Container(height=20),
                self.apply_button,
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO
        )

        self.restart_dialog = None
        i18n_manager.subscribe(self.update_ui)

    def _load_initial_values(self):
        
        user_data = load_user_data()
        self._initial_language = user_data.get("language", "zh_CN")
        self._initial_theme = user_data.get("theme_mode", "light")
        self._initial_close_mode = user_data.get("close_mode", "ask")
        self._initial_china_ai_mode = user_data.get("china_ai_mode", False)

    def did_mount(self):
        if self.page:
            self.restart_dialog = self._create_restart_dialog()
            if self.restart_dialog not in self.page.overlay:
                self.page.overlay.append(self.restart_dialog)
            
            self.page.update()

    def will_unmount(self):
        i18n_manager.unsubscribe(self.update_ui)
        if self.page and self.restart_dialog:
            try:
                self.page.overlay.remove(self.restart_dialog)
            except ValueError:
                pass

    def update_ui(self):
        if not self.page:
            return
        if self.restart_dialog:
            self._update_restart_dialog()
        self.update()

    def _create_restart_dialog(self):
        self.dialog_title = ft.Text(
            i18n_manager.t("restart_confirm_title"), 
            text_align=ft.TextAlign.CENTER, 
            size=20, 
            weight=ft.FontWeight.W_600
        )
        self.dialog_content = ft.Text(
            i18n_manager.t("restart_confirm_message"), 
            size=15
        )
        self.confirm_button_text = ft.Text(
            i18n_manager.t("confirm_button"), 
            color=ft.Colors.WHITE,
            weight=ft.FontWeight.W_500
        )
        self.cancel_button_text = ft.Text(
            i18n_manager.t("cancel_button"), 
            color=ft.Colors.WHITE,
            weight=ft.FontWeight.W_500
        )
        
        dialog = ft.AlertDialog(
            modal=True,
            title=self.dialog_title,
            content=self.dialog_content,
            shape=ft.RoundedRectangleBorder(radius=20),
            actions=[
                ft.Container(
                    content=ft.Row(
                        [ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20), self.confirm_button_text],
                        tight=True,
                        spacing=8
                    ),
                    bgcolor=ft.Colors.GREEN_600,
                    padding=ft.padding.symmetric(vertical=12, horizontal=24),
                    border_radius=12,
                    on_click=self._confirm_restart,
                    tooltip=i18n_manager.t("confirm_button"),
                    shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.GREEN_200, spread_radius=1)
                ),
                ft.Container(
                    content=ft.Row(
                        [ft.Icon(ft.Icons.CANCEL, color=ft.Colors.WHITE, size=20), self.cancel_button_text],
                        tight=True,
                        spacing=8
                    ),
                    bgcolor=ft.Colors.RED_600,
                    padding=ft.padding.symmetric(vertical=12, horizontal=24),
                    border_radius=12,
                    on_click=self._cancel_restart,
                    tooltip=i18n_manager.t("cancel_button"),
                    shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.RED_200, spread_radius=1)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            content_padding=30,
        )
        return dialog

    def _update_restart_dialog(self):
        if self.restart_dialog:
            self.dialog_title.value = i18n_manager.t("restart_confirm_title")
            self.dialog_content.value = i18n_manager.t("restart_confirm_message")
            self.confirm_button_text.value = i18n_manager.t("confirm_button")
            self.cancel_button_text.value = i18n_manager.t("cancel_button")
            if self.restart_dialog.actions:
                if len(self.restart_dialog.actions) > 0:
                    self.restart_dialog.actions[0].tooltip = i18n_manager.t("confirm_button")
                if len(self.restart_dialog.actions) > 1:
                    self.restart_dialog.actions[1].tooltip = i18n_manager.t("cancel_button")

    def _handle_apply(self, e):

        current_lang = self.language_card.get_selected_language()
        current_theme = self.theme_card.get_selected_theme()
        current_close_mode = self.close_mode_card.get_selected_mode()
        current_china_ai_mode = self.china_ai_mode_card.get_selected_mode()
        
        has_changes = (
            current_lang != self._initial_language or
            current_theme != self._initial_theme or
            current_close_mode != self._initial_close_mode or
            current_china_ai_mode != self._initial_china_ai_mode
        )
        
        if not has_changes:
            if self.page:
                self.page.snack_bar = ft.SnackBar(content=ft.Text(i18n_manager.t("settings_no_changes")))
                self.page.snack_bar.open = True
                self.page.update()
            return
            
        if not current_lang or not current_theme or not current_close_mode:
            return
        
        if not self.page:
            return
        
        save_user_data({
            "language": current_lang,
            "theme_mode": current_theme,
            "close_mode": current_close_mode,
            "china_ai_mode": current_china_ai_mode
        })
        
        if not self.restart_dialog:
            self.restart_dialog = self._create_restart_dialog()
            if self.restart_dialog not in self.page.overlay:
                self.page.overlay.append(self.restart_dialog)
        
        if self.restart_dialog:
            self.restart_dialog.open = True
            self.page.update()

    def _confirm_restart(self, e):
        
        import sys
        import os
        import subprocess
        

        python_exe = sys.executable
        
        if getattr(sys, 'frozen', False):

            pass
                
        else:

            script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'main.py')
            cmd = [python_exe, script_path]
            cwd = os.path.dirname(script_path)
            subprocess.Popen(cmd, cwd=cwd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
        

        if self.page:
            try:
                self.page.window.destroy()
            except:
                pass
        sys.exit(0)

    def _cancel_restart(self, e):
        if self.restart_dialog:
            self.restart_dialog.open = False
            if self.page:
                self.page.update()
