import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.widgets import PageHeader, EmptyState, UserAvatar
from database import fetch_all, fetch_one, execute_query

def show_social_feed(page: ft.Page, user: dict):
    """Renders the global social hub feed with media sharing, comments, and likes."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)
    my_id = user["id"]

    header = PageHeader(
        title="Social Hub",
        subtitle="Share updates, links, and discuss campus topics with other members.",
        is_dark=is_dark
    )

    feed_list = ft.Column(spacing=16, expand=True)

    # 1. Compose post card fields
    post_input = ft.TextField(
        placeholder="What's on your mind?",
        multiline=True,
        min_lines=2,
        max_lines=4,
        border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER,
        text_size=13,
    )
    
    media_input = ft.TextField(
        placeholder="Image or media URL (Optional)",
        prefix_icon=ft.icons.LINK,
        border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER,
        text_size=12,
    )

    def submit_post(e):
        txt = post_input.value.strip()
        media = media_input.value.strip() or None
        
        if not txt:
            page.open(ft.SnackBar(ft.Text("Post content cannot be empty.")))
            return

        try:
            execute_query("""
            INSERT INTO group_posts (user_id, content, media_url, media_type, status)
            VALUES (?, ?, ?, 'image', 'published')
            """, (my_id, txt, media))

            post_input.value = ""
            media_input.value = ""
            page.open(ft.SnackBar(ft.Text("Update posted successfully!")))
            load_feed()
        except Exception as ex:
            page.open(ft.SnackBar(ft.Text(f"Failed to post: {str(ex)}")))

    post_btn = ft.ElevatedButton(
        text="Share Post",
        icon=ft.icons.SHARE,
        bgcolor=ThemeColors.PRIMARY,
        color=ft.colors.WHITE,
        on_click=submit_post,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    compose_card = ft.Container(
        content=ft.Column([
            ft.Row([
                UserAvatar(user["firstname"], user["lastname"], size=36),
                ft.Text("Share an Update", size=14, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
            ], spacing=10),
            post_input,
            media_input,
            ft.Row([post_btn], alignment=ft.MainAxisAlignment.END)
        ], spacing=10),
        padding=16,
        **style
    )

    # 2. Feed Loader
    def load_feed():
        feed_list.controls.clear()
        
        # Select posts (excluding group specific posts for global feed)
        query = """
        SELECT gp.*, u.firstname, u.lastname,
               (SELECT COUNT(*) FROM post_likes WHERE post_id = gp.id AND user_id = ?) as has_liked
        FROM group_posts gp
        JOIN users u ON u.id = gp.user_id
        WHERE gp.group_id IS NULL AND gp.status = 'published'
        ORDER BY gp.created_at DESC
        """
        posts = fetch_all(query, (my_id,))

        if not posts:
            feed_list.controls.append(
                EmptyState(
                    ft.icons.FEED_OUTLINED,
                    "Feed is Empty",
                    "Be the first to share an update on the global campus feed!",
                    is_dark=is_dark
                )
            )
        else:
            for p in posts:
                post_id = p["id"]
                author_name = f"{p['firstname']} {p['lastname']}"
                has_liked = p["has_liked"] > 0
                
                # Expand comments container
                comments_box = ft.Column(spacing=6, visible=False)
                new_comment_input = ft.TextField(
                    placeholder="Write a comment...",
                    border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER,
                    text_size=12,
                    expand=True,
                    height=36,
                )

                def toggle_like(e, pid=post_id, liked=has_liked):
                    try:
                        if liked:
                            execute_query("DELETE FROM post_likes WHERE post_id = ? AND user_id = ?", (pid, my_id))
                            execute_query("UPDATE group_posts SET like_count = MAX(0, like_count - 1) WHERE id = ?", (pid,))
                        else:
                            execute_query("INSERT OR IGNORE INTO post_likes (post_id, user_id) VALUES (?, ?)", (pid, my_id))
                            execute_query("UPDATE group_posts SET like_count = like_count + 1 WHERE id = ?", (pid,))
                        load_feed()
                    except Exception as ex:
                        page.open(ft.SnackBar(ft.Text(f"Like toggle failed: {str(ex)}")))

                def toggle_comments(e, cb=comments_box, pid=post_id):
                    cb.visible = not cb.visible
                    if cb.visible:
                        load_comments(cb, pid)
                    page.update()

                def load_comments(cb, pid):
                    cb.controls.clear()
                    comment_rows = fetch_all("""
                        SELECT pc.*, u.firstname, u.lastname
                        FROM post_comments pc
                        JOIN users u ON u.id = pc.user_id
                        WHERE pc.post_id = ?
                        ORDER BY pc.created_at ASC
                    """, (pid,))
                    
                    for c in comment_rows:
                        cb.controls.append(
                            ft.Container(
                                content=ft.Row([
                                    UserAvatar(c["firstname"], c["lastname"], size=24),
                                    ft.Column([
                                        ft.Text(f"{c['firstname']} {c['lastname']}", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                                        ft.Text(c["content"], size=11, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                                    ], spacing=1, expand=True)
                                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START),
                                padding=ft.padding.symmetric(horizontal=8, vertical=6),
                                bgcolor=ft.colors.with_opacity(0.01, ft.colors.WHITE if is_dark else ft.colors.BLACK),
                                border_radius=6,
                            )
                        )
                    
                    # Add comment box
                    def post_comment(ev, c_input=new_comment_input, pid=pid, cb_ref=cb):
                        c_txt = c_input.value.strip()
                        if not c_txt:
                            return
                        try:
                            execute_query("INSERT INTO post_comments (post_id, user_id, content) VALUES (?, ?, ?)", (pid, my_id, c_txt))
                            execute_query("UPDATE group_posts SET comment_count = comment_count + 1 WHERE id = ?", (pid,))
                            c_input.value = ""
                            load_comments(cb_ref, pid)
                            load_feed() # reload stats counts on cards
                        except Exception as ex:
                            page.open(ft.SnackBar(ft.Text(f"Comment failed: {str(ex)}")))

                    cb.controls.append(
                        ft.Row([
                            new_comment_input,
                            ft.IconButton(
                                icon=ft.icons.SEND,
                                icon_color=ThemeColors.PRIMARY,
                                icon_size=16,
                                on_click=post_comment,
                            )
                        ], spacing=6)
                    )
                    page.update()

                # Card items
                card_items = [
                    ft.Row([
                        UserAvatar(p["firstname"], p["lastname"], size=36),
                        ft.Column([
                            ft.Text(author_name, size=13, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                            ft.Text(p["created_at"], size=10, color=ThemeColors.DARK_TEXT_FAINT if is_dark else ThemeColors.LIGHT_TEXT_FAINT),
                        ], spacing=1)
                    ], spacing=10),
                    ft.Text(p["content"], size=13, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT, selectable=True),
                ]

                # Optional Media Image Preview
                if p["media_url"]:
                    card_items.append(
                        ft.Container(
                            content=ft.Image(
                                src=p["media_url"],
                                fit=ft.ImageFit.COVER,
                                border_radius=8,
                            ),
                            max_height=200,
                            border_radius=8,
                            alignment=ft.alignment.center,
                        )
                    )

                card_items.append(ft.Divider(height=1, color=ft.colors.with_opacity(0.05, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)))
                
                # Action links
                like_icon = ft.icons.FAVORITE if has_liked else ft.icons.FAVORITE_BORDER
                like_color = ThemeColors.DANGER if has_liked else (ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED)

                card_items.append(
                    ft.Row([
                        ft.Row([
                            ft.IconButton(like_icon, icon_color=like_color, icon_size=18, on_click=toggle_like),
                            ft.Text(str(p["like_count"]), size=12, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                        ], spacing=4),
                        ft.Row([
                            ft.IconButton(ft.icons.COMMENT_OUTLINED, icon_color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, icon_size=18, on_click=toggle_comments),
                            ft.Text(str(p["comment_count"]), size=12, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                        ], spacing=4),
                    ], spacing=16)
                )
                
                card_items.append(comments_box)

                feed_list.controls.append(
                    ft.Container(
                        content=ft.Column(card_items, spacing=10),
                        padding=16,
                        **style
                    )
                )
        page.update()

    load_feed()

    layout = ft.Container(
        content=ft.Column([
            header,
            ft.Row([
                ft.Column([
                    compose_card,
                    ft.Container(height=10),
                    feed_list
                ], spacing=10, expand=True)
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START, spacing=16)
        ], spacing=16, scroll=ft.ScrollMode.ADAPTIVE),
        padding=30,
        expand=True,
    )

    return layout
