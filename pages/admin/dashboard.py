import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.widgets import PageHeader, StatCard, StatusBadge, EmptyState
from database import fetch_all, fetch_one, execute_query

def show_admin_dashboard(page: ft.Page, user: dict):
    """Renders the main admin management dashboard with summary stats and quick actions."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)
    admin_id = user["id"]

    header = PageHeader(
        title="Admin Control Center",
        subtitle="Manage student onboarding workflows, review uploaded credentials, and update application pipelines.",
        is_dark=is_dark
    )

    # 1. Fetch KPI Statistics (JOIN Queries / Optimized as per DB Standards)
    total_students_row = fetch_one("SELECT COUNT(*) as count FROM users WHERE role = 'student'")
    pending_review_row = fetch_one("SELECT COUNT(*) as count FROM users WHERE role = 'student' AND status IN ('submitted', 'pending', 'documents_uploaded', 'under_review')")
    approved_row = fetch_one("SELECT COUNT(*) as count FROM users WHERE role = 'student' AND status = 'approved'")
    rejected_row = fetch_one("SELECT COUNT(*) as count FROM users WHERE role = 'student' AND status = 'rejected'")

    total_count = total_students_row["count"] if total_students_row else 0
    pending_count = pending_review_row["count"] if pending_review_row else 0
    approved_count = approved_row["count"] if approved_row else 0
    rejected_count = rejected_row["count"] if rejected_row else 0

    stats_row = ft.Row(
        controls=[
            StatCard("Total Applicants", total_count, ft.Icons.PEOPLE, ThemeColors.PRIMARY, is_dark),
            StatCard("Pending Review", pending_count, ft.Icons.HOURGLASS_EMPTY, ThemeColors.WARNING, is_dark),
            StatCard("Approved", approved_count, ft.Icons.CHECK_CIRCLE_OUTLINE, ThemeColors.SUCCESS, is_dark),
            StatCard("Rejected", rejected_count, ft.Icons.CANCEL_OUTLINED, ThemeColors.DANGER, is_dark),
        ],
        spacing=16,
    )

    # 2. Recent Applications List
    recent_list = ft.Column(spacing=8, expand=True)

    def update_student_status(student_id, new_status):
        try:
            # Update user status
            execute_query("UPDATE users SET status = ? WHERE id = ?", (new_status, student_id))
            
            # Record audit stage change
            execute_query("INSERT INTO application_stages (user_id, stage_name) VALUES (?, ?)", (student_id, new_status))
            
            # Send Notification Alert to the student
            status_labels = {
                "under_review": ("Application Under Review", "Your onboarding profile is now being reviewed by our coordinators."),
                "approved": ("Application Approved!", "Congratulations! Your application has been approved. Click to view your offer letter."),
                "rejected": ("Application Update", "Your application has been reviewed, and update details are posted to your dashboard.")
            }
            
            if new_status in status_labels:
                title, msg = status_labels[new_status]
                execute_query("INSERT INTO notifications (user_id, title, message, type) VALUES (?, ?, ?, ?)", 
                              (student_id, title, msg, "success" if new_status == "approved" else ("error" if new_status == "rejected" else "info")))
            
            # If approved, generate default recruitment letter (V2 feature)
            if new_status == "approved":
                student_name = fetch_one("SELECT firstname, lastname FROM users WHERE id = ?", (student_id,))
                name_str = f"{student_name['firstname']} {student_name['lastname']}" if student_name else "Student"
                
                letter_md = f"""# Campus Recruitment Offer Letter

Dear **{name_str}**,

We are pleased to inform you that you have been officially accepted through our recruitment evaluation process. We were highly impressed by your academic records and background credentials.

Please log in to your **Campus Dive Settings** to complete any outstanding details and finalize your profile verification.

