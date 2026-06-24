import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.widgets import PageHeader, EmptyState, UserAvatar
from database import fetch_all, fetch_one, execute_query

def show_messages_page(page: ft.Page, user: dict):
    """Renders the modular dual-pane private messaging system."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)
    my_id = user["id"]

    header = PageHeader(
        title="Direct Message Hub",
        subtitle="Chat directly with other campus community members, recruitment managers, or students.",
        is_dark=is_dark
    )

    # State variables
    selected_partner_id = None
    selected_partner_name = "Conversation"
    
    contacts_list = ft.Column(spacing=4, scroll=ft.ScrollMode.ADAPTIVE)
    messages_timeline = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    
    message_input = ft.TextField(
        placeholder="Type a message...",
        border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER,
        focused_border_color=ThemeColors.PRIMARY,
        text_size=13,
        expand=True,
    )

    right_pane = ft.Column(spacing=10, expand=True)

    def load_contacts():
        contacts_list.controls.clear()
        
        # Select all users we've chatted with
        query = """
        SELECT DISTINCT u.id, u.firstname, u.lastname, u.email, u.role
        FROM users u
        WHERE u.id != ? AND (
            u.id IN (SELECT receiver_id FROM messages WHERE sender_id = ?) OR
            u.id IN (SELECT sender_id FROM messages WHERE receiver_id = ?)
        )
        """
        partners = fetch_all(query, (my_id, my_id, my_id))

        if not partners:
            contacts_list.controls.append(
                ft.Text("No active chats.", size=12, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, text_align=ft.TextAlign.CENTER)
            )
        else:
            for p in partners:
                pid = p["id"]
                pname = f"{p['firstname']} {p['lastname']}"
                
                # Active selection highlight
                is_active = selected_partner_id == pid
                bg = ft.colors.with_opacity(0.1, ThemeColors.PRIMARY) if is_active else ft.colors.TRANSPARENT
                
                contacts_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            UserAvatar(p["firstname"], p["lastname"], size=32),
                            ft.Column([
                                ft.Text(pname, size=13, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                                ft.Text(p["role"].title(), size=10, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                            ], spacing=1, expand=True)
                        ], spacing=8),
                        padding=8,
                        bgcolor=bg,
                        border_radius=8,
                        on_click=lambda e, partner_id=pid, partner_name=pname: select_conversation(partner_id, partner_name),
                        hover_color=ft.colors.with_opacity(0.03, ThemeColors.PRIMARY),
                    )
                )
        page.update()

    def select_conversation(partner_id, partner_name):
        nonlocal selected_partner_id, selected_partner_name
        selected_partner_id = partner_id
        selected_partner_name = partner_name
        
        load_contacts()  # Refresh contacts list highlight
        load_messages()  # Populate chat timeline
        
        # Assemble message box input layout
        right_pane.controls.clear()
        
        chat_header = ft.Row([
            UserAvatar(partner_name.split()[0], partner_name.split()[1] if len(partner_name.split()) > 1 else "", size=36),
            ft.Text(partner_name, size=15, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
        ], spacing=10)
        
        right_pane.controls.extend([
            ft.Container(
                content=chat_header,
                padding=ft.padding.only(bottom=10),
                border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)))
            ),
            ft.Container(
                content=messages_timeline,
                expand=True,
            ),
            ft.Row([
                message_input,
                ft.IconButton(
                    icon=ft.icons.SEND,
                    icon_color=ThemeColors.PRIMARY,
                    on_click=send_message,
                    tooltip="Send Message"
                )
            ], spacing=8)
        ])
        page.update()

    def load_messages():
        messages_timeline.controls.clear()
        if not selected_partner_id:
            return
            
        # Select message thread safely
        query = """
        SELECT m.*, u.firstname, u.lastname
        FROM messages m
        JOIN users u ON u.id = m.sender_id
        WHERE (m.sender_id = ? AND m.receiver_id = ?) OR (m.sender_id = ? AND m.receiver_id = ?)
        ORDER BY m.created_at ASC
        """
        msgs = fetch_all(query, (my_id, selected_partner_id, selected_partner_id, my_id))
        
        # Mark thread as read
        execute_query("UPDATE messages SET is_read = 1 WHERE sender_id = ? AND receiver_id = ?", (selected_partner_id, my_id))

        for m in msgs:
            is_me = m["sender_id"] == my_id
            align = ft.CrossAxisAlignment.END if is_me else ft.CrossAxisAlignment.START
            bubble_color = ThemeColors.PRIMARY if is_me else (ThemeColors.DARK_SURFACE_LIGHT if is_dark else ThemeColors.LIGHT_SURFACE_LIGHT)
            text_color = ft.colors.WHITE if is_me else (ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT)
            
            messages_timeline.controls.append(
                ft.Column([
                    ft.Container(
                        content=ft.Text(m["message"], color=text_color, size=13),
                        bgcolor=bubble_color,
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        border_radius=ft.border_radius.only(
                            top_left=12, top_right=12,
                            bottom_left=0 if not is_me else 12,
                            bottom_right=12 if not is_me else 0
                        ),
                        max_width=320,
                    ),
                    ft.Text(m["created_at"][-8:-3], size=9, color=ThemeColors.DARK_TEXT_FAINT if is_dark else ThemeColors.LIGHT_TEXT_FAINT)
                ], horizontal_alignment=align, spacing=2)
            )
        page.update()

    def send_message(e):
        txt = message_input.value.strip()
        if not txt or not selected_partner_id:
            return
            
        try:
            execute_query("""
            INSERT INTO messages (sender_id, receiver_id, subject, message)
            VALUES (?, ?, 'Direct Chat', ?)
            """, (my_id, selected_partner_id, txt))

            # Trigger notification to receiver
            execute_query("""
            INSERT INTO notifications (user_id, title, message, type)
            VALUES (?, 'New Message', ?, 'info')
            """, (selected_partner_id, f"Message from {user['firstname']}: {txt[:40]}..."))

            message_input.value = ""
            load_messages()
        except Exception as ex:
            page.open(ft.SnackBar(ft.Text(f"Failed to send: {str(ex)}")))

    # 3. New Chat dialog setup
    def open_new_chat_dialog(e):
        # Fetch other users in the system to start a conversation
        users = fetch_all("SELECT id, firstname, lastname, email, role FROM users WHERE id != ? ORDER BY firstname ASC", (my_id,))
        
        user_options = [ft.dropdown.Option(str(u["id"]), f"{u['firstname']} {u['lastname']} ({u['role'].title()})") for u in users]
        
        user_select = ft.Dropdown(
            label="Select Recipient",
            options=user_options,
            border_color=ThemeColors.PRIMARY,
            text_size=13,
            expand=True,
        )
        
        init_message_input = ft.TextField(
            label="Type initial message...",
            multiline=True,
            min_lines=2,
            border_color=ThemeColors.PRIMARY,
            text_size=13,
        )

        def initiate_conversation(ev):
            partner_id_str = user_select.value
            txt = init_message_input.value.strip()
            
            if not partner_id_str or not txt:
                page.open(ft.SnackBar(ft.Text("Please fill out all fields.")))
                return
                
            p_id = int(partner_id_str)
            try:
                execute_query("""
                INSERT INTO messages (sender_id, receiver_id, subject, message)
                VALUES (?, ?, 'Direct Chat', ?)
                """, (my_id, p_id, txt))

                execute_query("""
                INSERT INTO notifications (user_id, title, message, type)
                VALUES (?, 'New Message Thread', ?, 'info')
                """, (p_id, f"New conversation started by {user['firstname']}."))

                page.close(new_chat_dialog)
                # Find partner name
                p_rec = fetch_one("SELECT firstname, lastname FROM users WHERE id = ?", (p_id,))
                p_name = f"{p_rec['firstname']} {p_rec['lastname']}" if p_rec else "Member"
                
                select_conversation(p_id, p_name)
            except Exception as ex:
                page.open(ft.SnackBar(ft.Text(f"Could not start chat: {str(ex)}")))

        new_chat_dialog = ft.AlertDialog(
            title=ft.Text("New Conversation", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                user_select,
                init_message_input,
            ], spacing=10, tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: page.close(new_chat_dialog)),
                ft.ElevatedButton("Send", on_click=initiate_conversation, bgcolor=ThemeColors.PRIMARY, color=ft.colors.WHITE),
            ],
        )
        page.open(new_chat_dialog)

    # Initial Right Pane Placeholder
    right_pane.controls.append(
        EmptyState(
            ft.icons.CHAT_BUBBLE_OUTLINE,
            "No Conversation Selected",
            "Select a contact from the left list to begin messaging, or initiate a new chat thread.",
            is_dark=is_dark
        )
    )

    # Compile Layout cards
    left_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Chats", size=15, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                ft.IconButton(ft.icons.ADD_COMMENT_OUTLINED, icon_color=ThemeColors.PRIMARY, icon_size=18, on_click=open_new_chat_dialog, tooltip="Start Chat")
            ], alignment=ft.MainAxisAlignment.BETWEEN),
            ft.Divider(height=10, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
            contacts_list,
        ], spacing=10),
        padding=16,
        width=250,
        **style
    )

    right_card = ft.Container(
        content=right_pane,
        padding=16,
        expand=True,
        **style
    )

    load_contacts()

    layout = ft.Container(
        content=ft.Column([
            header,
            ft.Row([left_card, right_card], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.STRETCH, spacing=16, expand=True),
        ], spacing=16, expand=True),
        padding=30,
        expand=True,
    )

    return layout
