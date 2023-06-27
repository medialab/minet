from playwright.async_api import Page, BrowserContext


class PageContextManager:
    def __init__(self, page: Page):
        self.page = page

    async def __aenter__(self) -> Page:
        return self.page

    async def __aexit__(self, *args):
        await self.page.close()


class BrowserContextContextManager:
    def __init__(self, context: BrowserContext) -> None:
        self.context = context

    async def __aenter__(self) -> BrowserContext:
        return self.context

    async def __aexit__(self, *args):
        await self.context.close()
