import functools
from logging import log, debug
from playwright.async_api import async_playwright, Playwright, Browser, Page, Locator
import asyncio
import random
from typing import List

from .config import *


def indent():
    return int(random.random()*5)+1


js = """
        Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
        """
conf = [{"num": 1, "cart": "dx", "bili": [50, 50]},
        {"num": 2, "cart": "dx", "bili": [15, 25, 35, 25]},
        {"num": 3, "cart": "dx", "bili": [30, 70]},
        {"num": 4, "cart": "dx", "bili": [15, 30, 30, 15, 5, 5]},
        {"num": 5, "cart": "dx", "bili": [25, 35, 25, 15]},
        {"num": 6, "cart": "dx", "bili": [25, 35, 27, 13]},
        {"num": 7, "cart": "dx", "bili": [40, 55, 5]},
        {"num": 8, "cart": "dx", "bili": [60, 40]},
        {"num": 9, "cart": "duoxuan", "bili": [
            15, 15, 35, 15, 80, 25, 25]},
        {"num": 10, "cart": "duoxuan", "bili": [60, 50, 50, 30, 5]},
        {"num": 11, "cart": "duoxuan", "bili": [
            60, 50, 50, 30, 50, 30, 20, 5]},
        {"num": 12, "cart": "duoxuan", "bili": [60, 30, 10, 50, 5]},
        {"num": 13, "cart": "dx", "bili": [40, 55, 3, 2]},
        {"num": 14, "cart": "dx", "bili": [45, 25, 10, 20]},
        {"num": 15, "cart": "dx", "bili": [10, 50, 40, 0]},
        {"num": 16, "cart": "duoxxuan",
         "bili": [10, 80, 10, 80, 5, 10, 5]},
        {"num": 17, "cart": "dx", "bili": [40, 5, 30, 25]},
        ]


async def main():
    async with async_playwright() as p:
        # iphone_11 = p.devices['iPhone 11 Pro']
        # context = await browser.new_context(
        #     **iphone_11,
        #     locale='zh-CN',
        #     geolocation={'longitude': 120.492507, 'latitude': 28.889938},
        #     permissions=['geolocation'],
        #     color_scheme='dark',
        # )
        # page = await browser.new_page()
        n = 10
        while n:
            await sim_bro(p)
            n -= 1


def wrapper_sam(sam: asyncio.Semaphore):
    def wrapper(func):
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            async with sam:
                try:
                    await func(*args, **kwargs)
                except Exception as e:
                    print(e.args)
        return inner
    return wrapper


async def sim_bro(p: "Playwright"):
    # proxyIp = requests.get(proxyUrl).json()["proxy"]
    # print(proxyIp)
    # ,proxy={"server": "http://39.105.95.187:443"47.112.167.85:80, }
    # proxy_list=["222.249.173.24:84","39.105.95.187:443","47.112.167.85:80"]
    # , proxy={"server": f"http://130.41.41.175:8080", }
    async with await p.chromium.launch(headless=False) as browser:
        task = []
        for i in range(20):
            task.append(asyncio.create_task(sim_page(await browser.new_context())))
        await asyncio.gather(*task)


sam = asyncio.Semaphore(10)


@wrapper_sam(sam)
async def sim_page(b: "Browser"):
    async with await b.new_page() as page:
        await page.add_init_script(js)
        await page.goto(url, timeout=100000)

        # 处理问题
        for cart in conf:
            locator = page.locator(f"#div{cart['num']}")
            # print(cart['num'])
            if cart["cart"] == "dx":
                await danxuan(locator, cart["bili"])
            else:
                await duoxuan(locator, cart["bili"])
        # 过验证
        await pass_check(page)


async def danxuan(part: "Locator", bili: "List"):
    random_i = random.randint(0, 99)
    sum = 0
    choice = 0
    for i in bili:
        sum += i
        if random_i < sum:
            break
        choice += 1
    await part.locator("div[class=ui-radio]").nth(choice).click()
    await asyncio.sleep(indent())


async def duoxuan(part: "Locator", bili: "List"):
    locator = part.locator("div[class=ui-checkbox]")
    clicked = 0
    choice_count = await locator.count()
    for i in range(choice_count):
        if random.randint(0, 99) < bili[i]:
            await locator.nth(i-clicked).click()
            clicked += 1
    if clicked == 0:
        await locator.nth(random.randint(0, choice_count-1)).click()
    await asyncio.sleep(indent())


async def pass_check(page: "Page"):
    await page.locator("#ctlNext").click()
    await asyncio.sleep(4)
    if page.url != url:
        return
    if await page.locator("#alert_box").count() != 0:
        debug("智能验证对话框")
        await page.locator("text=确认").click()

    await page.locator("#SM_TXT_1").click(force=True)
    await asyncio.sleep(4)
    #         while True:
    #             dom = await page.content()
    #             if '点击按钮开始智能验证' in dom:
    #                 await page.locator("#SM_TXT_1").click(force=True)
    #                 await asyncio.sleep(4)
    #             else:
    #                 break
    if await page.locator("#SM_POP_1").count() != 0:
        debug("发现滑块")
        selector = "#nc_1_n1z"
        await page.drag_and_drop(selector, selector, force=True,
                                 target_position={"x": 400, "y": 0})
        await asyncio.sleep(2)
        if await page.locator("#SM_POP_1").count() != 0:
            debug("滑块失败，重试")
            await page.locator("#nc_1_refresh1").click()
            await page.drag_and_drop(selector, selector, force=True,
                                     target_position={"x": 400, "y": 0})
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
