
import flet as ft
from core.i18n import i18n_manager
from ui.styles import theme_manager

class MobileNavigationBar(ft.Container):
    
    

    MOBILE_NAV_MAP = {
        0: 1,
        1: 5,
        2: 6,
    }
    
    def __init__(self, on_destination_selected):
        self.on_destination_selected = on_destination_selected
        self.selected_index = 0
        self.nav_buttons = {}
        
        super().__init__(
            height=65,
            bgcolor=theme_manager.current_colors.CARD_BG,
            padding=ft.padding.symmetric(horizontal=8, vertical=6),
            border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_200)),
        )
        
        self.nav_configs = [
            {"index": 0, "key": "nav_water", "icon": ft.Icons.WATER_DROP_OUTLINED, "selected_icon": ft.Icons.WATER_DROP},
            {"index": 1, "key": "nav_calendar", "icon": ft.Icons.CALENDAR_MONTH_OUTLINED, "selected_icon": ft.Icons.CALENDAR_MONTH},
            {"index": 2, "key": "nav_settings", "icon": ft.Icons.SETTINGS_OUTLINED, "selected_icon": ft.Icons.SETTINGS},
        ]
        
        self._build_layout()
        i18n_manager.subscribe(self.update_ui)
        theme_manager.subscribe(self.update_theme)

    def will_unmount(self):
        i18n_manager.unsubscribe(self.update_ui)
        theme_manager.unsubscribe(self.update_theme)

    def update_theme(self):
        self.bgcolor = theme_manager.current_colors.CARD_BG
        self._update_selection_visuals()
        if self.page:
            self.update()

    def update_ui(self):
        for config in self.nav_configs:
            idx = config["index"]
            if idx in self.nav_buttons:
                _, text_control, _ = self.nav_buttons[idx]
                text_control.value = i18n_manager.t(config["key"])
        if self.page:
            self.update()

    def _build_nav_item(self, config):
        idx = config["index"]
        key = config["key"]
        icon = config["icon"]
        selected_icon = config["selected_icon"]
        
        is_selected = (idx == self.selected_index)
        current_icon = selected_icon if is_selected else icon
        color = theme_manager.current_colors.PRIMARY if is_selected else ft.Colors.GREY_500
        bgcolor = theme_manager.current_colors.PRIMARY_CONTAINER if is_selected else ft.Colors.TRANSPARENT
        
        icon_control = ft.Icon(current_icon, color=color, size=24)
        text_control = ft.Text(
            i18n_manager.t(key),
            size=10,
            color=color,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.NORMAL
        )
        
        item_container = ft.Container(
            content=ft.Column(
                [icon_control, text_control],
                spacing=2,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=4),
            border_radius=16,
            bgcolor=bgcolor,
            on_click=lambda e, i=idx: self._handle_click(i),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            expand=True,
        )
        
        self.nav_buttons[idx] = (icon_control, text_control, item_container)
        return item_container

    def _build_layout(self):
        row_controls = []
        for config in self.nav_configs:
            row_controls.append(self._build_nav_item(config))
        
        self.content = ft.Row(
            controls=row_controls,
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )

    def _handle_click(self, index):
        if index != self.selected_index:
            self.selected_index = index
            self._update_selection_visuals()

            actual_index = self.MOBILE_NAV_MAP.get(index, index)
            self.on_destination_selected(actual_index)

    def _update_selection_visuals(self):
        for idx, controls in self.nav_buttons.items():
            icon_control, text_control, container = controls
            config = next(c for c in self.nav_configs if c["index"] == idx)
            
            is_selected = (idx == self.selected_index)
            current_icon = config["selected_icon"] if is_selected else config["icon"]
            color = theme_manager.current_colors.PRIMARY if is_selected else ft.Colors.GREY_500
            bgcolor = theme_manager.current_colors.PRIMARY_CONTAINER if is_selected else ft.Colors.TRANSPARENT
            
            icon_control.name = current_icon
            icon_control.color = color
            text_control.color = color
            text_control.weight = ft.FontWeight.W_500 if is_selected else ft.FontWeight.NORMAL
            container.bgcolor = bgcolor
            
            if self.page:
                container.update()

    def set_selection(self, actual_index):
        

        for bar_idx, view_idx in self.MOBILE_NAV_MAP.items():
            if view_idx == actual_index:
                if bar_idx != self.selected_index:
                    self.selected_index = bar_idx
                    self._update_selection_visuals()
                return
