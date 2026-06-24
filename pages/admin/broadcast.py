import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.widgets import PageHeader
from database import fetch_all, execute_query

def show_broadcast_panel(page: ft.Page, user: dict):
    """Renders the broadcast announcement composition view."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)
    admin_id = user["id"]

    header = PageHeader(
        title="Broadcast System",
        subtitle="Send announcements and recruitment alerts to segmented student pools.",
        is_dark=is_dark
    )

    # UI fields
    title_input = ft.TextField(
        label="Notification Title",
        border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER,
        text_size=13,
    )

    message_input = ft.TextField(
        label="Announcement Message",
        multiline=True,
        min_lines=4,
        max_lines=8,
        border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER,
        text_size=13,
    )

    segment_dropdown = ft.Dropdown(
        label="Target Recipient Segment",
        options=[
            ft.dropdown.Option("all", "All Students"),
            ft.dropdown.Option("pending", "Pending/Reviewing Students"),
            ft.dropdown.Option("approved", "Approved Students"),
            ft.dropdown.Option("rejected", "Rejected Students"),
        ],
        value="all",
        border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER,
        text_size=13,
    )

    error_text = ft.Text(value="", color=ThemeColors.DANGER, size=11, visible=False)

    def trigger_broadcast(e):
        error_text.visible = False
        error_text.value = ""

        title = title_input.value.strip()
        msg = message_input.value.strip()
        segment = segment_dropdown.value

        if not title or not msg:
            error_text.value = "Please complete the title and message fields."
            error_text.visible = True
            page.update()
            return

        try:
            # Query targets based on segments
            if segment == "all":
                query = "SELECT id FROM users WHERE role = 'student'"
                params = ()
            elif segment == "pending":
                query = "SELECT id FROM users WHERE role = 'student' AND status IN ('submitted', 'pending', 'under_review', 'documents_uploaded', 'interview_scheduled')"
                params = ()
            elif segment == "approved":
                query = "SELECT id FROM users WHERE role = 'student' AND status = 'approved'"
                params = ()
            elif segment == "rejected":
                query = "SELECT id FROM users WHERE role = 'student' AND status = 'rejected'"
                params = ()
            
            recipients = fetch_all(query, params)
            if not recipients:
                page.open(ft.SnackBar(ft.Text("No students found in the selected target segment.")))
                return

            # Batch insert notifications (Safe SQLite parameterization)
            for r in recipients:
                execute_query("""
                INSERT INTO notifications (user_id, title, message, type)
                VALUES (?, ?, ?, 'info')
                """, (r["id"], title, msg))

            # Log broadcast
            execute_query("""
            INSERT INTO analytics_logs (user_id, action, details)
            VALUES (?, 'Broadcast Announcement', ?)
            """, (admin_id, f"Broadcast title '{title}' sent to segment '{segment}' ({len(recipients)} recipients)"))

            title_input.value = ""
            message_input.value = ""
            page.open(ft.SnackBar(ft.Text(f"Broadcast successfully distributed to {len(recipients)} students.")))
            page.update()
        except Exception as ex:
            error_text.value = f"Broadcast dispatch failed: {str(ex)}"
            error_text.visible = True
            page.update()

    send_btn = ft.ElevatedButton(
        text="Distribute Announcement",
        icon=ft.icons.SEND,
        bgcolor=ThemeColors.PRIMARY,
        color=ft.colors.WHITE,
        on_click=trigger_broadcast,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        height=44,
    )

    broadcast_card = ft.Container(
        content=ft.Column([
            ft.Text("Compose Broadcast Alert", size=16, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
            ft.Divider(height=10, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
            segment_dropdown,
            title_input,
            message_input,
            error_text,
            ft.Row([send_btn], alignment=ft.MainAxisAlignment.START)
        ], spacing=14),
        padding=24,
        max_width=600,
        **style
    )

    layout = ft.Container(
        content=ft.Column([
            header,
            broadcast_card,
        ], spacing=16),
        padding=30,
        expand=True,
    )

    return layout
