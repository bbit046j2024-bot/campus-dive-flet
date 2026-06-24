import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.navbar import Navbar

def show_about(page: ft.Page):
    """Renders the About page."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)

    title_block = ft.Column(
        controls=[
            ft.Text("About Campus Dive", size=36, weight=ft.FontWeight.BLACK, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT, text_align=ft.TextAlign.CENTER),
            ft.Text("A Secure Migration and Rebuilding Project", size=15, color=ThemeColors.PRIMARY, text_align=ft.TextAlign.CENTER),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4,
    )

    mission_text = ft.Text(
        "Campus Dive is a modern, unified workspace migrated from a legacy React/PHP stack to a robust single-file Python Flet desktop and web platform. "
        "Our goal is to deliver an integrated student onboarding workflow, social community hub, and built-in code vulnerability scanner, "
        "whilst maintaining the highest software development security standards.",
        size=14,
        color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED,
        text_align=ft.TextAlign.CENTER,
    )

    # Security implementation cards
    sec_features = [
        ("No SQL Injections", "Parameterized SQL is enforced across every lookup and query to database.py, eliminating parameter insertion bugs."),
        ("No Path Traversal", "All document uploads and downloads are strictly bound via os.path.basename and verified absolute paths within the uploads folder."),
        ("Bcrypt Password Hashing", "Zero hardcoded user passwords. On-the-fly random salts are generated and verified via the secure bcrypt library."),
        ("Session Boundaries", "Clean state boundaries enforced inside python code, blocking cross-session memory leaks or CSRF requests.")
    ]

    sec_cards = ft.Row(
        wrap=True,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=16,
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row([
                            ft.Icon(ft.icons.SHIELD_OUTLINED, color=ThemeColors.SUCCESS, size=20),
                            ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                        ], spacing=8),
                        ft.Text(desc, size=11, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                    ],
                    spacing=8,
                ),
                width=230,
                height=130,
                padding=16,
                **style
            ) for title, desc in sec_features
        ]
    )

    content_container = ft.Container(
        content=ft.Column(
            controls=[
                title_block,
                ft.Container(height=15),
                mission_text,
                ft.Container(height=30),
                ft.Text("Engineered Security Standard", size=20, weight=ft.FontWeight.BLACK, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                ft.Container(height=10),
                sec_cards,
                ft.Container(height=30),
                ft.ElevatedButton(
                    text="Back to Landing Page",
                    on_click=lambda _: page.go("/"),
                    bgcolor=ThemeColors.PRIMARY,
                    color=ft.colors.WHITE,
                    height=44,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        ),
        padding=ft.padding.symmetric(vertical=40, horizontal=30),
        alignment=ft.alignment.center,
        max_width=800,
    )

    layout = ft.Column(
        controls=[
            Navbar(page, "/about"),
            ft.Container(content=content_container, alignment=ft.alignment.top_center, expand=True)
        ],
        spacing=0,
        scroll=ft.ScrollMode.ADAPTIVE,
    )

    return layout
