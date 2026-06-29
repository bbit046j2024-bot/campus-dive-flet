import flet as ft
from components.theme import ThemeColors, glass_card_style

class StatusBadge(ft.Container):
    """Pill badge indicating application or document status with custom colors."""
    def __init__(self, status):
        status = (status or "pending").lower()
        
        # Color mapping based on status
        colors = {
            "submitted": (ft.colors.BLUE_400, ft.colors.BLUE_900),
            "pending": (ft.colors.ORANGE_400, ft.colors.ORANGE_900),
            "documents_uploaded": (ft.colors.PURPLE_400, ft.colors.PURPLE_900),
            "under_review": (ft.colors.AMBER_400, ft.colors.AMBER_900),
            "interview_scheduled": (ft.colors.TEAL_400, ft.colors.TEAL_900),
            "approved": (ft.colors.GREEN_400, ft.colors.GREEN_900),
            "rejected": (ft.colors.RED_400, ft.colors.RED_900),
            "active": (ft.colors.GREEN_400, ft.colors.GREEN_900),
            "archived": (ft.colors.GREY_400, ft.colors.GREY_900),
        }
        
        text_color, bg_color = colors.get(status, (ft.colors.GREY_400, ft.colors.GREY_900))
        label_text = status.replace("_", " ").title()

        super().__init__(
            content=ft.Text(label_text, color=text_color, size=11, weight=ft.FontWeight.BOLD),
            bgcolor=ft.colors.with_opacity(0.15, bg_color),
            border=ft.border.all(1, ft.colors.with_opacity(0.3, text_color)),
            border_radius=ft.border_radius.all(12),
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
            alignment=ft.alignment.center,
        )

class UserAvatar(ft.Container):
    """Initials-based colored user avatar."""
    def __init__(self, firstname, lastname, size=40):
        initials = ""
        if firstname:
            initials += firstname[0].upper()
        if lastname:
            initials += lastname[0].upper()
        if not initials:
            initials = "U"
            
        # Determine background color based on name characters
        char_sum = sum(ord(c) for c in (firstname + lastname)) if (firstname or lastname) else 0
        bg_colors = [
            ft.colors.INDIGO_600,
            ft.colors.PURPLE_600,
            ft.colors.DEEP_PURPLE_600,
            ft.colors.BLUE_600,
            ft.colors.TEAL_600,
            ft.colors.AMBER_600,
        ]
        avatar_bg = bg_colors[char_sum % len(bg_colors)]

        super().__init__(
            content=ft.Text(initials, color=ft.colors.WHITE, size=size * 0.4, weight=ft.FontWeight.BOLD),
            bgcolor=avatar_bg,
            width=size,
            height=size,
            border_radius=ft.border_radius.all(size / 2),
            alignment=ft.alignment.center,
        )

class StatCard(ft.Container):
    """Premium glassmorphic statistic card for dashboards."""
    def __init__(self, title, value, icon, color=ThemeColors.PRIMARY, is_dark=True):
        style = glass_card_style(is_dark)
        
        super().__init__(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(icon, color=color, size=24),
                        bgcolor=ft.colors.with_opacity(0.1, color),
                        padding=12,
                        border_radius=12,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(title, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, size=12, weight=ft.FontWeight.W_500),
                            ft.Text(str(value), color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT, size=24, weight=ft.FontWeight.W_900),
                        ],
                        spacing=2,
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            padding=16,
            expand=True,
            **style
        )

