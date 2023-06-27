from playwright.async_api import Page


class PageContextManager:
    def __init__(self, page: Page):
        self.page = page

    async def __aenter__(self) -> Page:
        return self.page

    async def __aexit__(self, *args):
        await self.page.close()
