import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.widgets import PageHeader, StatusBadge, EmptyState
from database import fetch_all, fetch_one, execute_query

def show_students_manager(page: ft.Page, user: dict):
    """Renders a secure searchable students grid with detailed review modal dialogs."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)
    admin_id = user["id"]

    header = PageHeader(
        title="Students Directory",
        subtitle="Search, filter, and review student application files and update onboarding statuses.",
        is_dark=is_dark
    )

    # State variables
    search_query = ""
    status_filter = "All"
    students_grid = ft.Column(spacing=8)

    # Search inputs
    search_input = ft.TextField(
        label="Search students by name, email, or ID...",
        prefix_icon=ft.icons.SEARCH,
        on_change=lambda e: handle_search(e.control.value),
        border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER,
        text_size=13,
        expand=True,
    )

    filter_dropdown = ft.Dropdown(
        label="Filter by Status",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Submitted"),
            ft.dropdown.Option("Documents Uploaded"),
            ft.dropdown.Option("Under Review"),
            ft.dropdown.Option("Interview Scheduled"),
            ft.dropdown.Option("Approved"),
            ft.dropdown.Option("Rejected"),
        ],
        value="All",
        on_change=lambda e: handle_filter(e.control.value),
        border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER,
        text_size=13,
        width=200,
    )

    def handle_search(val):
        nonlocal search_query
        search_query = val.strip()
        load_students()

    def handle_filter(val):
        nonlocal status_filter
        status_filter = val
        load_students()

    # Modal trigger handler
    def open_student_modal(student_id):
        # Retrieve complete details securely
        student = fetch_one("SELECT * FROM users WHERE id = ? AND role = 'student'", (student_id,))
        if not student:
            page.open(ft.SnackBar(ft.Text("Student details not found.")))
            return

        docs = fetch_all("SELECT * FROM documents WHERE user_id = ?", (student_id,))

        # Modal dropdown selection
        status_select = ft.Dropdown(
            label="Recruitment Status",
            options=[
                ft.dropdown.Option("submitted", "Submitted"),
                ft.dropdown.Option("under_review", "Under Review"),
                ft.dropdown.Option("interview_scheduled", "Interview Scheduled"),
                ft.dropdown.Option("approved", "Approved"),
                ft.dropdown.Option("rejected", "Rejected"),
            ],
            value=student["status"],
            border_color=ThemeColors.PRIMARY,
            text_size=13,
            width=180,
        )

        def save_status_change(e):
            new_status = status_select.value
            try:
                execute_query("UPDATE users SET status = ? WHERE id = ?", (new_status, student_id))
                execute_query("INSERT OR IGNORE INTO application_stages (user_id, stage_name) VALUES (?, ?)", (student_id, new_status))
                
                # Notification alert
                execute_query("""
                INSERT INTO notifications (user_id, title, message, type)
                VALUES (?, 'Status Updated', ?, 'info')
                """, (student_id, f"Your onboarding recruitment status has been changed to: {new_status.replace('_', ' ').title()}"))

                # Write audit log
                execute_query("INSERT INTO analytics_logs (user_id, action, details) VALUES (?, ?, ?)",
                              (admin_id, "Update Status", f"Updated student ID {student_id} to status {new_status}"))

                page.open(ft.SnackBar(ft.Text("Student status updated successfully.")))
                page.close(modal_dialog)
                load_students()
            except Exception as ex:
                page.open(ft.SnackBar(ft.Text(f"Failed to update status: {str(ex)}")))

        # Document list component
        doc_list = ft.Column(spacing=6)
        if not docs:
            doc_list.controls.append(ft.Text("No documents uploaded yet.", size=11, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED))
        else:
            for d in docs:
                doc_id = d["id"]
                
                # Document status buttons
                def update_doc_status(e, did=doc_id, s="approved"):
                    execute_query("UPDATE documents SET status = ? WHERE id = ?", (s, did))
                    page.open(ft.SnackBar(ft.Text(f"Document status marked as {s}.")))
                    # Refresh modal view by closing and opening it again (simplest reactive loop)
                    page.close(modal_dialog)
                    open_student_modal(student_id)

                doc_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.INSERT_DRIVE_FILE, color=ThemeColors.PRIMARY, size=16),
                            ft.Text(d["original_name"], size=12, expand=True, overflow=ft.TextOverflow.ELLIPSIS, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                            StatusBadge(d["status"]),
                            ft.Row([
                                ft.IconButton(ft.icons.CHECK, icon_color=ThemeColors.SUCCESS, icon_size=16, tooltip="Approve Document", on_click=lambda e: update_doc_status(e, s="approved")),
                                ft.IconButton(ft.icons.CLOSE, icon_color=ThemeColors.DANGER, icon_size=16, tooltip="Reject Document", on_click=lambda e: update_doc_status(e, s="rejected")),
                            ], spacing=2)
                        ], alignment=ft.MainAxisAlignment.BETWEEN),
                        padding=6,
                        bgcolor=ft.colors.with_opacity(0.02, ft.colors.WHITE if is_dark else ft.colors.BLACK),
                        border_radius=6,
                    )
                )

        modal_content = ft.Column(
            controls=[
                ft.Row([
                    ft.Column([
                        ft.Text(f"{student['firstname']} {student['lastname']}", size=20, weight=ft.FontWeight.BLACK, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                        ft.Text(f"Email: {student['email']} • Phone: {student['phone']}", size=11, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                        ft.Text(f"Student ID: {student['student_id'] or 'N/A'} • Location: {student['location'] or 'N/A'}", size=11, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                    ], spacing=2, expand=True)
                ], spacing=10),
                ft.Divider(height=10, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
                ft.Text("Biography", size=12, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                ft.Text(student["bio"] or "No biography provided.", size=12, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                ft.Divider(height=10, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
                ft.Text("Uploaded Files vault", size=12, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                doc_list,
                ft.Divider(height=15, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
                ft.Row([
                    status_select,
                    ft.ElevatedButton("Update Status", on_click=save_status_change, bgcolor=ThemeColors.PRIMARY, color=ft.colors.WHITE, height=40)
                ], alignment=ft.MainAxisAlignment.BETWEEN)
            ],
            spacing=12,
            tight=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            width=500,
        )

        modal_dialog = ft.AlertDialog(
            content=modal_content,
            actions=[
                ft.TextButton("Close", on_click=lambda _: page.close(modal_dialog))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.open(modal_dialog)

    def load_students():
        students_grid.controls.clear()
        
        # Build parameterized SQL search (fixes SQL Injection vulnerability in Step 1)
        base_query = """
        SELECT id, firstname, lastname, email, student_id, status, created_at
        FROM users
        WHERE role = 'student'
        """
        params = []

        if search_query:
            base_query += " AND (firstname LIKE ? OR lastname LIKE ? OR email LIKE ? OR student_id LIKE ?)"
            like_val = f"%{search_query}%"
            params.extend([like_val, like_val, like_val, like_val])

        if status_filter != "All":
            base_query += " AND status = ?"
            params.append(status_filter.lower().replace(" ", "_"))

        base_query += " ORDER BY created_at DESC"
        students = fetch_all(base_query, tuple(params))

        if not students:
            students_grid.controls.append(
                EmptyState(
                    ft.icons.SEARCH_OFF_OUTLINED,
                    "No Matching Students",
                    "Try refining your search text or removing the status filter.",
                    is_dark=is_dark
                )
            )
        else:
            # Grid Headers
            students_grid.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text("Student Details", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=3),
                        ft.Text("Student ID", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=1),
                        ft.Text("Status", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=1),
                        ft.Text("Action", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=1, text_align=ft.TextAlign.RIGHT),
                    ]),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)))
                )
            )

            # Rows
            for s in students:
                sid = s["id"]
                fullname = f"{s['firstname']} {s['lastname']}"
                row_controls = ft.Row([
                    ft.Column([
                        ft.Text(fullname, size=13, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                        ft.Text(s["email"], size=11, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                    ], spacing=2, expand=3),
                    ft.Text(s["student_id"] or "N/A", size=12, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT, expand=1),
                    StatusBadge(s["status"]),
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.VISIBILITY_OUTLINED,
                            icon_color=ThemeColors.PRIMARY,
                            icon_size=18,
                            tooltip="Review Profile & Files",
                            on_click=lambda e, sid=sid: open_student_modal(sid),
                        )
                    ], expand=1, alignment=ft.MainAxisAlignment.END)
                ], alignment=ft.MainAxisAlignment.BETWEEN)

                students_grid.controls.append(
                    ft.Container(
                        content=row_controls,
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        border_radius=8,
                        hover_color=ft.colors.with_opacity(0.02, ThemeColors.PRIMARY),
                    )
                )
        page.update()

    load_students()

    search_row = ft.Row([search_input, filter_dropdown], spacing=16)

    students_card = ft.Container(
        content=ft.Column([
            search_row,
            ft.Divider(height=10, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
            students_grid,
        ], spacing=14),
        padding=24,
        expand=True,
        **style
    )

    layout = ft.Container(
        content=ft.Column([
            header,
            students_card,
        ], spacing=16),
        padding=30,
        expand=True,
    )

    return layout
