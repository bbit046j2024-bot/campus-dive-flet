import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.navbar import Navbar
from auth import register_user, login_user

def show_register(page: ft.Page):
    """Renders the student registration screen with verification validation."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)

    # Input Fields
    firstname_input = ft.TextField(label="First Name", border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER, text_size=13)
    lastname_input = ft.TextField(label="Last Name", border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER, text_size=13)
    email_input = ft.TextField(label="Email Address", keyboard_type=ft.KeyboardType.EMAIL, border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER, text_size=13)
    phone_input = ft.TextField(label="Phone Number", keyboard_type=ft.KeyboardType.PHONE, border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER, text_size=13)
    student_id_input = ft.TextField(label="Student ID (Optional)", border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER, text_size=13)
    password_input = ft.TextField(label="Password", password=True, can_reveal_password=True, border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER, text_size=13)
    confirm_password_input = ft.TextField(label="Confirm Password", password=True, can_reveal_password=True, border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER, text_size=13)

    error_text = ft.Text(value="", color=ThemeColors.DANGER, size=11, visible=False)

    def handle_register(e):
        error_text.visible = False
        error_text.value = ""

        # Retrieve form data
        fn = firstname_input.value.strip()
        ln = lastname_input.value.strip()
        email = email_input.value.strip()
        phone = phone_input.value.strip()
        sid = student_id_input.value.strip()
        pwd = password_input.value.strip()
        cpwd = confirm_password_input.value.strip()

        # Validate entries
        if not all([fn, ln, email, phone, pwd, cpwd]):
            error_text.value = "All fields except Student ID are required."
            error_text.visible = True
            page.update()
            return

        if pwd != cpwd:
            error_text.value = "Passwords do not match."
            error_text.visible = True
            page.update()
            return

        if len(pwd) < 6:
            error_text.value = "Password must be at least 6 characters."
            error_text.visible = True
            page.update()
            return

        try:
            # Register user
            register_user(fn, ln, email, phone, sid, pwd)
            
            # Auto-login after successful registration
            user = login_user(email, pwd)
            if user:
                page.session.store.set("user", user)
                page.go("/student/dashboard")
            else:
                page.go("/login")
        except ValueError as val_err:
            error_text.value = str(val_err)
            error_text.visible = True
            page.update()
        except Exception as ex:
            error_text.value = f"Registration error: {str(ex)}"
            error_text.visible = True
            page.update()

    register_button = ft.ElevatedButton(
        text="Submit Application",
        on_click=handle_register,
        bgcolor=ThemeColors.PRIMARY,
        color=ft.colors.WHITE,
        height=46,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        expand=True,
    )

    form_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Onboarding Application", size=24, weight=ft.FontWeight.BLACK, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                ft.Text("Submit your profile details to start student recruitment", size=12, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                ft.Container(height=10),
                ft.Row([firstname_input, lastname_input], spacing=10),
                email_input,
                ft.Row([phone_input, student_id_input], spacing=10),
                password_input,
                confirm_password_input,
                error_text,
                ft.Container(height=10),
                ft.Row([register_button]),
                ft.Container(height=5),
                ft.Row(
                    controls=[
                        ft.Text("Already registered?", color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, size=13),
                        ft.TextButton(
                            text="Sign In",
                            on_click=lambda _: page.go("/login"),
                            style=ft.ButtonStyle(color=ThemeColors.PRIMARY_LIGHT if is_dark else ThemeColors.PRIMARY_DARK),
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            spacing=10,
        ),
        padding=30,
        width=460,
        **style
    )

    layout = ft.Column(
        controls=[
            Navbar(page, "/register"),
            ft.Container(
                content=form_card,
                alignment=ft.alignment.center,
                expand=True,
                margin=ft.margin.only(top=30, bottom=30),
            )
        ],
        spacing=0,
        scroll=ft.ScrollMode.ADAPTIVE,
    )

    return layout
