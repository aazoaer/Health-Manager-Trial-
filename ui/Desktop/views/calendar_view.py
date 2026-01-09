import flet as ft
from ui.Desktop.components.calendar_grid_card import CalendarGridCard
from ui.Desktop.components.calendar_chart_card import CalendarChartCard

class CalendarView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        

        self.chart_card = CalendarChartCard()
        

        self.grid_card = CalendarGridCard(on_month_change=self.chart_card.update_month)
        
        self.content = ft.Row(
            controls=[
                self.grid_card,
                self.chart_card
            ],
            spacing=20,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH
        )
        
        self.padding = ft.padding.symmetric(horizontal=50, vertical=20)
