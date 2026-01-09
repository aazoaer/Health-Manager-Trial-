import flet as ft
from ui.Desktop.components.header import DateHeader
from ui.Desktop.components.user_info_card import UserInfoCard
from ui.Desktop.components.reminder_card import ReminderCard
from ui.Desktop.components.today_overview_card import TodayOverviewCard

class HomeView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

        self.user_info_card = UserInfoCard()
        self.today_overview_card = TodayOverviewCard()
        self.reminder_card = ReminderCard()

        self.content = ft.ListView(
             controls=[
                DateHeader(),
                ft.Row(
                    controls=[
                        self.user_info_card,
                        ft.Column(
                            controls=[
                                self.reminder_card,
                                ft.Container(content=self.today_overview_card, expand=True) 
                            ],
                            expand=True, 
                            spacing=20,
                            alignment=ft.MainAxisAlignment.START
                        )
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=20
                )
             ],
             padding=ft.padding.only(left=20, top=20, right=35, bottom=20)
        )
