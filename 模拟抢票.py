import tempfile
from pathlib import Path
import time

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


MOCK_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>模拟票务</title>
<style>
    body { font-family: sans-serif; padding: 40px; }
    button { padding: 10px 20px; font-size: 16px; }
    button:disabled { background: #ccc; cursor: not-allowed; }
    #order-form { display: none; margin-top: 20px; }
    #result { display: none; margin-top: 20px; color: green; font-weight: bold; }
    input { display: block; margin: 8px 0; padding: 6px; }
</style>
</head>
<body>
    <h1>模拟演唱会门票</h1>
    <p>开售倒计时：<span id="countdown">3</span> 秒</p>
    <button id="buy-btn" disabled>立即购买</button>

    <div id="order-form">
        <h2>填写订单</h2>
        <input id="name" placeholder="姓名" />
        <input id="phone" placeholder="手机号" />
        <button id="submit-btn">提交订单</button>
    </div>

    <div id="result">抢票成功！</div>

    <script>
        let seconds = 3;
        const countdownEl = document.getElementById('countdown');
        const buyBtn = document.getElementById('buy-btn');
        const orderForm = document.getElementById('order-form');
        const submitBtn = document.getElementById('submit-btn');
        const result = document.getElementById('result');

        const timer = setInterval(() => {
            seconds--;
            countdownEl.textContent = seconds;
            if (seconds <= 0) {
                clearInterval(timer);
                buyBtn.disabled = false;
                countdownEl.textContent = '0';
            }
        }, 1000);

        buyBtn.addEventListener('click', () => {
            orderForm.style.display = 'block';
        });

        submitBtn.addEventListener('click', () => {
            const name = document.getElementById('name').value.trim();
            const phone = document.getElementById('phone').value.trim();
            if (!name || !phone) {
                alert('请填写姓名和手机号');
                return;
            }
            result.style.display = 'block';
        });
    </script>
</body>
</html>
"""


def create_mock_page() -> Path:
    """生成本地模拟票务页面，返回 HTML 文件路径。"""
    temp_dir = Path(tempfile.mkdtemp(prefix="ticket_demo_"))
    html_path = temp_dir / "mock_ticket.html"
    html_path.write_text(MOCK_HTML, encoding="utf-8")
    return html_path


def main():
    html_path = create_mock_page()
    url = html_path.as_uri()
    print(f"模拟页面：{url}")

    with sync_playwright() as p:
        # headless=False 可以看到浏览器操作过程；slow_mo=100 放慢动作方便观察
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()
        page.goto(url)

        try:
            # 1. 等待“立即购买”按钮变为可用
            print("等待开售...")
            page.wait_for_function(
                "() => !document.querySelector('#buy-btn').disabled",
                timeout=10000
            )
            print("开售了，点击购买")
            page.click("#buy-btn")

            # 2. 等待订单表单出现
            page.wait_for_selector("#order-form", state="visible", timeout=5000)

            # 3. 填写订单信息
            page.fill("#name", "张三")
            page.fill("#phone", "13800138000")

            # 4. 提交订单
            page.click("#submit-btn")

            # 5. 等待结果
            page.wait_for_selector("#result", state="visible", timeout=5000)
            result_text = page.inner_text("#result")
            print("页面结果：", result_text)

            # 6. 截图保存
            page.screenshot(path="result.png")
            print("截图已保存：result.png")

        except PlaywrightTimeoutError as e:
            print("操作超时：", e)

        finally:
            time.sleep(2)
            browser.close()


if __name__ == "__main__":
    main()