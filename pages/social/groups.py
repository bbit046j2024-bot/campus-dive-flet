import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.widgets import PageHeader, EmptyState
from database import fetch_all, fetch_one, execute_query

def show_social_groups(page: ft.Page, user: dict):
    """Renders the community groups directory panel with search and membership controls."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)
    my_id = user["id"]

    header = PageHeader(
        title="Campus Groups",
        subtitle="Browse existing interest circles, join communities, or create a new social group.",
        is_dark=is_dark
    )

    groups_grid = ft.Row(wrap=True, spacing=16, alignment=ft.MainAxisAlignment.START)

    def load_groups():
        groups_grid.controls.clear()
        
        # Select groups details (including membership status)
        query = """
        SELECT sg.*,
               (SELECT COUNT(*) FROM group_members WHERE group_id = sg.id) as member_count,
               (SELECT COUNT(*) FROM group_members WHERE group_id = sg.id AND user_id = ?) as is_member
        FROM social_groups sg
        WHERE sg.status = 'active'
        ORDER BY sg.name ASC
        """
        groups = fetch_all(query, (my_id,))

        if not groups:
            # Seed default groups if none exist yet to showcase V2 groups
            execute_query("""
            INSERT OR IGNORE INTO social_groups (name, slug, description, category, created_by)
            VALUES 
                ('Tech & Coding Hub', 'tech-coding', 'Discuss software projects, web standards, and secure coding patterns.', 'Academic', 1),
                ('Campus Sports Hub', 'campus-sports', 'Connect for football matches, gym workouts, and sports announcements.', 'Recreational', 1)
            """)
            # Auto enroll admin creator
            tech_g = fetch_one("SELECT id FROM social_groups WHERE slug = 'tech-coding'")
            sports_g = fetch_one("SELECT id FROM social_groups WHERE slug = 'campus-sports'")
            if tech_g:
                execute_query("INSERT OR IGNORE INTO group_members (group_id, user_id, role) VALUES (?, 1, 'admin')", (tech_g["id"],))
            if sports_g:
                execute_query("INSERT OR IGNORE INTO group_members (group_id, user_id, role) VALUES (?, 1, 'admin')", (sports_g["id"],))
            
            # Reload
            groups = fetch_all(query, (my_id,))

        for g in groups:
            g_id = g["id"]
            slug = g["slug"]
            is_member = g["is_member"] > 0
            
            def handle_membership(e, group_id=g_id, member_status=is_member):
                try:
                    if member_status:
                        execute_query("DELETE FROM group_members WHERE group_id = ? AND user_id = ?", (group_id, my_id))
                        page.open(ft.SnackBar(ft.Text("You have left the group.")))
                    else:
                        execute_query("INSERT OR IGNORE INTO group_members (group_id, user_id, role) VALUES (?, ?, 'member')", (group_id, my_id))
                        page.open(ft.SnackBar(ft.Text("Successfully joined the group!")))
                    load_groups()
                except Exception as ex:
                    page.open(ft.SnackBar(ft.Text(f"Action failed: {str(ex)}")))

            action_buttons = []
            if is_member:
                action_buttons.extend([
                    ft.ElevatedButton(
                        text="View Feed",
                        icon=ft.icons.FORWARD,
                        bgcolor=ThemeColors.PRIMARY,
                        color=ft.colors.WHITE,
                        on_click=lambda e, s=slug: page.go(f"/social/group/{s}"),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                    ),
                    ft.TextButton(
                        text="Leave",
                        on_click=handle_membership,
                        style=ft.ButtonStyle(color=ThemeColors.DANGER),
                    )
                ])
            else:
                action_buttons.append(
                    ft.ElevatedButton(
                        text="Join Group",
                        icon=ft.icons.ADD,
                        bgcolor=ft.colors.with_opacity(0.1, ThemeColors.PRIMARY),
                        color=ThemeColors.PRIMARY_LIGHT if is_dark else ThemeColors.PRIMARY_DARK,
                        on_click=handle_membership,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                    )
                )

            groups_grid.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.icons.GROUP_OUTLINED, color=ThemeColors.PRIMARY, size=24),
                                ft.Container(
                                    content=ft.Text(g["category"], size=10, color=ThemeColors.PRIMARY_LIGHT if is_dark else ThemeColors.PRIMARY_DARK, weight=ft.FontWeight.BOLD),
                                    bgcolor=ft.colors.with_opacity(0.1, ThemeColors.PRIMARY),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                    border_radius=4,
                                )
                            ], alignment=ft.MainAxisAlignment.BETWEEN),
                        ),
                        ft.Text(g["name"], size=16, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                        ft.Text(g["description"] or "", size=11, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                        ft.Text(f"{g['member_count']} members", size=10, color=ThemeColors.DARK_TEXT_FAINT if is_dark else ThemeColors.LIGHT_TEXT_FAINT),
                        ft.Divider(height=1, color=ft.colors.with_opacity(0.05, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
                        ft.Row(action_buttons, alignment=ft.MainAxisAlignment.BETWEEN),
                    ], spacing=10),
                    width=290,
                    height=200,
                    padding=16,
                    **style
                )
            )
        page.update()

    def open_create_group_dialog(e):
        name_in = ft.TextField(label="Group Name", border_color=ThemeColors.PRIMARY, text_size=13)
        slug_in = ft.TextField(label="URL Slug (letters and hyphens only)", border_color=ThemeColors.PRIMARY, text_size=13)
        desc_in = ft.TextField(label="Description", border_color=ThemeColors.PRIMARY, text_size=13, multiline=True, min_lines=2)
        cat_in = ft.Dropdown(
            label="Category",
            options=[
                ft.dropdown.Option("Academic"),
                ft.dropdown.Option("Recreational"),
                ft.dropdown.Option("Career"),
                ft.dropdown.Option("General"),
            ],
            value="General",
            border_color=ThemeColors.PRIMARY,
            text_size=13,
        )

        def submit_group(ev):
            name = name_in.value.strip()
            slug = slug_in.value.strip().lower()
            desc = desc_in.value.strip()
            cat = cat_in.value

            if not name or not slug:
                page.open(ft.SnackBar(ft.Text("Name and Slug are required fields.")))
                return

            try:
                # Insert group record
                execute_query("""
                INSERT INTO social_groups (name, slug, description, category, created_by)
                VALUES (?, ?, ?, ?, ?)
                """, (name, slug, desc or None, cat, my_id))
                
                # Fetch new group ID
                g_row = fetch_one("SELECT id FROM social_groups WHERE slug = ?", (slug,))
                if g_row:
                    # Auto join creator as admin
                    execute_query("INSERT OR IGNORE INTO group_members (group_id, user_id, role) VALUES (?, ?, 'admin')", (g_row["id"], my_id))

                page.open(ft.SnackBar(ft.Text("Group created successfully!")))
                page.close(create_dialog)
                load_groups()
            except Exception as ex:
                page.open(ft.SnackBar(ft.Text(f"Failed to create group: {str(ex)}")))

        create_dialog = ft.AlertDialog(
            title=ft.Text("Create New Community Group", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                name_in,
                slug_in,
                desc_in,
                cat_in
            ], spacing=10, tight=True, width=400),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: page.close(create_dialog)),
                ft.ElevatedButton("Create", on_click=submit_group, bgcolor=ThemeColors.PRIMARY, color=ft.colors.WHITE),
            ],
        )
        page.open(create_dialog)

    load_groups()

    create_btn = ft.ElevatedButton(
        text="Create New Group",
        icon=ft.icons.ADD_CIRCLE_OUTLINE,
        bgcolor=ThemeColors.PRIMARY,
        color=ft.colors.WHITE,
        on_click=open_create_group_dialog,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    layout = ft.Container(
        content=ft.Column([
            ft.Row([
                header,
                create_btn
            ], alignment=ft.MainAxisAlignment.BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(height=1, color=ft.colors.with_opacity(0.05, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
            groups_grid
        ], spacing=16, scroll=ft.ScrollMode.ADAPTIVE),
        padding=30,
        expand=True,
    )

    return layout
