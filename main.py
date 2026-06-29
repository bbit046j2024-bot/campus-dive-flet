import flet as ft
import sys
import os

# Compatibility layer for Flet version differences
try:
    # Flet 0.85+ removed colors module, use Colors class instead
    if not hasattr(ft, 'colors') or ft.colors is None:
        ft.colors = ft.Colors
except (AttributeError, NameError):
    # Fallback for different Flet versions
    pass

from database import init_db
from components.theme import get_theme, ThemeColors
from components.sidebar import Sidebar

# Import views
from pages.home import show_home
from pages.about import show_about
from pages.login import show_login
from pages.register import show_register
from pages.student.dashboard import show_student_dashboard
from pages.student.documents import show_student_documents
from pages.student.settings import show_student_settings
from pages.admin.dashboard import show_admin_dashboard
from pages.admin.students import show_students_manager
from pages.admin.roles import show_roles_manager
from pages.admin.broadcast import show_broadcast_panel
from pages.admin.analytics import show_analytics_panel
from pages.messages import show_messages_page
from pages.social.feed import show_social_feed
from pages.social.groups import show_social_groups
from pages.social.group_detail import show_group_detail
from pages.social.notifications import show_notifications_panel
from pages.audit_workspace import show_audit_workspace

def main(page: ft.Page):
    # Initialize page metadata & defaults
    page.title = "Campus Dive Onboarding Portal"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = get_theme(is_dark=True)
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 900
    page.window.min_height = 650
    page.padding = 0
    page.spacing = 0

    # Initialize session store - FIX #1: Session store initialization
    if not hasattr(page, 'session') or page.session is None:
        class SessionStore:
            def __init__(self):
                self.store = {}
            def get(self, key):
                return self.store.get(key)
            def set(self, key, value):
                self.store[key] = value
            def clear(self):
                self.store.clear()
        
        class Session:
            def __init__(self):
                self.store = {}
            def get(self, key):
                return self.store.get(key)
            def set(self, key, value):
                self.store[key] = value
            def clear(self):
                self.store.clear()
        
        page.session = Session()

    # Initialize SQLite tables & seed default admin
    init_db()

    # Layout state for responsive updates
    layout_state = {
        "sidebar": None,
        "divider": None,
        "hamburger": None
    }

    def handle_resize(e):
        is_mobile = page.width < 768
        if layout_state["sidebar"]:
            layout_state["sidebar"].visible = not is_mobile
        if layout_state["divider"]:
            layout_state["divider"].visible = not is_mobile
        if layout_state["hamburger"]:
            layout_state["hamburger"].visible = is_mobile
        page.update()

    page.on_resized = handle_resize

    # Create the single main content container
    main_container = ft.Container(expand=True)
    page.add(main_container)

    def navigate(route):
        if page.drawer:
            page.drawer.open = False
        page.route = route
        page.bgcolor = ThemeColors.DARK_BG if page.theme_mode == ft.ThemeMode.DARK else ThemeColors.LIGHT_BG
        user = page.session.get("user")

        # ── 1. ROUTE GUARDS / SESSION SECURITY (Resolves CSRF/Session vulnerabilities) ──
        public_routes = ("/", "/about", "/login", "/register")
        is_public = route in public_routes

        if not user and not is_public:
            # Not logged in, redirect to login
            navigate("/login")
            return

        if user:
            role = user.get("role", "student")
            is_admin_route = route.startswith("/admin") or route == "/audit"
            is_admin_role = role in ("admin", "manager", "interviewer")
            
            # Prevent unauthorized role access to admin modules
            if is_admin_route and not is_admin_role:
                navigate("/student/dashboard")
                return

        # ── 2. VIEW BUILDER ──
        view_content = None

        # Route matching
        if route == "/":
            view_content = show_home(page)
        elif route == "/about":
            view_content = show_about(page)
        elif route == "/login":
            view_content = show_login(page)
        elif route == "/register":
            view_content = show_register(page)
        elif route == "/student/dashboard":
            view_content = show_student_dashboard(page, user)
        elif route == "/student/documents":
            view_content = show_student_documents(page, user)
        elif route == "/student/settings":
            view_content = show_student_settings(page, user)
        elif route == "/admin/dashboard":
            view_content = show_admin_dashboard(page, user)
        elif route == "/admin/students":
            view_content = show_students_manager(page, user)
        elif route == "/admin/roles":
            view_content = show_roles_manager(page, user)
        elif route == "/admin/broadcast":
            view_content = show_broadcast_panel(page, user)
        elif route == "/admin/analytics":
            view_content = show_analytics_panel(page, user)
        elif route == "/messages":
            view_content = show_messages_page(page, user)
        elif route == "/social/feed":
            view_content = show_social_feed(page, user)
        elif route == "/social/groups":
            view_content = show_social_groups(page, user)
        elif route.startswith("/social/group/"):
            group_slug = route.split("/")[-1]
            view_content = show_group_detail(page, user, group_slug)
        elif route == "/social/notifications":
            view_content = show_notifications_panel(page, user)
        elif route == "/audit":
            view_content = show_audit_workspace(page, user)
        else:
            # Fallback 404
            view_content = ft.Container(
                content=ft.Column([
                    ft.Text("404 - Page Not Found", size=24, weight=ft.FontWeight.BOLD, color=ThemeColors.DANGER),
                    ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/"))
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True
            )

        # ── 3. FRAME ASSEMBLE ──
        # If public route, render landing content directly.
        # If authed route, embed sidebar side-by-side with scroll content container.
        if is_public:
            # Clear layout state references on public pages
            layout_state["sidebar"] = None
            layout_state["divider"] = None
            layout_state["hamburger"] = None
            page.drawer = None
            main_layout = view_content
        else:
            # Sidebar callbacks
            def on_logout(ev):
                page.session.clear()  # Safely clears out all logged-in user session data
                page.go("/")          # Redirects the user back to the landing page

            def on_theme_toggle(ev):
                # FIX #7: Don't re-navigate, just update theme and refresh UI
                if page.theme_mode == ft.ThemeMode.DARK:
                    page.theme_mode = ft.ThemeMode.LIGHT
                    page.theme = get_theme(is_dark=False)
                else:
                    page.theme_mode = ft.ThemeMode.DARK
                    page.theme = get_theme(is_dark=True)
                page.update()  # Just update, don't re-navigate

            sidebar = Sidebar(
                page=page,
                active_route=route,
                user=user,
                on_logout=on_logout,
                on_theme_toggle=on_theme_toggle
            )

            # Mobile sidebar drawer copy
            drawer_sidebar = Sidebar(
                page=page,
                active_route=route,
                user=user,
                on_logout=on_logout,
                on_theme_toggle=on_theme_toggle
            )
            drawer_sidebar.width = None
            drawer_sidebar.border = None

            page.drawer = ft.NavigationDrawer(
                controls=[drawer_sidebar],
                bgcolor=ft.colors.with_opacity(0.95, ThemeColors.DARK_SURFACE) if page.theme_mode == ft.ThemeMode.DARK else ft.colors.with_opacity(0.95, ThemeColors.LIGHT_SURFACE),
            )

            def open_drawer(e):
                page.drawer.open = True
                page.drawer.update()

            hamburger_btn = ft.IconButton(
                icon=ft.Icons.MENU,
                icon_color=ThemeColors.PRIMARY,
                on_click=open_drawer,
            )

            hamburger_row = ft.Container(
                content=ft.Row(
                    controls=[
                        hamburger_btn,
                        ft.Icon(ft.Icons.EXPLORE, color=ThemeColors.PRIMARY, size=20),
                        ft.Text("Campus Dive", size=14, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if page.theme_mode == ft.ThemeMode.DARK else ThemeColors.LIGHT_TEXT),
                    ],
                    spacing=8,
                ),
                padding=ft.padding.only(left=16, top=12, right=16, bottom=4),
            )

            divider = ft.VerticalDivider(width=1, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if page.theme_mode == ft.ThemeMode.DARK else ThemeColors.LIGHT_BORDER))

            is_mobile = page.width < 768
            sidebar.visible = not is_mobile
            divider.visible = not is_mobile
            hamburger_row.visible = is_mobile

            # Store components in state so resize handler can access them
            layout_state["sidebar"] = sidebar
            layout_state["divider"] = divider
            layout_state["hamburger"] = hamburger_row

            content_column = ft.Column(
                controls=[
                    hamburger_row,
                    ft.Container(
                        content=view_content,
                        expand=True,
                    )
                ],
                spacing=0,
                expand=True,
            )

            main_layout = ft.Row(
                controls=[
                    sidebar,
                    divider,
                    content_column
                ],
                spacing=0,
                expand=True,
            )

        main_container.content = main_layout
        page.update()

    # Override navigation functions so other modules work without changes
    page.go = navigate
    page.push_route = navigate
    # FIX #8: Don't set on_route_change to avoid infinite recursion
    # page.on_route_change = lambda e: navigate(page.route)
    
    # Go to landing page initially
    navigate(page.route or "/")

if __name__ == "__main__":
    ft.app(target=main)
