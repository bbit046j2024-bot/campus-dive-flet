import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.widgets import PageHeader, EmptyState
from database import fetch_all, execute_query

def show_notifications_panel(page: ft.Page, user: dict):
    """Renders the comprehensive notification dashboard for account alerts."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)
    user_id = user["id"]

    header = PageHeader(
        title="Notification Center",
        subtitle="Manage system alerts, recruitment status modifications, and inbox warnings.",
        is_dark=is_dark
    )

    notifs_list = ft.Column(spacing=10, expand=True)

    def load_notifications():
        notifs_list.controls.clear()
        
        # Select user notifications
        notifications = fetch_all("SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC", (user_id,))

        if not notifications:
            notifs_list.controls.append(
                EmptyState(
                    ft.icons.NOTIFICATIONS_OFF_OUTLINED,
                    "Inbox is Clean",
                    "You have no system alerts or recruitment stage updates.",
                    is_dark=is_dark
                )
            )
        else:
            # Mark all as read button row
            notifs_list.controls.append(
                ft.Row([
                    ft.Text("Recent Announcements", size=14, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                    ft.TextButton(
                        text="Mark all as read",
                        icon=ft.icons.DONE_ALL,
                        on_click=mark_all_read,
                        style=ft.ButtonStyle(color=ThemeColors.PRIMARY_LIGHT if is_dark else ThemeColors.PRIMARY_DARK),
                    )
                ], alignment=ft.MainAxisAlignment.BETWEEN)
            )

            for n in notifications:
                is_unread = n["is_read"] == 0
                bg_opacity = 0.05 if is_unread else 0.01
                border_color = ThemeColors.PRIMARY if is_unread else (ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)
                
                # Determine icon & color based on alert types
                n_type = n.get("type", "info").lower()
                icon = ft.icons.NOTIFICATIONS_ON_OUTLINED
                icon_color = ThemeColors.PRIMARY
                
                if n_type in ("success", "approved"):
                    icon = ft.icons.CHECK_CIRCLE_OUTLINE
                    icon_color = ThemeColors.SUCCESS
                elif n_type in ("error", "danger", "rejected"):
                    icon = ft.icons.ERROR_OUTLINE
                    icon_color = ThemeColors.DANGER
                elif n_type == "warning":
                    icon = ft.icons.WARNING_AMBER_OUTLINED
                    icon_color = ThemeColors.WARNING

                notifs_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(icon, color=icon_color, size=20),
                            ft.Column([
                                ft.Row([
                                    ft.Text(n["title"], size=13, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                                    ft.Container(
                                        content=ft.Text("NEW", size=9, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                                        bgcolor=ThemeColors.PRIMARY,
                                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                        border_radius=4,
                                        visible=is_unread,
                                    )
                                ], spacing=8),
                                ft.Text(n["message"], size=12, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                                ft.Text(n["created_at"], size=9, color=ThemeColors.DARK_TEXT_FAINT if is_dark else ThemeColors.LIGHT_TEXT_FAINT),
                            ], spacing=2, expand=True)
                        ], spacing=12),
                        padding=14,
                        bgcolor=ft.colors.with_opacity(bg_opacity, ThemeColors.PRIMARY if is_unread else (ft.colors.WHITE if is_dark else ft.colors.BLACK)),
                        border_radius=10,
                        border=ft.border.all(1, ft.colors.with_opacity(0.15 if is_unread else 0.05, border_color)),
                    )
                )
        page.update()

    def mark_all_read(e):
        try:
            execute_query("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
            page.open(ft.SnackBar(ft.Text("Marked all notifications as read.")))
            load_notifications()
        except Exception as ex:
            page.open(ft.SnackBar(ft.Text(f"Action failed: {str(ex)}")))

    load_notifications()

    layout = ft.Container(
        content=ft.Column([
            header,
            notifs_list,
        ], spacing=16, scroll=ft.ScrollMode.ADAPTIVE),
        padding=30,
        expand=True,
    )

    return layout
