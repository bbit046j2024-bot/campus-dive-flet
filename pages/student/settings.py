import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.widgets import PageHeader
from auth import update_user_profile, change_user_password, get_user_by_id

def show_student_settings(page: ft.Page, user: dict):
    """Renders the settings panel with options for profile updates and password change."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)
    user_id = user["id"]

    # Refresh fresh profile details
    fresh_user = get_user_by_id(user_id) or user

    header = PageHeader(
        title="Account Settings",
        subtitle="Manage your profile information and update account security preferences.",
        is_dark=is_dark
    )

    # 1. Profile Information Section
    fn_input = ft.TextField(label="First Name", value=fresh_user.get("firstname", ""), border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER, text_size=13, expand=True)
    ln_input = ft.TextField(label="Last Name", value=fresh_user.get("lastname", ""), border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER, text_size=13, expand=True)
    phone_input = ft.TextField(label="Phone Number", value=fresh_user.get("phone", ""), border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER, text_size=13)
    location_input = ft.TextField(label="Location", value=fresh_user.get("location", "") or "", border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER, text_size=13)
    bio_input = ft.TextField(label="Bio", value=fresh_user.get("bio", "") or "", multiline=True, min_lines=3, max_lines=5, border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER, text_size=13)

    profile_error = ft.Text(value="", color=ThemeColors.DANGER, size=11, visible=False)

    def save_profile(e):
        profile_error.visible = False
        profile_error.value = ""

        fn = fn_input.value.strip()
        ln = ln_input.value.strip()
        phone = phone_input.value.strip()
        bio = bio_input.value.strip()
        loc = location_input.value.strip()

        if not all([fn, ln, phone]):
            profile_error.value = "First Name, Last Name, and Phone Number are required."
            profile_error.visible = True
            page.update()
            return

        try:
            updated_user = update_user_profile(user_id, fn, ln, phone, bio, loc)
            page.session.store.set("user", updated_user)
            page.open(ft.SnackBar(ft.Text("Profile details updated successfully.")))
            page.go("/student/settings") # reload view
        except Exception as ex:
            profile_error.value = f"Update failed: {str(ex)}"
            profile_error.visible = True
            page.update()

    profile_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Profile Details", size=16, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                ft.Divider(height=10, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
                ft.Row([fn_input, ln_input], spacing=10),
                ft.Row([phone_input, location_input], spacing=10),
                bio_input,
                profile_error,
                ft.ElevatedButton(
                    text="Save Profile Changes",
                    bgcolor=ThemeColors.PRIMARY,
                    color=ft.colors.WHITE,
                    on_click=save_profile,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                )
            ],
            spacing=14,
        ),
        padding=24,
        expand=True,
        **style
    )

    # 2. Security Section (Password Updates)
    current_pwd_input = ft.TextField(label="Current Password", password=True, can_reveal_password=True, border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER, text_size=13)
    new_pwd_input = ft.TextField(label="New Password", password=True, can_reveal_password=True, border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER, text_size=13)
    confirm_pwd_input = ft.TextField(label="Confirm New Password", password=True, can_reveal_password=True, border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER, text_size=13)

    security_error = ft.Text(value="", color=ThemeColors.DANGER, size=11, visible=False)

    def save_password(e):
        security_error.visible = False
        security_error.value = ""

        current_pwd = current_pwd_input.value.strip()
        new_pwd = new_pwd_input.value.strip()
        confirm_pwd = confirm_pwd_input.value.strip()

        if not all([current_pwd, new_pwd, confirm_pwd]):
            security_error.value = "All fields are required to update password."
            security_error.visible = True
            page.update()
            return

        if new_pwd != confirm_pwd:
            security_error.value = "New passwords do not match."
            security_error.visible = True
            page.update()
            return

        if len(new_pwd) < 6:
            security_error.value = "New password must be at least 6 characters."
            security_error.visible = True
            page.update()
            return

        try:
            change_user_password(user_id, current_pwd, new_pwd)
            current_pwd_input.value = ""
            new_pwd_input.value = ""
            confirm_pwd_input.value = ""
            page.open(ft.SnackBar(ft.Text("Password updated successfully!")))
            page.update()
        except ValueError as val_err:
            security_error.value = str(val_err)
            security_error.visible = True
            page.update()
        except Exception as ex:
            security_error.value = f"Security update failed: {str(ex)}"
            security_error.visible = True
            page.update()

    security_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Security Credentials", size=16, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                ft.Divider(height=10, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
                current_pwd_input,
                new_pwd_input,
                confirm_pwd_input,
                security_error,
                ft.ElevatedButton(
                    text="Update Password",
                    bgcolor=ThemeColors.PRIMARY,
                    color=ft.colors.WHITE,
                    on_click=save_password,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                )
            ],
            spacing=14,
        ),
        padding=24,
        expand=True,
        **style
    )

    layout = ft.Container(
        content=ft.Column(
            controls=[
                header,
                ft.Row([profile_card, security_card], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START, spacing=16),
            ],
            spacing=16,
            scroll=ft.ScrollMode.ADAPTIVE,
        ),
        padding=30,
        expand=True,
    )

    return layout