Best Regards,
**Campus Recruitment Team**
"""
                # Check if letter exists first
                letter_exists = fetch_one("SELECT id FROM recruitment_letters WHERE user_id = ?", (student_id,))
                if not letter_exists:
                    execute_query("INSERT INTO recruitment_letters (user_id, letter_content, sent_by) VALUES (?, ?, ?)", 
                                  (student_id, letter_md, admin_id))

            # Log admin action in audit logs (Security requirements)
            execute_query("INSERT INTO analytics_logs (user_id, action, details) VALUES (?, ?, ?)", 
                          (admin_id, "Update Student Status", f"Updated student ID {student_id} status to {new_status}"))

            page.open(ft.SnackBar(ft.Text(f"Updated student status to {new_status.replace('_', ' ').title()}.")))
            page.go("/admin/dashboard") # refresh page
        except Exception as ex:
            page.open(ft.SnackBar(ft.Text(f"Status update failed: {str(ex)}")))

    def load_recent_applicants():
        recent_list.controls.clear()
        
        # Select recent applicants (students) - select explicit columns only (resolves API Overfetching / security gap)
        query = """
        SELECT id, firstname, lastname, email, phone, status, created_at
        FROM users
        WHERE role = 'student'
        ORDER BY created_at DESC
        LIMIT 5
        """
        applicants = fetch_all(query)

        if not applicants:
            recent_list.controls.append(
                EmptyState(
                    ft.Icons.PEOPLE_OUTLINE,
                    "No Recent Applicants",
                    "New applicant profiles will show up here as they register.",
                    is_dark=is_dark
                )
            )
        else:
            # Header Columns - FIX #10: Complete truncated line
            recent_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text("Student Details", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=3),
                        ft.Text("Status", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=1),
                        ft.Text("Quick Actions", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=2, text_align=ft.TextAlign.RIGHT),
                    ]),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)))
                )
            )

            # Row rendering
            for app in applicants:
                app_id = app["id"]
                fullname = f"{app['firstname']} {app['lastname']}"
                
                # Checkbox actions logic
                actions_row = ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.RATE_REVIEW,
                            icon_color=ThemeColors.WARNING,
                            icon_size=18,
                            tooltip="Move to Review",
                            on_click=lambda e, aid=app_id: update_student_status(aid, "under_review"),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CHECK,
                            icon_color=ThemeColors.SUCCESS,
                            icon_size=18,
                            tooltip="Approve Application",
                            on_click=lambda e, aid=app_id: update_student_status(aid, "approved"),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_color=ThemeColors.DANGER,
                            icon_size=18,
                            tooltip="Reject Application",
                            on_click=lambda e, aid=app_id: update_student_status(aid, "rejected"),
                        ),
                    ],
                    spacing=2,
                    alignment=ft.MainAxisAlignment.END,
                )

                recent_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(fullname, size=13, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                                ft.Text(f"{app['email']} • {app['phone']}", size=11, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                            ], spacing=2, expand=3),
                            StatusBadge(app["status"]),
                            ft.Container(content=actions_row, expand=2, alignment=ft.alignment.center_right)
                        ]),
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        border_radius=8,
                        on_hover=lambda e: setattr(e.control, "bgcolor", ft.colors.with_opacity(0.02, ThemeColors.PRIMARY) if e.data == "true" else ft.colors.TRANSPARENT) or e.control.update(),
                    )
                )
        page.update()

    load_recent_applicants()

    recent_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Recent Onboarding Applications", size=14, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                ft.TextButton("View all students", on_click=lambda _: page.go("/admin/students"), style=ft.ButtonStyle(color=ThemeColors.PRIMARY)),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=10, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
            recent_list
        ], spacing=10),
        padding=24,
        expand=True,
        **style
    )

    layout = ft.Container(
        content=ft.Column(
            controls=[
                header,
                stats_row,
                ft.Container(height=10),
                ft.Row([recent_card], spacing=16),
            ],
            spacing=16,
            scroll=ft.ScrollMode.ADAPTIVE,
        ),
        padding=30,
        expand=True,
    )

    return layout
