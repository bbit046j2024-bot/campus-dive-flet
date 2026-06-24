import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.widgets import PageHeader, ProgressTracker, StatusBadge, StatCard
from database import fetch_all, fetch_one
from auth import get_user_by_id

def show_student_dashboard(page: ft.Page, user: dict):
    """Renders the main student dashboard content page."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)
    user_id = user["id"]

    # Retrieve fresh user data to reflect status updates
    fresh_user = get_user_by_id(user_id) or user
    status = fresh_user.get("status", "submitted")

    # 1. Header
    header = PageHeader(
        title=f"Welcome, {fresh_user.get('firstname', 'Student')}!",
        subtitle="Track your recruitment progress, manage documents, and connect with groups.",
        is_dark=is_dark
    )

    # 2. Recruitment Progress Tracker
    tracker_section = ft.Column(
        controls=[
            ft.Text("Application Pipeline", size=16, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
            ProgressTracker(status, is_dark=is_dark)
        ],
        spacing=10,
    )

    # 3. Document Count & Verification Alert
    # Retrieve documents count
    doc_count_row = fetch_one("SELECT COUNT(*) as count FROM documents WHERE user_id = ?", (user_id,))
    doc_count = doc_count_row["count"] if doc_count_row else 0

    unread_notifs_row = fetch_one("SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND is_read = 0", (user_id,))
    unread_notifs = unread_notifs_row["count"] if unread_notifs_row else 0

    stats_row = ft.Row(
        controls=[
            StatCard("Uploaded Documents", doc_count, ft.icons.UPLOAD_FILE, ThemeColors.PRIMARY, is_dark),
            StatCard("Unread Notifications", unread_notifs, ft.icons.NOTIFICATIONS, ThemeColors.ACCENT, is_dark),
        ],
        spacing=16,
    )

    # Status Info Banner
    banner_color = ThemeColors.PRIMARY
    banner_title = "Application Submitted"
    banner_desc = "Your initial application was received. Please upload your Resume and Academic Transcripts under 'My Documents' to advance to the review stage."

    if status == "documents_uploaded":
        banner_color = ThemeColors.ACCENT
        banner_title = "Documents Uploaded Successfully"
        banner_desc = "Thank you! Your documents have been uploaded. An administrator will review your files shortly."
    elif status == "under_review":
        banner_color = ThemeColors.WARNING
        banner_title = "Under Review"
        banner_desc = "Your profile and documents are currently being evaluated by our recruitment committee."
    elif status == "interview_scheduled":
        banner_color = ThemeColors.INFO
        banner_title = "Interview Scheduled!"
        banner_desc = "An interviewer has been assigned to you. Please check your inbox and notifications for interview slot scheduling."
    elif status == "approved":
        banner_color = ThemeColors.SUCCESS
        banner_title = "Congratulations! You are Approved"
        banner_desc = "You have successfully passed the recruitment pipeline. Your recruitment letter is ready below."
    elif status == "rejected":
        banner_color = ThemeColors.DANGER
        banner_title = "Application Status Update"
        banner_desc = "Thank you for your interest. Unfortunately, your application has not been selected for this cycle."

    banner = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.icons.INFO_OUTLINE, color=banner_color, size=28),
                ft.Column(
                    controls=[
                        ft.Row([
                            ft.Text(banner_title, size=14, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                            StatusBadge(status)
                        ], spacing=10),
                        ft.Text(banner_desc, size=12, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, max_width=600),
                    ],
                    spacing=4,
                    expand=True,
                )
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
        ),
        padding=16,
        border_radius=12,
        bgcolor=ft.colors.with_opacity(0.08, banner_color),
        border=ft.border.all(1, ft.colors.with_opacity(0.2, banner_color)),
    )

    # 4. Recruitment Letter display (if approved)
    letter_container = ft.Column(visible=False)
    if status == "approved":
        letter_row = fetch_one("SELECT letter_content FROM recruitment_letters WHERE user_id = ? ORDER BY sent_at DESC LIMIT 1", (user_id,))
        if letter_row and letter_row["letter_content"]:
            letter_content = letter_row["letter_content"]
            letter_container = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Official Recruitment Offer", size=16, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                        ft.Container(
                            content=ft.Markdown(
                                value=letter_content,
                                selectable=True,
                                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                            ),
                            padding=20,
                            bgcolor=ft.colors.with_opacity(0.03, ft.colors.WHITE if is_dark else ft.colors.BLACK),
                            border=ft.border.all(1, ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
                            border_radius=8,
                        )
                    ],
                    spacing=10,
                ),
                margin=ft.margin.only(top=10),
                visible=True
            )

    # 5. Recent notifications
    notifications = fetch_all("SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 3", (user_id,))
    notif_list = ft.Column(spacing=8)
    if not notifications:
        notif_list.controls.append(ft.Text("No recent alerts.", size=12, color=ThemeColors.DARK_TEXT_FAINT if is_dark else ThemeColors.LIGHT_TEXT_FAINT))
    else:
        for n in notifications:
            notif_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.NOTIFICATIONS_ON_OUTLINED, color=ThemeColors.PRIMARY, size=16),
                        ft.Column([
                            ft.Text(n["title"], size=12, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                            ft.Text(n["message"], size=11, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                        ], spacing=2, expand=True)
                    ], spacing=10),
                    padding=10,
                    bgcolor=ft.colors.with_opacity(0.02, ft.colors.WHITE if is_dark else ft.colors.BLACK),
                    border_radius=8,
                    border=ft.border.all(1, ft.colors.with_opacity(0.05, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
                )
            )

    notif_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Recent Alerts", size=14, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                ft.TextButton("Clear all", on_click=lambda _: clear_notifs(page, user_id), style=ft.ButtonStyle(color=ThemeColors.PRIMARY)),
            ], alignment=ft.MainAxisAlignment.BETWEEN),
            ft.Divider(height=10, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
            notif_list
        ], spacing=10),
        padding=16,
        expand=True,
        **style
    )

    def clear_notifs(p, uid):
        from database import execute_query
        execute_query("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (uid,))
        p.go("/student/dashboard") # refresh

    # Assemble main layout
    dashboard_layout = ft.Container(
        content=ft.Column(
            controls=[
                header,
                banner,
                ft.Container(height=10),
                stats_row,
                ft.Container(height=10),
                tracker_section,
                letter_container,
                ft.Container(height=10),
                ft.Row([notif_card], spacing=16),
            ],
            spacing=16,
            scroll=ft.ScrollMode.ADAPTIVE,
        ),
        padding=30,
        expand=True,
    )

    return dashboard_layout
