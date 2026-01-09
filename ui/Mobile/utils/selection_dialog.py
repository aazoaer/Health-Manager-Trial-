

import flet as ft
from typing import Callable, Optional, List
from core.i18n import i18n_manager

class SelectionOption:
    
    def __init__(
        self, 
        key: str, 
        label_key: str = None, 
        label: str = None,
        icon: str = None
    ):
        
        self.key = key
        self.label_key = label_key
        self.label = label
        self.icon = icon
    
    def get_display_text(self) -> str:
        
        if self.label_key:
            return i18n_manager.t(self.label_key)
        return self.label or self.key

class SelectionDialog(ft.Container):
    
    
    def __init__(
        self,
        title_key: str,
        options: List[SelectionOption],
        on_select: Callable[[str], None],
        selected_key: str = None,
        selected_color: str = ft.Colors.BLUE,
        width: int = 300,
        height: int = 400,
        trigger_width: int = None,
        show_search: bool = False,
        search_placeholder_key: str = "search_placeholder",
        border_radius: int = 8,
        **container_kwargs
    ):
        
        self.title_key = title_key
        self.options = options
        self.on_select = on_select
        self.selected_key = selected_key
        self.selected_color = selected_color
        self.dialog_width = width
        self.dialog_height = height
        self.trigger_width = trigger_width
        self.show_search = show_search
        self.search_placeholder_key = search_placeholder_key
        self._filtered_options = options.copy()
        

        self.display_text = ft.Text(
            self._get_selected_display(),
            size=14
        )
        

        self.search_box = ft.TextField(
            hint_text=i18n_manager.t(search_placeholder_key),
            prefix_icon=ft.Icons.SEARCH,
            height=40,
            text_size=14,
            content_padding=10,
            on_change=self._on_search
        ) if show_search else None
        

        self.list_view = ft.ListView(spacing=0, expand=True)
        

        dialog_content_children = []
        if self.search_box:
            dialog_content_children.append(self.search_box)
            dialog_content_children.append(ft.Divider())
        dialog_content_children.append(self.list_view)
        
        self.dialog = ft.AlertDialog(
            title=ft.Text(i18n_manager.t(title_key)),
            content=ft.Container(
                content=ft.Column(dialog_content_children, spacing=10, expand=True),
                width=width,
                height=height,
                padding=0
            ),
            actions=[
                ft.TextButton(
                    i18n_manager.t("cancel_button"), 
                    on_click=self._close_dialog
                )
            ],
            modal=True,
        )
        

        trigger_container = ft.Container(
            content=self.display_text,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=border_radius,
            padding=ft.padding.symmetric(horizontal=12, vertical=14),
            width=trigger_width,
            on_click=self._open_dialog,
            ink=True,
        )
        
        super().__init__(
            content=trigger_container,
            **container_kwargs
        )
    
    def _get_selected_display(self) -> str:
        
        if not self.selected_key:
            return ""
        for opt in self.options:
            if opt.key == self.selected_key:
                return opt.get_display_text()
        return self.selected_key
    
    def _build_list_items(self):
        
        items = []
        for opt in self._filtered_options:
            is_selected = opt.key == self.selected_key
            items.append(
                ft.ListTile(
                    title=ft.Text(opt.get_display_text()),
                    leading=ft.Icon(
                        ft.Icons.CHECK, 
                        color=self.selected_color
                    ) if is_selected else ft.Icon(
                        ft.Icons.CIRCLE_OUTLINED, 
                        size=10, 
                        opacity=0
                    ),
                    on_click=lambda e, key=opt.key: self._select_item(key),
                    content_padding=ft.padding.symmetric(horizontal=10),
                )
            )
        self.list_view.controls = items
    
    def _open_dialog(self, e):
        
        if self.search_box:
            self.search_box.value = ""
        self._filtered_options = self.options.copy()
        self._build_list_items()
        

        self.dialog.title.value = i18n_manager.t(self.title_key)
        self.dialog.actions[0].text = i18n_manager.t("cancel_button")
        
        self.dialog.open = True
        if self.page:
            self.page.update()
    
    def _close_dialog(self, e=None):
        
        self.dialog.open = False
        if self.page:
            self.page.update()
    
    def _select_item(self, key: str):
        
        self.selected_key = key
        self.display_text.value = self._get_selected_display()
        
        if self.page:
            self.display_text.update()
        
        self._close_dialog()
        
        if self.on_select:
            self.on_select(key)
    
    def _on_search(self, e):
        
        search_term = (self.search_box.value or "").lower()
        if not search_term:
            self._filtered_options = self.options.copy()
        else:
            self._filtered_options = [
                opt for opt in self.options
                if search_term in opt.get_display_text().lower() or search_term in opt.key.lower()
            ]
        self._build_list_items()
        if self.page:
            self.list_view.update()
    
    def did_mount(self):
        
        if self.page and self.dialog not in self.page.overlay:
            self.page.overlay.append(self.dialog)
            self.page.update()
    
    def will_unmount(self):
        
        if self.dialog:
            self.dialog.open = False
        if self.page and self.dialog in self.page.overlay:
            self.page.overlay.remove(self.dialog)
    
    def set_selected(self, key: str):
        
        self.selected_key = key
        self.display_text.value = self._get_selected_display()
        if self.page:
            self.display_text.update()
    
    def get_selected(self) -> str:
        
        return self.selected_key
    
    def update_options(self, options: List[SelectionOption]):
        
        self.options = options
        self._filtered_options = options.copy()
