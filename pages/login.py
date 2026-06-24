import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.navbar import Navbar
from auth import login_user

def show_login(page: ft.Page):
    """Renders the login screen with email, password fields and redirects based on role."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)

    # Input elements
    email_input = ft.TextField(
        label="Email Address",
        prefix_icon=ft.icons.EMAIL_OUTLINED,
        keyboard_type=ft.KeyboardType.EMAIL,
        border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER,
        focused_border_color=ThemeColors.PRIMARY,
        label_style=ft.TextStyle(color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
        text_size=14,
    )

    password_input = ft.TextField(
        label="Password",
        prefix_icon=ft.icons.LOCK_OUTLINED,
        password=True,
        can_reveal_password=True,
        border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER,
        focused_border_color=ThemeColors.PRIMARY,
        label_style=ft.TextStyle(color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
        text_size=14,
    )

    error_text = ft.Text(
        value="",
        color=ThemeColors.DANGER,
        size=12,
        visible=False,
    )

    def handle_login(e):
        error_text.visible = False
        error_text.value = ""
        
        email = email_input.value.strip()
        password = password_input.value.strip()

        if not email or not password:
            error_text.value = "Please fill in all fields."
            error_text.visible = True
            page.update()
            return

        try:
            user = login_user(email, password)
            if user:
                # Save user session details
                page.session.store.set("user", user)
                
                # Role-based redirection
                role = user.get("role", "student")
                if role in ("admin", "manager", "interviewer"):
                    page.go("/admin/dashboard")
                else:
                    page.go("/student/dashboard")
            else:
                error_text.value = "Invalid email or password."
                error_text.visible = True
                page.update()
        except Exception as ex:
            error_text.value = f"An error occurred: {str(ex)}"
            error_text.visible = True
            page.update()

    login_button = ft.ElevatedButton(
        text="Sign In",
        on_click=handle_login,
        bgcolor=ThemeColors.PRIMARY,
        color=ft.colors.WHITE,
        height=46,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        expand=True,
    )

    # Form card layout
    form_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Welcome Back", size=24, weight=ft.FontWeight.BLACK, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                ft.Text("Enter your credentials to access your workspace", size=12, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                ft.Container(height=10),
                email_input,
                password_input,
                error_text,
                ft.Container(height=5),
                ft.Row(
                    controls=[
                        ft.TextButton(
                            text="Forgot Password?",
                            on_click=lambda _: page.open(ft.SnackBar(ft.Text("Please contact system administrators at admin@campusdive.com"))),
                            style=ft.ButtonStyle(color=ThemeColors.PRIMARY_LIGHT if is_dark else ThemeColors.PRIMARY_DARK),
                        )
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
                ft.Container(height=5),
                ft.Row([login_button], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=10),
                ft.Row(
                    controls=[
                        ft.Text("Don't have an account?", color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, size=13),
                        ft.TextButton(
                            text="Sign Up",
                            on_click=lambda _: page.go("/register"),
                            style=ft.ButtonStyle(color=ThemeColors.PRIMARY_LIGHT if is_dark else ThemeColors.PRIMARY_DARK),
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            spacing=10,
        ),
        padding=30,
        width=400,
        **style
    )

    layout = ft.Column(
        controls=[
            Navbar(page, "/login"),
            ft.Container(
                content=form_card,
                alignment=ft.alignment.center,
                expand=True,
                margin=ft.margin.only(top=40),
            )
        ],
        spacing=0,
        scroll=ft.ScrollMode.ADAPTIVE,
    )

    return layout
