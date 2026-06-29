import flet as ft
import os
import shutil
from components.theme import ThemeColors, glass_card_style
from components.widgets import PageHeader, StatusBadge, EmptyState
from database import fetch_all, execute_query, fetch_one

# FIX #5: Use proper user data directory instead of app root
# Store uploads in user's home directory for packaged app compatibility
UPLOADS_DIR = os.path.expanduser("~/.campus_dive/uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Whitelist of allowed document formats
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def show_student_documents(page: ft.Page, user: dict):
    """Renders the document management panel with secure validation checks."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)
    user_id = user["id"]

    header = PageHeader(
        title="Document Vault",
        subtitle="Upload your Resume, Transcripts, and Certificates. Maximum file size is 5MB.",
        is_dark=is_dark
    )

    documents_list = ft.Column(spacing=10, expand=True)

    def load_documents():
        documents_list.controls.clear()
        docs = fetch_all("SELECT * FROM documents WHERE user_id = ? ORDER BY uploaded_at DESC", (user_id,))
        
        if not docs:
            documents_list.controls.append(
                EmptyState(
                    ft.icons.FOLDER_OPEN_OUTLINED,
                    "No Documents Yet",
                    "Please upload your Resume or Academic Transcripts to begin review.",
                    is_dark=is_dark
                )
            )
        else:
            # Table Header
            grid_cols = ft.Row(
                controls=[
                    ft.Text("Document Name", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=3),
                    ft.Text("Size", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=1),
                    ft.Text("Status", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=1),
                    ft.Text("Actions", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=1, text_align=ft.TextAlign.RIGHT),
                ],
                alignment=ft.MainAxisAlignment.BETWEEN,
            )
            documents_list.controls.append(
                ft.Container(
                    content=grid_cols,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)))
                )
            )

            # Table Rows
            for d in docs:
                file_size_kb = f"{d['file_size'] / 1024:.1f} KB"
                
                # Delete handler with ownership verification (IDOR protection)
                def delete_doc(e, doc_id=d["id"], filename=d["filename"]):
                    try:
                        # Verify ownership in DB
                        doc_record = fetch_one("SELECT * FROM documents WHERE id = ? AND user_id = ?", (doc_id, user_id))
                        if not doc_record:
                            page.open(ft.SnackBar(ft.Text("Error: Document not found or unauthorized access.")))
                            return

                        # Safe file delete with Path Traversal protection
                        safe_filename = os.path.basename(filename)
                        filepath = os.path.abspath(os.path.join(UPLOADS_DIR, safe_filename))
                        if filepath.startswith(UPLOADS_DIR) and os.path.exists(filepath):
                            os.remove(filepath)

                        execute_query("DELETE FROM documents WHERE id = ?", (doc_id,))
                        
                        # Re-calculate student status if zero docs left
                        remaining = fetch_one("SELECT COUNT(*) as count FROM documents WHERE user_id = ?", (user_id,))
                        if not remaining or remaining["count"] == 0:
                            execute_query("UPDATE users SET status = 'submitted' WHERE id = ? AND status = 'documents_uploaded'", (user_id,))

                        page.open(ft.SnackBar(ft.Text("Document deleted successfully.")))
                        load_documents()
                    except Exception as ex:
                        page.open(ft.SnackBar(ft.Text(f"Delete failed: {str(ex)}")))

                row_controls = ft.Row(
                    controls=[
                        ft.Row([
                            ft.Icon(ft.icons.INSERT_DRIVE_FILE, color=ThemeColors.PRIMARY, size=18),
                            ft.Text(d["original_name"], size=13, weight=ft.FontWeight.W_500, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT, overflow=ft.TextOverflow.ELLIPSIS),
                        ], spacing=8, expand=3),
                        ft.Text(file_size_kb, size=12, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED, expand=1),
                        StatusBadge(d["status"]),
                        ft.Row([
                            ft.IconButton(
                                icon=ft.icons.DELETE_OUTLINE,
                                icon_color=ThemeColors.DANGER,
                                icon_size=18,
                                on_click=delete_doc,
                                tooltip="Delete Document"
                            )
                        ], expand=1, alignment=ft.MainAxisAlignment.END)
                    ],
                    alignment=ft.MainAxisAlignment.BETWEEN,
                )

                documents_list.controls.append(
                    ft.Container(
                        content=row_controls,
                        padding=ft.padding.symmetric(horizontal=12, vertical=10),
                        border_radius=8,
                        hover_color=ft.colors.with_opacity(0.02, ThemeColors.PRIMARY),
                    )
                )
        page.update()

    def on_file_selected(e: ft.FilePickerResultEvent):
        if not e.files:
            return

        selected_file = e.files[0]
        original_name = selected_file.name
        
        # 1. Path Traversal & Sanitization Protection
        # Strip directory traversal characters
        safe_name = os.path.basename(original_name)
        
        # 2. Check extension whitelist
        _, ext = os.path.splitext(safe_name.lower())
        if ext not in ALLOWED_EXTENSIONS:
            page.open(ft.SnackBar(ft.Text(f"Invalid format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")))
            return

        # 3. Check File Size Limit
        if selected_file.size > MAX_FILE_SIZE:
            page.open(ft.SnackBar(ft.Text("File exceeds maximum allowed size (5MB).")))
            return

        # 4. Resolve absolute paths to prevent traversal leaks
        dest_path = os.path.abspath(os.path.join(UPLOADS_DIR, safe_name))
        if not dest_path.startswith(UPLOADS_DIR):
            page.open(ft.SnackBar(ft.Text("Invalid destination path.")))
            return

        try:
            # FIX #12: Better error handling for file operations
            if not os.path.exists(selected_file.path):
                page.open(ft.SnackBar(ft.Text("Selected file no longer exists.")))
                return

            # Copy file from temporary picker storage to the vault directory
            shutil.copy(selected_file.path, dest_path)

            # Write document details to DB
            execute_query("""
            INSERT INTO documents (user_id, document_name, filename, original_name, file_type, file_size, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
            """, (user_id, safe_name, safe_name, original_name, ext[1:].upper(), selected_file.size))

            # Update User status to documents_uploaded if in default stage
            execute_query("""
            UPDATE users
            SET status = 'documents_uploaded'
            WHERE id = ? AND status = 'submitted'
            """, (user_id,))
            
            # Send Notification to system admins or managers
            execute_query("""
            INSERT INTO notifications (user_id, title, message, type)
            VALUES (?, 'Documents Uploaded', ?, 'info')
            """, (user_id, f"Uploaded document: {original_name}. Verification is now pending."))

            page.open(ft.SnackBar(ft.Text("Document uploaded successfully!")))
            load_documents()
        except Exception as ex:
            page.open(ft.SnackBar(ft.Text(f"Upload failed: {str(ex)}")))

    file_picker = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(file_picker)

    upload_button = ft.ElevatedButton(
        text="Upload Document",
        icon=ft.icons.UPLOAD,
        bgcolor=ThemeColors.PRIMARY,
        color=ft.colors.WHITE,
        on_click=lambda _: file_picker.pick_files(allow_multiple=False),
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    load_documents()

    documents_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row([
                    ft.Text("Vault Documents", size=16, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                    upload_button,
                ], alignment=ft.MainAxisAlignment.BETWEEN),
                ft.Divider(height=10, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
                documents_list,
            ],
            spacing=14,
        ),
        padding=24,
        expand=True,
        **style
    )

    layout = ft.Container(
        content=ft.Column(
            controls=[
                header,
                documents_card,
            ],
            spacing=16,
        ),
        padding=30,
        expand=True,
    )

    return layout