class EmptyState(ft.Container):
    """Centered empty state placeholder with an icon, title, and descriptive message."""
    def __init__(self, icon, title, message, action_btn=None, is_dark=True):
        controls = [
            ft.Container(
                content=ft.Icon(icon, color=ThemeColors.PRIMARY_LIGHT if is_dark else ThemeColors.PRIMARY, size=40),
                bgcolor=ft.colors.with_opacity(0.1, ThemeColors.PRIMARY),
                padding=20,
                border_radius=ft.border_radius.all(28),
                alignment=ft.alignment.center,
            ),
            ft.Text(title, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT, size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(message, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, size=13, text_align=ft.TextAlign.CENTER),
        ]
        if action_btn:
            controls.append(ft.Container(content=action_btn, margin=ft.margin.only(top=10)))

        super().__init__(
            content=ft.Column(
                controls=controls,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                tight=True,
            ),
            alignment=ft.alignment.center,
            padding=40,
        )

class ProgressTracker(ft.Container):
    """Interactive visual pipeline indicator for recruitment stages."""
    def __init__(self, current_status, is_dark=True):
        stages = [
            ("submitted", "Submitted"),
            ("documents_uploaded", "Documents"),
            ("under_review", "Under Review"),
            ("interview_scheduled", "Interview"),
            ("approved", "Outcome")  # Could be approved or rejected
        ]
        
        current_status = current_status.lower() if current_status else "submitted"
        if current_status == "rejected":
            stages[-1] = ("rejected", "Rejected")
        elif current_status == "approved":
            stages[-1] = ("approved", "Approved")
        elif current_status == "pending":
            current_status = "submitted"
            
        # Determine active index
        active_idx = 0
        for i, (slug, _) in enumerate(stages):
            if slug == current_status:
                active_idx = i
                break
        
        # If status is intermediate or not matched, try some rules
        if current_status == "interview_scheduled":
            active_idx = 3
        elif current_status in ("approved", "rejected"):
            active_idx = 4
            
        step_controls = []
        for i, (slug, label) in enumerate(stages):
            is_done = i < active_idx
            is_current = i == active_idx
            
            circle_color = ThemeColors.PRIMARY if (is_done or is_current) else (ThemeColors.DARK_SURFACE_LIGHT if is_dark else ThemeColors.LIGHT_SURFACE_LIGHT)
            if is_current and current_status == "rejected":
                circle_color = ThemeColors.DANGER
            elif (is_done or is_current) and current_status == "approved":
                circle_color = ThemeColors.SUCCESS
                
            icon = ft.Icons.CHECK if is_done else (ft.Icons.HOURGLASS_EMPTY if is_current else ft.Icons.RADIO_BUTTON_UNCHECKED)
            if is_current and current_status == "rejected":
                icon = ft.Icons.CLOSE
                
            circle = ft.Container(
                content=ft.Icon(icon, size=14, color=ft.colors.WHITE if (is_done or is_current) else (ThemeColors.DARK_TEXT_FAINT if is_dark else ThemeColors.LIGHT_TEXT_FAINT)),
                bgcolor=circle_color,
                width=28,
                height=28,
                border_radius=14,
                alignment=ft.alignment.center,
                animate=200,
            )
            
            lbl = ft.Text(
                label,
                size=11,
                color=ThemeColors.DARK_TEXT if is_current else (ThemeColors.DARK_TEXT_MUTED if is_done else ThemeColors.DARK_TEXT_FAINT),
                weight=ft.FontWeight.BOLD if is_current else ft.FontWeight.NORMAL,
            )
            
            step_controls.append(
                ft.Column(
                    controls=[circle, lbl],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=6,
                )
            )
            
            # Add connector line
            if i < len(stages) - 1:
                line_color = ThemeColors.PRIMARY if i < active_idx else (ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)
                if i < active_idx and current_status == "approved":
                    line_color = ThemeColors.SUCCESS
                
                step_controls.append(
                    ft.Container(
                        bgcolor=line_color,
                        height=2,
                        width=60,
                        margin=ft.margin.only(top=13),
                        animate=200,
                    )
                )

        super().__init__(
            content=ft.Row(
                controls=step_controls,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=0,
            ),
            padding=20,
            border_radius=16,
            bgcolor=ft.colors.with_opacity(0.02, ft.colors.WHITE) if is_dark else ft.colors.with_opacity(0.02, ft.colors.BLACK),
            border=ft.border.all(1, ft.colors.with_opacity(0.05, ft.colors.WHITE) if is_dark else ft.colors.with_opacity(0.05, ft.colors.BLACK)),
        )

class PageHeader(ft.Column):
    """Header element containing the section title and descriptive subtitle."""
    def __init__(self, title, subtitle, is_dark=True):
        super().__init__(
            controls=[
                ft.Text(
                    title,
                    size=28,
                    weight=ft.FontWeight.W_900,
                    color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT,
                ),
                ft.Text(
                    subtitle,
                    size=13,
                    color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED,
                ),
                ft.Divider(height=24, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
            ],
            spacing=4,
            tight=True,
        )
