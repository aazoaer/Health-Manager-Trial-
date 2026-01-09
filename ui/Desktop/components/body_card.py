import flet as ft
from ui.styles import CARD_STYLE
from core.i18n import I18nText

class BodyCard(ft.Container):
    def __init__(self):

        style = CARD_STYLE.copy()
        style["bgcolor"] = ft.Colors.WHITE
        style["expand"] = True

        super().__init__(**style)

        self.content = ft.Column([
            ft.Row([
                I18nText(key="body_shape_title", size=18, weight=ft.FontWeight.W_600)
            ]),

        ])
