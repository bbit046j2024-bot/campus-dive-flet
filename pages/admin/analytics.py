import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.widgets import PageHeader, EmptyState
from database import fetch_all

def show_analytics_panel(page: ft.Page, user: dict):
    """Renders the administrative system audit log and activity timeline."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)

    header = PageHeader(
        title="System Analytics & Audit Logs",
        subtitle="Review security events, access control updates, status modifications, and system activity logs.",
        is_dark=is_dark
    )

    logs_list = ft.Column(spacing=6, expand=True)

    def load_audit_logs():
        logs_list.controls.clear()
        
        # Select audit logs with associated names
        query = """
        SELECT al.id, al.action, al.details, al.ip_address, al.created_at, u.firstname, u.lastname
        FROM analytics_logs al
        LEFT JOIN users u ON u.id = al.user_id
        ORDER BY al.created_at DESC
        LIMIT 50
        """
        logs = fetch_all(query)

        if not logs:
            logs_list.controls.append(
                EmptyState(
                    ft.icons.HISTORY,
                    "No Log Records",
                    "Security audit and admin activity log items will appear here.",
                    is_dark=is_dark
                )
            )
        else:
            # Header
            logs_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text("Timestamp", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=2),
                        ft.Text("User", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=2),
                        ft.Text("Action", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=2),
                        ft.Text("Details", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=4),
                    ]),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)))
                )
            )

            # Rows
            for l in logs:
                user_str = f"{l['firstname']} {l['lastname']}" if l["firstname"] else "Guest / System"
                
                row_controls = ft.Row([
                    ft.Text(l["created_at"], size=11, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=2),
                    ft.Text(user_str, size=12, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT, expand=2, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Container(
                        content=ft.Text(l["action"].upper(), size=10, weight=ft.FontWeight.BOLD, color=ThemeColors.PRIMARY_LIGHT if is_dark else ThemeColors.PRIMARY_DARK),
                        bgcolor=ft.colors.with_opacity(0.1, ThemeColors.PRIMARY),
                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        border_radius=4,
                        expand=2,
                        alignment=ft.alignment.center,
                    ),
                    ft.Text(l["details"] or "", size=11, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=4, overflow=ft.TextOverflow.ELLIPSIS),
                ], alignment=ft.MainAxisAlignment.BETWEEN)

                logs_list.controls.append(
                    ft.Container(
                        content=row_controls,
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        border_radius=8,
                        hover_color=ft.colors.with_opacity(0.01, ThemeColors.PRIMARY),
                    )
                )
        page.update()

    load_audit_logs()

    logs_card = ft.Container(
        content=ft.Column([
            ft.Text("Activity Logs", size=15, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
            ft.Divider(height=10, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
            logs_list,
        ], spacing=10),
        padding=24,
        expand=True,
        **style
    )

    layout = ft.Container(
        content=ft.Column([
            header,
            logs_card,
        ], spacing=16),
        padding=30,
        expand=True,
    )

    return layout
