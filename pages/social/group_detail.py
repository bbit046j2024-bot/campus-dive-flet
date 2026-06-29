import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.widgets import UserAvatar, StatusBadge, EmptyState
from database import fetch_all, fetch_one, execute_query

def show_group_detail(page: ft.Page, user: dict, group_slug: str):
    """Renders the detailed group feed, members list, and posting permissions."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)
    my_id = user["id"]

    # 1. Fetch Group Info
    group = fetch_one("SELECT * FROM social_groups WHERE slug = ?", (group_slug,))
    if not group:
        return ft.Container(content=ft.Text("Group not found.", size=16, color=ThemeColors.DANGER), padding=30)

    group_id = group["id"]
    group_name = group["name"]

    # Verify if user is member
    member_record = fetch_one("SELECT * FROM group_members WHERE group_id = ? AND user_id = ?", (group_id, my_id))
    is_member = member_record is not None

    if not is_member:
        return ft.Container(
            content=ft.Column([
                ft.Text("Access Denied", size=20, weight=ft.FontWeight.BOLD, color=ThemeColors.DANGER),
                ft.Text("You must join this group before you can view its feed and members.", size=13),
                ft.ElevatedButton("Back to Groups", on_click=lambda _: page.go("/social/groups"), bgcolor=ThemeColors.PRIMARY, color=ft.colors.WHITE)
            ], spacing=10),
            padding=30
        )

    # UI controls
    group_feed_list = ft.Column(spacing=12, expand=True)
    members_list = ft.Column(spacing=8, expand=True)

    post_input = ft.TextField(
        hint_text=f"Post something to {group_name}...",
        multiline=True,
        min_lines=2,
        border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER,
        text_size=13,
    )

    def submit_group_post(e):
        txt = post_input.value.strip()
        if not txt:
            return
        try:
            execute_query("""
            INSERT INTO group_posts (user_id, group_id, content, status)
            VALUES (?, ?, ?, 'published')
            """, (my_id, group_id, txt))

            post_input.value = ""
            page.open(ft.SnackBar(ft.Text("Post shared inside group.")))
            load_group_feed()
        except Exception as ex:
            page.open(ft.SnackBar(ft.Text(f"Post failed: {str(ex)}")))

    post_btn = ft.ElevatedButton(
        text="Post to Group",
        icon=ft.Icons.SEND,
        bgcolor=ThemeColors.PRIMARY,
        color=ft.colors.WHITE,
        on_click=submit_group_post,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    group_post_composer = ft.Container(
        content=ft.Column([
            post_input,
            ft.Row([post_btn], alignment=ft.MainAxisAlignment.END)
        ], spacing=10),
        padding=16,
        **style
    )

    def load_group_feed():
        group_feed_list.controls.clear()
        
        # Fetch group specific posts (Optimized with Joins)
        posts = fetch_all("""
            SELECT gp.*, u.firstname, u.lastname,
                   (SELECT COUNT(*) FROM post_likes WHERE post_id = gp.id AND user_id = ?) as has_liked
            FROM group_posts gp
            JOIN users u ON u.id = gp.user_id
            WHERE gp.group_id = ? AND gp.status = 'published'
            ORDER BY gp.created_at DESC
        """, (my_id, group_id))

        if not posts:
            group_feed_list.controls.append(
                EmptyState(
                    ft.Icons.FEED_OUTLINED,
                    "No Group Posts",
                    "Start the discussion by sharing the first post in this group!",
                    is_dark=is_dark
                )
            )
        else:
            for p in posts:
                pid = p["id"]
                author_name = f"{p['firstname']} {p['lastname']}"
                has_liked = p["has_liked"] > 0

                # Expand comments container
                comments_box = ft.Column(spacing=6, visible=False)
                new_comment_input = ft.TextField(
                    hint_text="Write a comment...",
                    border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER,
                    text_size=11,
                    expand=True,
                    height=32,
                )

                def toggle_like(e, post_id=pid, liked=has_liked):
                    if liked:
                        execute_query("DELETE FROM post_likes WHERE post_id = ? AND user_id = ?", (post_id, my_id))
                        execute_query("UPDATE group_posts SET like_count = MAX(0, like_count - 1) WHERE id = ?", (post_id,))
                    else:
                        execute_query("INSERT OR IGNORE INTO post_likes (post_id, user_id) VALUES (?, ?)", (post_id, my_id))
                        execute_query("UPDATE group_posts SET like_count = like_count + 1 WHERE id = ?", (post_id,))
                    load_group_feed()

                def toggle_comments(e, cb=comments_box, post_id=pid):
                    cb.visible = not cb.visible
                    if cb.visible:
                        load_comments(cb, post_id)
                    page.update()

                def load_comments(cb, post_id):
                    cb.controls.clear()
                    comment_rows = fetch_all("""
                        SELECT pc.*, u.firstname, u.lastname
                        FROM post_comments pc
                        JOIN users u ON u.id = pc.user_id
                        WHERE pc.post_id = ?
                        ORDER BY pc.created_at ASC
                    """, (post_id,))
                    
                    for c in comment_rows:
                        cb.controls.append(
                            ft.Row([
                                UserAvatar(c["firstname"], c["lastname"], size=20),
                                ft.Column([
                                    ft.Text(f"{c['firstname']} {c['lastname']}", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                                    ft.Text(c["content"], size=11, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                                ], spacing=1, expand=True)
                            ], spacing=6)
                        )
                    
                    def add_comment(ev, c_input=new_comment_input, post_id=post_id, cb_ref=cb):
                        c_txt = c_input.value.strip()
                        if not c_txt:
                            return
                        execute_query("INSERT INTO post_comments (post_id, user_id, content) VALUES (?, ?, ?)", (post_id, my_id, c_txt))
                        execute_query("UPDATE group_posts SET comment_count = comment_count + 1 WHERE id = ?", (post_id,))
                        c_input.value = ""
                        load_comments(cb_ref, post_id)
                        load_group_feed()

                    cb.controls.append(
                        ft.Row([
                            new_comment_input,
                            ft.IconButton(ft.Icons.SEND, icon_color=ThemeColors.PRIMARY, icon_size=14, on_click=add_comment)
                        ], spacing=6)
                    )
                    page.update()

                like_icon = ft.Icons.FAVORITE if has_liked else ft.Icons.FAVORITE_BORDER
                like_color = ThemeColors.DANGER if has_liked else (ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED)

                group_feed_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                UserAvatar(p["firstname"], p["lastname"], size=32),
                                ft.Column([
                                    ft.Text(author_name, size=13, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                                    ft.Text(p["created_at"], size=9, color=ThemeColors.DARK_TEXT_FAINT if is_dark else ThemeColors.LIGHT_TEXT_FAINT),
                                ], spacing=1)
                            ], spacing=8),
                            ft.Text(p["content"], size=13, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                            ft.Divider(height=1, color=ft.colors.with_opacity(0.05, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
                            ft.Row([
                                ft.Row([
                                    ft.IconButton(like_icon, icon_color=like_color, icon_size=16, on_click=toggle_like),
                                    ft.Text(str(p["like_count"]), size=11, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                                ], spacing=2),
                                ft.Row([
                                    ft.IconButton(ft.Icons.COMMENT_OUTLINED, icon_color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, icon_size=16, on_click=toggle_comments),
                                    ft.Text(str(p["comment_count"]), size=11, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                                ], spacing=2),
                            ], spacing=12),
                            comments_box
                        ], spacing=8),
                        padding=12,
                        **style
                    )
                )
        page.update()

    def load_group_members():
        members_list.controls.clear()
        
        # Fetch group members
        m_rows = fetch_all("""
            SELECT gm.*, u.firstname, u.lastname, u.email
            FROM group_members gm
            JOIN users u ON u.id = gm.user_id
            WHERE gm.group_id = ?
            ORDER BY gm.joined_at ASC
        """, (group_id,))

        for m in m_rows:
            members_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        UserAvatar(m["firstname"], m["lastname"], size=30),
                        ft.Column([
                            ft.Text(f"{m['firstname']} {m['lastname']}", size=12, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                            ft.Text(m["email"], size=10, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                        ], spacing=1, expand=True),
                        ft.Container(
                            content=ft.Text(m["role"].upper(), size=9, color=ThemeColors.PRIMARY_LIGHT if is_dark else ThemeColors.PRIMARY_DARK, weight=ft.FontWeight.BOLD),
                            bgcolor=ft.colors.with_opacity(0.1, ThemeColors.PRIMARY),
                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            border_radius=4,
                        )
                    ], spacing=10),
                    padding=6,
                    border_radius=8,
                )
            )
        page.update()

    # 4. Tab selection structure
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Group Discussion",
                icon=ft.Icons.FEED_OUTLINED,
                content=ft.Column([
                    group_post_composer,
                    ft.Container(height=10),
                    group_feed_list
                ], spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
            ),
            ft.Tab(
                text="Members Roster",
                icon=ft.Icons.PEOPLE_OUTLINED,
                content=ft.Column([
                    members_list
                ], spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
            )
        ],
        on_change=lambda e: load_group_members() if e.control.selected_index == 1 else load_group_feed()
    )

    # Load initial tab data
    load_group_feed()

    # Layout compilation
    group_header = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, icon_color=ThemeColors.PRIMARY, on_click=lambda _: page.go("/social/groups")),
                ft.Text(group_name, size=22, weight=ft.FontWeight.W_900, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
            ], spacing=8),
            ft.Text(group["description"] or "", size=13, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
            ft.Divider(height=15, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
        ], spacing=6),
        padding=ft.padding.only(bottom=10)
    )

    layout = ft.Container(
        content=ft.Column([
            group_header,
            ft.Container(content=tabs, expand=True)
        ], spacing=10, expand=True),
        padding=30,
        expand=True,
    )

    return layout
