import flet as ft

def main(page: ft.Page):
    print("Page session type:", type(page.session))
    print("Page session attributes:", dir(page.session))
    try:
        print("Page session.store:", page.session.store)
        print("Page session.store attributes:", dir(page.session.store))
    except Exception as e:
        print("Error getting session.store:", e)
    page.window.close()

if __name__ == "__main__":
    ft.app(target=main)
