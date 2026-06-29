import flet as ft
from components.theme import ThemeColors

class Navbar(ft.Container):
    """Public landing page navigation bar."""
    def __init__(self, page: ft.Page, active_route: str):
        self.page = page
        self.active_route = active_route
        self.is_dark = page.theme_mode == ft.ThemeMode.DARK

        super().__init__(
            bgcolor=ft.colors.with_opacity(0.8, ThemeColors.DARK_BG) if self.is_dark else ft.colors.with_opacity(0.8, ThemeColors.LIGHT_BG),
            border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if self.is_dark else ThemeColors.LIGHT_BORDER))),
            padding=ft.padding.symmetric(horizontal=30, vertical=16),
            height=70,
            alignment=ft.alignment.center,
        )
        self.build_navbar()

    def build_navbar(self):
        brand = ft.GestureDetector(
            content=ft.Row(
                controls=[
                    ft.Image(src="new_logo.png", width=30, height=30, fit=ft.ImageFit.CONTAIN),
                    ft.Text("Campus Dive", size=18, weight=ft.FontWeight.W_900, color=ThemeColors.DARK_TEXT if self.is_dark else ThemeColors.LIGHT_TEXT),
                ],
                spacing=8,
            ),
            on_tap=lambda _: self.page.go("/"),
            mouse_cursor=ft.MouseCursor.CLICK,
        )

        # Nav Links
        def link_style(route_path):
            is_active = self.active_route == route_path
            return {
                "color": ThemeColors.PRIMARY_LIGHT if is_active else (ThemeColors.DARK_TEXT_MUTED if self.is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                "weight": ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
            }

        nav_links = ft.Row(
            controls=[
                ft.TextButton(
                    text="Home",
                    on_click=lambda _: self.page.go("/"),
                    style=ft.ButtonStyle(color=link_style("/")["color"]),
                ),
                ft.TextButton(
                    text="About",
                    on_click=lambda _: self.page.go("/about"),
                    style=ft.ButtonStyle(color=link_style("/about")["color"]),
                ),
            ],
            spacing=10,
        )

        auth_links = ft.Row(
            controls=[
                ft.TextButton(
                    text="Sign In",
                    on_click=lambda _: self.page.go("/login"),
                    style=ft.ButtonStyle(color=ThemeColors.DARK_TEXT if self.is_dark else ThemeColors.LIGHT_TEXT),
                ),
                ft.ElevatedButton(
                    text="Apply Now",
                    on_click=lambda _: self.page.go("/register"),
                    bgcolor=ThemeColors.PRIMARY,
                    color=ft.colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    )
                )
            ],
            spacing=10,
        )

        # Main layout structure
        self.content = ft.Row(
            controls=[
                brand,
                nav_links,   # Placed directly here so SPACE_BETWEEN pushes it to the center
                auth_links,  # Pushed to the far right
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )