import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.widgets import PageHeader
from database import fetch_all, execute_query

def show_roles_manager(page: ft.Page, user: dict):
    """Renders the roles and system permissions management screen."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)
    admin_id = user["id"]

    header = PageHeader(
        title="Role Management",
        subtitle="Configure system user roles, access control levels, and assign account permissions.",
        is_dark=is_dark
    )

    users_list = ft.Column(spacing=8, expand=True)

    def change_user_role(user_id, role_name):
        role_mapping = {
            "admin": 1,
            "manager": 2,
            "interviewer": 3,
            "student": 4
        }
        r_id = role_mapping.get(role_name.lower(), 4)
        try:
            execute_query("UPDATE users SET role = ?, role_id = ? WHERE id = ?", (role_name.lower(), r_id, user_id))
            execute_query("INSERT INTO analytics_logs (user_id, action, details) VALUES (?, ?, ?)",
                          (admin_id, "Change Role", f"Changed user ID {user_id} role to {role_name}"))
            page.open(ft.SnackBar(ft.Text("User role updated successfully.")))
            load_roles_data()
        except Exception as ex:
            page.open(ft.SnackBar(ft.Text(f"Failed to update role: {str(ex)}")))

    def load_roles_data():
        users_list.controls.clear()
        
        # Select users details safely (exclude credentials)
        users = fetch_all("SELECT id, firstname, lastname, email, role FROM users ORDER BY created_at DESC")
        
        # Grid Header
        users_list.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Text("User Details", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=3),
                    ft.Text("Role", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=2),
                ]),
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)))
            )
        )

        for u in users:
            uid = u["id"]
            fullname = f"{u['firstname']} {u['lastname']}"
            
            # Disable changing self role to avoid lockouts
            is_self = uid == admin_id
            
            role_dropdown = ft.Dropdown(
                options=[
                    ft.dropdown.Option("admin", "Admin"),
                    ft.dropdown.Option("manager", "Manager"),
                    ft.dropdown.Option("interviewer", "Interviewer"),
                    ft.dropdown.Option("student", "Student"),
                ],
                value=u["role"],
                disabled=is_self,
                border_color=ThemeColors.PRIMARY,
                text_size=12,
                height=38,
                width=140,
                on_change=lambda e, user_id=uid: change_user_role(user_id, e.control.value),
            )

            row_controls = ft.Row([
                ft.Column([
                    ft.Text(fullname, size=13, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                    ft.Text(u["email"], size=11, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                ], spacing=2, expand=3),
                ft.Row([role_dropdown], expand=2)
            ], alignment=ft.MainAxisAlignment.BETWEEN)

            users_list.controls.append(
                ft.Container(
                    content=row_controls,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border_radius=8,
                    hover_color=ft.colors.with_opacity(0.02, ThemeColors.PRIMARY),
                )
            )
        page.update()

    # Reference permissions list card
    perms = fetch_all("""
        SELECT r.name as role_name, GROUP_CONCAT(p.name, ', ') as perm_list
        FROM roles r
        LEFT JOIN role_permissions rp ON rp.role_id = r.id
        LEFT JOIN permissions p ON p.id = rp.permission_id
        GROUP BY r.id
    """)
    
    perms_column = ft.Column(spacing=10)
    for p in perms:
        perms_column.controls.append(
            ft.Column([
                ft.Text(p["role_name"], size=13, weight=ft.FontWeight.BOLD, color=ThemeColors.PRIMARY),
                ft.Text(p["perm_list"] or "No explicitly assigned permissions.", size=11, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                ft.Divider(height=10, color=ft.colors.with_opacity(0.05, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER))
            ], spacing=2)
        )

    roles_info_card = ft.Container(
        content=ft.Column([
            ft.Text("Role Permissions Matrix", size=15, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
            ft.Divider(height=10, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
            perms_column
        ], spacing=12),
        padding=24,
        width=300,
        **style
    )

    users_roles_card = ft.Container(
        content=ft.Column([
            ft.Text("System Accounts", size=15, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
            ft.Divider(height=10, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
            users_list
        ], spacing=10),
        padding=24,
        expand=True,
        **style
    )

    load_roles_data()

    layout = ft.Container(
        content=ft.Column([
            header,
            ft.Row([users_roles_card, roles_info_card], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START, spacing=16),
        ], spacing=16),
        padding=30,
        expand=True,
    )

    return layout
