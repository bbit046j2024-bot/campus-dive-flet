import flet as ft
# Compatibility layer for Flet 0.85 color module removal
ft.colors = ft.Colors

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

    # Initialize SQLite tables & seed default admin
    init_db()

    # Create the single main content container
    main_container = ft.Container(expand=True)
    page.add(main_container)

    def navigate(route):
        page.route = route
        page.bgcolor = ThemeColors.DARK_BG if page.theme_mode == ft.ThemeMode.DARK else ThemeColors.LIGHT_BG
        user = page.session.store.get("user")

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
            main_layout = view_content
        else:
            # Sidebar callbacks
            def on_logout(ev):
                page.session.store.clear()
                page.go("/")

            def on_theme_toggle(ev):
                if page.theme_mode == ft.ThemeMode.DARK:
                    page.theme_mode = ft.ThemeMode.LIGHT
                    page.theme = get_theme(is_dark=False)
                else:
                    page.theme_mode = ft.ThemeMode.DARK
                    page.theme = get_theme(is_dark=True)
                navigate(page.route) # Re-navigate to refresh view colors

            sidebar = Sidebar(
                page=page,
                active_route=route,
                user=user,
                on_logout=on_logout,
                on_theme_toggle=on_theme_toggle
            )
            
            main_layout = ft.Row(
                controls=[
                    sidebar,
                    ft.VerticalDivider(width=1, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if page.theme_mode == ft.ThemeMode.DARK else ThemeColors.LIGHT_BORDER)),
                    ft.Container(
                        content=view_content,
                        expand=True,
                    )
                ],
                spacing=0,
                expand=True,
            )

        main_container.content = main_layout
        page.update()

    # Override navigation functions so other modules work without changes
    page.go = navigate
    page.push_route = navigate
    page.on_route_change = lambda e: navigate(page.route)
    
    # Go to landing page initially
    navigate(page.route or "/")

if __name__ == "__main__":
    ft.run(main)
