import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.navbar import Navbar

def show_about(page: ft.Page):
    """Renders the about page with information about Campus Dive."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)

    # About Section
    about_content = ft.Column(
        controls=[
            ft.Text(
                "About Campus Dive",
                size=32,
                weight=ft.FontWeight.BLACK,
                color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT,
            ),
            ft.Text(
                "A comprehensive student recruitment and onboarding platform",
                size=16,
                color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED,
            ),
            ft.Container(height=20),
            ft.Text(
                "Our Mission",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT,
            ),
            ft.Text(
                "Campus Dive streamlines the student recruitment process by providing a modern, secure platform "
                "for managing applications, documents, communications, and community engagement. Our platform empowers "
                "students and administrators to collaborate efficiently throughout the onboarding journey.",
                size=14,
                color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED,
            ),
            ft.Container(height=20),
            ft.Text(
                "Key Features",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT,
            ),
            ft.Column(
                controls=[
                    ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color=ThemeColors.SUCCESS, size=20),
                        ft.Text("Streamlined recruitment pipeline with status tracking", size=13)
                    ], spacing=10),
                    ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color=ThemeColors.SUCCESS, size=20),
                        ft.Text("Secure document management and verification", size=13)
                    ], spacing=10),
                    ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color=ThemeColors.SUCCESS, size=20),
                        ft.Text("Direct messaging between applicants and coordinators", size=13)
                    ], spacing=10),
                    ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color=ThemeColors.SUCCESS, size=20),
                        ft.Text("Community groups and social engagement features", size=13)
                    ], spacing=10),
                    ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color=ThemeColors.SUCCESS, size=20),
                        ft.Text("Advanced analytics and audit logging", size=13)
                    ], spacing=10),
                    ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color=ThemeColors.SUCCESS, size=20),
                        ft.Text("Role-based access control with granular permissions", size=13)
                    ], spacing=10),
                ],
                spacing=8,
            ),
            ft.Container(height=20),
            ft.Text(
                "Technology",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT,
            ),
            ft.Text(
                "Built with Python and Flet for cross-platform desktop deployment. Utilizes SQLite for reliable "
                "data persistence with enterprise-grade security measures including bcrypt password hashing, "
                "CSRF protection, and secure file handling.",
                size=14,
                color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED,
            ),
            ft.Container(height=20),
            ft.Text(
                "Contact & Support",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT,
            ),
            ft.Text(
                "For support inquiries or more information, please contact: admin@campusdive.com",
                size=14,
                color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED,
            ),
            ft.Container(height=20),
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        text="Back to Home",
                        on_click=lambda _: page.go("/"),
                        bgcolor=ThemeColors.PRIMARY,
                        color=ft.colors.WHITE,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        ],
        spacing=12,
    )

    about_card = ft.Container(
        content=about_content,
        padding=40,
        width=800,
        **style
    )

    layout = ft.Column(
        controls=[
            Navbar(page, "/about"),
            ft.Container(
                content=about_card,
                alignment=ft.alignment.center,
                expand=True,
                margin=ft.margin.only(top=40, bottom=40),
            )
        ],
        spacing=0,
        scroll=ft.ScrollMode.ADAPTIVE,
    )

    return layout
