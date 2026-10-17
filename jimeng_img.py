# -*- coding: utf-8 -*-
"""
jimeng_img.py —— 用 requests 调用「即梦 / 豆包 Seedream」生成历史插画，并保存到本地 img 文件夹。

用途：为《辛亥革命》网页 PPT 批量生成统一风格的历史插画（16:9，写实油画风格）。

两种调用通道（--provider 选择）：
  1) ark     火山方舟（推荐，官方接口，稳定）
             POST https://ark.cn-beijing.volces.com/api/v3/images/generations
             鉴权：Authorization: Bearer <ARK_API_KEY>
             密钥来源：环境变量 ARK_API_KEY，或 --key 参数
  2) jimeng  即梦网页版（非官方，逆向接口，随时可能失效；仓库 iptag/jimeng-api 已归档）
             POST https://jimeng.jianying.com/mweb/v1/aigc_draft/generate        提交任务
             POST https://jimeng.jianying.com/mweb/v1/get_history_by_ids         轮询结果
             鉴权：网页版 Cookie 中的 sessionid（环境变量 JIMENG_SESSIONID 或 --key）
             取法：浏览器登录 jimeng.jianying.com -> F12 -> Application -> Cookies -> 复制 sessionid

常用命令：
    python jimeng_img.py --list                        # 查看全部插画提示词
    python jimeng_img.py --dry-run                     # 只打印请求体，不发网络请求
    python jimeng_img.py --self-test                   # 离线自检（不花钱、不联网）
    python jimeng_img.py                               # 用默认通道生成全部缺图
    python jimeng_img.py --only 05,07 --force          # 只重生成第 5、7 张
    python jimeng_img.py --provider jimeng --model jimeng-4.5
    python jimeng_img.py --prompt "自定义提示词" --name custom_demo

说明：脚本默认顺序生成（避免触发限流），每张之间间隔 --sleep 秒；已经存在的图片会自动跳过，
      可用于断点续跑；生成结果会写入 img/manifest.json，网页 PPT 可直接读取文件名与标题。
"""

import argparse
import base64
import hashlib
import json
import os
import random
import re
import sys
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Windows 控制台输出中文时可能出现编码告警，这里只做兜底，不改编码
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# 一、基础配置
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "img"                     # 图片输出目录
MANIFEST_PATH = IMG_DIR / "manifest.json"      # 生成清单（供网页 PPT 调用）

# --- 通道 1：火山方舟（即梦同源模型 Seedream / 豆包图片生成） ---
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
ARK_ENDPOINT = "/images/generations"
ARK_MODEL_DEFAULT = "doubao-seedream-4-0-250828"   # 4.0 支持自定义尺寸；3.0 的 ID 是 doubao-seedream-3-0-t2i-250415
ARK_SIZES_4_0 = {                                  # Seedream 4.0：宽高均在 [1024,4096] 且总像素在 [1280*720, 4096*4096]
    "16:9": "2048x1152",   # 网页 PPT 主用尺寸
    "4:3": "2304x1728",
    "1:1": "2048x2048",
    "3:4": "1728x2304",
    "9:16": "1152x2048",
}
ARK_SIZES_3_0 = {"16:9": "1280x720", "1:1": "1024x1024", "3:4": "864x1152", "9:16": "720x1280"}

# --- 通道 2：即梦网页版（逆向接口） ---
JIMENG_BASE_URL = "https://jimeng.jianying.com"
JIMENG_SUBMIT_PATH = "/mweb/v1/aigc_draft/generate"
JIMENG_HISTORY_PATH = "/mweb/v1/get_history_by_ids"
JIMENG_AID = 513695            # 国内站 appid / assistant id
JIMENG_REGION = "cn"
JIMENG_PLATFORM_CODE = "7"
JIMENG_VERSION_CODE = "8.4.0"  # Appvr
JIMENG_DA_VERSION = "3.3.9"
JIMENG_WEB_VERSION = "7.5.0"
JIMENG_DRAFT_VERSION = "3.3.9"
JIMENG_DRAFT_MIN_VERSION = "3.0.2"
# 用户模型名 -> 即梦内部模型名（来自 iptag/jimeng-api 的 IMAGE_MODEL_MAP）
JIMENG_MODEL_MAP = {
    "jimeng-5.0": "high_aes_general_v50",
    "jimeng-4.6": "high_aes_general_v42",
    "jimeng-4.5": "high_aes_general_v40l",
    "jimeng-4.1": "high_aes_general_v41",
    "jimeng-4.0": "high_aes_general_v40",
    "jimeng-3.1": "high_aes_general_v30l_art_fangzhou:general_v3.0_18b",
    "jimeng-3.0": "high_aes_general_v30l:general_v3.0_18b",
}
JIMENG_MODEL_DEFAULT = "jimeng-4.5"
# 分辨率 / 比例 -> 宽高与 image_ratio（来自 iptag/jimeng-api 的 RESOLUTION_OPTIONS）
JIMENG_RESOLUTION_OPTIONS = {
    "1k": {
        "1:1": (1024, 1024, 1), "4:3": (768, 1024, 4), "3:4": (1024, 768, 2),
        "16:9": (1024, 576, 3), "9:16": (576, 1024, 5), "3:2": (1024, 682, 7),
        "2:3": (682, 1024, 6), "21:9": (1195, 512, 8),
    },
    "2k": {
        "1:1": (2048, 2048, 1), "4:3": (2304, 1728, 4), "3:4": (1728, 2304, 2),
        "16:9": (2560, 1440, 3), "9:16": (1440, 2560, 5), "3:2": (2496, 1664, 7),
        "2:3": (1664, 2496, 6), "21:9": (3024, 1296, 8),
    },
}

# 统一画风 / 内容约束：确保 12 张插画风格一致，且不出现真实人物肖像、文字与水印
STYLE_SUFFIX = (
    "，写实主义历史油画风格，厚涂笔触，暖褐色与暗红色调，老照片般的胶片颗粒质感，"
    "伦勃朗式明暗对比光影，电影感宽幅构图，画面中人物均为远景群像或剪影，"
    "不具备可辨识的面部特征，不出现任何文字、字母、标语、旗帜文字与水印，"
    "不出现手机、汽车等现代元素，历史插画，高清细节"
)
NEGATIVE_PROMPT = (
    "文字, 字母, 标语, 水印, logo, 现代建筑, 现代服饰, 卡通, 3D 渲染, 低清, 模糊, "
    "畸形手指, 面部特写, 真实人物肖像, 血腥, 暴力特写"
)

# ---------------------------------------------------------------------------
# 二、《辛亥革命》网页 PPT 插画提示词（12 页，16:9）
#     key      : 命令行 --only 的筛选关键字（也用于文件名）
#     title    : PPT 中显示的标题
#     caption  : 图片说明，网页 PPT 可作副标题使用
# ---------------------------------------------------------------------------
PROMPTS = [
    {
        "key": "01_dawn_wuchang",
        "title": "封面 · 破晓武昌",
        "caption": "1911 年秋，武昌城头的黎明",
        "prompt": (
            "1911 年秋天的中国武昌古城，破晓时分，高大厚重的城楼与城墙轮廓剪影，"
            "长江江面薄雾与远处帆船，一列革命军士兵持枪行进的远景剪影，"
            "天边一线橙红曙光穿透云层，肃穆而充满希望的气氛"
        ),
    },
    {
        "key": "02_late_qing_crisis",
        "title": "晚清困局",
        "caption": "民族危机与专制统治下的中国",
        "prompt": (
            "清末的中国沿海，雾气笼罩的港湾里停泊着外国军舰的巨大黑色剪影，"
            "岸边古老炮台与残破城墙，破败的村落屋顶与枯树，"
            "压抑沉郁的灰褐色调，风雨欲来的天空，象征国家危亡的纪实氛围"
        ),
    },
    {
        "key": "03_huanghuagang",
        "title": "黄花岗起义",
        "caption": "1911 年 4 月，广州起义",
        "prompt": (
            "1911 年广州城狭窄的麻石巷道中，革命党人奋勇冲锋的远景群像剪影，"
            "青砖骑楼与斑驳墙面，枪火硝烟在巷道弥漫，地面散落弹壳与倒下的人影，"
            "悲壮惨烈而庄重的历史场景，逆光与浓烟形成强烈明暗对比"
        ),
    },
    {
        "key": "04_railway_protection",
        "title": "保路运动",
        "caption": "1911 年 5 月，四川保路风潮",
        "prompt": (
            "1911 年四川成都街头，成千上万民众聚集请愿，密密集集的人群剪影如潮水般拥挤，"
            "无字的素色布制长条旗在雨中低垂，青瓦木质店铺招牌与屋檐，"
            "泥泞石板路与雨雾，汹涌民意汇成洪流的震撼全景"
        ),
    },
    {
        "key": "05_wuchang_uprising",
        "title": "武昌起义第一枪",
        "caption": "1911 年 10 月 10 日夜，湖北新军工程营",
        "prompt": (
            "1911 年 10 月 10 日深夜的武昌，湖北新军工程营士兵持枪跃起的动态剪影，"
            "远处军械库燃起冲天火光与滚滚浓烟，火光映红半边夜空与青瓦营房，"
            "夜色中枪火闪光，紧张激烈的起义之夜，火光与黑暗强烈对比"
        ),
    },
    {
        "key": "06_provinces_response",
        "title": "各省响应",
        "caption": "1911 年末，全国十余省相继宣布独立",
        "prompt": (
            "1911 年末中国多座城市轮廓组成的宽广长卷，城楼、江面与远处山峦层叠，"
            "数根高杆上无字的旗帜迎风升起，街头欢腾人群的远景剪影，"
            "晨光洒在青瓦屋顶上，由近及远的纵深构图，气象开阔壮阔"
        ),
    },
    {
        "key": "07_provisional_government",
        "title": "中华民国成立",
        "caption": "1912 年 1 月 1 日，南京临时大总统就职",
        "prompt": (
            "1912 年 1 月 1 日南京旧式会堂内的就职典礼会场，木质廊柱与高挂的红灯笼，"
            "主礼台上讲坛与立于台下的大批人群远景剪影，庄重肃穆的仪式气氛，"
            "暖黄灯光与深红布幔，油画般厚重的室内光影"
        ),
    },
    {
        "key": "08_abdication_edict",
        "title": "清帝退位",
        "caption": "1912 年 2 月 12 日，清帝退位诏书颁布",
        "prompt": (
            "1912 年冬季清晨的紫禁城太和殿前广场，空旷无人的皇家宫殿建筑群与汉白玉台阶，"
            "晨雾弥漫，白雪覆盖的屋顶与稀疏枯枝，一名抱着文书远去的背影小剪影，"
            "苍凉沉寂的氛围，象征古老王朝的终结"
        ),
    },
    {
        "key": "09_provisional_constitution",
        "title": "《中华民国临时约法》",
        "caption": "1912 年 3 月，中国第一部资产阶级共和国宪法性质文件",
        "prompt": (
            "1912 年议事厅内长条木桌的静物特写，摊开的泛黄纸质文书与墨水瓶、"
            "羽毛笔、老式台灯与堆叠的文件，背景虚化的众人剪影与拱形窗棂，"
            "午后斜射光线中漂浮的尘埃，安静而庄严，象征法治与共和的诞生"
        ),
    },
    {
        "key": "10_republic_spirit",
        "title": "共和的象征",
        "caption": "从帝制走向共和的时代转折",
        "prompt": (
            "静物式构图：一面无字的素色旗帜在风中舒展，旁边斜靠一支老式步枪，"
            "地面上散落旧式礼帽、拆开的官印与一叠书籍纸张，"
            "斑驳的青石板地面，强光下拖出长长的影子，象征旧制度崩塌与共和新生"
        ),
    },
    {
        "key": "11_significance",
        "title": "历史意义",
        "caption": "推翻帝制，打开中国进步闸门",
        "prompt": (
            "象征性长卷：一条由辛亥革命群像剪影组成的绵延人流，从昏暗的山谷走向"
            "远处喷薄而出的金色黎明，脚下是被晨雾淹没的旧城墙废墟，"
            "群像高举手臂但面目不可辨，磅礴宏大，充满希望与力量感"
        ),
    },
    {
        "key": "12_tribute",
        "title": "结语 · 致敬",
        "caption": "铭记先驱，继续前行",
        "prompt": (
            "浮雕风格的人民纪念群像：深色石质纪念碑式浮雕中，众多无名革命者身影"
            "并肩站立、前倾前行，衣角与发丝在风中扬起，庄严静穆，"
            "单色石雕质感叠加暖褐色侧光，横向画卷式构图，肃穆致敬的氛围"
        ),
    },
]


# ---------------------------------------------------------------------------
# 三、公共工具：会话、密钥、下载、保存
# ---------------------------------------------------------------------------
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36")


def make_session(retries=3, backoff=2.0):
    """带自动重试（429/5xx）的 requests.Session"""
    session = requests.Session()
    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        backoff_factor=backoff,                     # 2s, 4s, 8s ...
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "POST"]),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=8)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def load_key(cli_key, env_name):
    """按优先级取密钥：--key > 环境变量 > 同目录 api_keys.json"""
    key = (cli_key or os.environ.get(env_name) or "").strip()
    if key:
        return key
    cfg_path = BASE_DIR / "api_keys.json"
    if cfg_path.exists():
        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
            key = str(data.get(env_name, "")).strip()
        except Exception as exc:                      # 配置写错时给出提示而不是直接崩溃
            print(f"[警告] 读取 {cfg_path.name} 失败：{exc}")
    if not key:
        raise SystemExit(
            f"[错误] 未找到 {env_name}。\n"
            f"       方式1：设置环境变量  set {env_name}=你的密钥\n"
            f"       方式2：在 {cfg_path} 中写入 {{\"{env_name}\": \"你的密钥\"}}\n"
            f"       方式3：命令行传入 --key 你的密钥"
        )
    return key


def download_image(session, url, timeout=120):
    """下载图片二进制（即梦返回的 URL 可能带 \\u0026 转义，这里统一处理）"""
    url = url.replace("\\u0026", "&").replace("\\/", "/")
    resp = session.get(url, timeout=timeout, headers={"User-Agent": UA})
    resp.raise_for_status()
    if not resp.content:
        raise RuntimeError(f"下载到空内容：{url}")
    return resp.content


def save_image(data, path, convert_jpg=True, max_side=0, quality=95):
    """保存图片；convert_jpg=True 时用 Pillow 统一转成 JPEG（网页 PPT 兼容性最好）"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not convert_jpg:
        path.write_bytes(data)
        return path
    try:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(data))
        if max_side and max(img.size) > max_side:      # 按需压缩体积，避免 PPT 过大
            ratio = max_side / float(max(img.size))
            img = img.resize((max(1, int(img.width * ratio)), max(1, int(img.height * ratio))),
                             Image.LANCZOS)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        img.save(path, "JPEG", quality=quality, subsampling=0)
        return path
    except ImportError:
        print("[提示] 未安装 Pillow，直接写入原始字节（pip install pillow 可自动转 JPG）")
        path.write_bytes(data)
        return path


def update_manifest(key, record):
    """把生成结果登记进 img/manifest.json，方便网页 PPT 读取文件名/标题/说明"""
    manifest = {}
    if MANIFEST_PATH.exists():
        try:
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}
    manifest[key] = record
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# 四、通道 1：火山方舟 / 豆包 Seedream（官方接口，推荐）
# ---------------------------------------------------------------------------
def ark_build_payload(prompt, model, size, seed=None, use_b64=False):
    """构造 /api/v3/images/generations 的请求体"""
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "response_format": "b64_json" if use_b64 else "url",
        "sequential_image_generation": "disabled",   # 关闭组图，保证每次一张
        "watermark": False,                          # 关闭 AI 水印
        "stream": False,
    }
    if seed is not None:
        payload["seed"] = seed
    return payload


def ark_generate(session, prompt, api_key, model, size, seed=None, timeout=300,
                 use_b64=False, verbose=True):
    """调用火山方舟图片生成，返回图片二进制列表"""
    url = ARK_BASE_URL + ARK_ENDPOINT
    payload = ark_build_payload(prompt, model, size, seed=seed, use_b64=use_b64)
    if verbose:
        print(f"  → POST {url}")
        print(f"    model={model} size={size} seed={seed}")

    resp = session.post(
        url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=timeout,
    )
    if resp.status_code >= 400:
        detail = resp.text[:500]
        try:
            err = resp.json().get("error") or {}
            detail = f"code={err.get('code')} message={err.get('message')}"
        except Exception:
            pass
        raise RuntimeError(f"方舟接口返回 {resp.status_code}：{detail}")

    body = resp.json()
    items = body.get("data") or []
    if not items:
        raise RuntimeError(f"方舟接口未返回图片：{json.dumps(body, ensure_ascii=False)[:500]}")

    images = []
    for item in items:
        if item.get("b64_json"):
            images.append(base64.b64decode(item["b64_json"]))
        elif item.get("url"):
            images.append(download_image(session, item["url"]))
    if not images:
        raise RuntimeError("方舟接口返回了数据，但没有 url / b64_json 字段")
    if verbose and body.get("usage"):
        print(f"    用量：{json.dumps(body['usage'], ensure_ascii=False)}")
    return images


# ---------------------------------------------------------------------------
# 五、通道 2：即梦网页版（非官方逆向接口，随时可能失效，仅作备用）
#     流程：提交 /mweb/v1/aigc_draft/generate → 轮询 /mweb/v1/get_history_by_ids
# ---------------------------------------------------------------------------
def md5_hex(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def jimeng_sign(uri, device_time):
    """即梦 web 端签名：md5("9e2c|" + uri 末 7 位 + "|" + Pf + "|" + Appvr + "|" + 时间戳 + "||11ac")"""
    return md5_hex(f"9e2c|{uri[-7:]}|{JIMENG_PLATFORM_CODE}|{JIMENG_VERSION_CODE}|{device_time}||11ac")


def jimeng_fake_web_id():
    """模拟网页端的随机 webId（与前端 JS 取值区间一致）"""
    return str(int(random.random() * 999999999999999999 + 7000000000000000000))


def jimeng_headers_and_params(uri, sessionid, web_id):
    """构造即梦接口所需的请求头与公共查询参数"""
    device_time = int(time.time())
    sign = jimeng_sign(uri, device_time)
    cookie = "; ".join([
        f"_tea_web_id={web_id}",
        "is_staff_user=false",
        f"sid_guard={sessionid}%7C{device_time}%7C5184000%7CMon%2C+03-Feb-2025+08%3A17%3A09+GMT",
        f"uid_tt={web_id}",
        f"uid_tt_ss={web_id}",
        f"sid_tt={sessionid}",
        f"sessionid={sessionid}",
        f"sessionid_ss={sessionid}",
    ])
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",       # 不要带 br/zstd，避免 requests 无法解码
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Priority": "u=1, i",
        "Appvr": JIMENG_VERSION_CODE,
        "Pf": JIMENG_PLATFORM_CODE,
        "App-Sdk-Version": "48.0.0",
        "Appid": str(JIMENG_AID),
        "Cookie": cookie,
        "Device-Time": str(device_time),
        "Lan": "zh-Hans",
        "Loc": "cn",
        "Sign": sign,
        "Sign-Ver": "1",
        "Tdid": "",
        "Origin": JIMENG_BASE_URL,
        "Referer": f"{JIMENG_BASE_URL}/ai-tool/generate?type=image",
        "User-Agent": UA,
        "Content-Type": "application/json",
    }
    params = {
        "aid": JIMENG_AID,
        "device_platform": "web",
        "region": JIMENG_REGION,
        "webId": web_id,
        "da_version": JIMENG_DA_VERSION,
        "os": "windows",
        "web_component_open_flag": 1,
        "web_version": JIMENG_WEB_VERSION,
        "aigc_features": "app_lip_sync",
    }
    return headers, params


def jimeng_build_payload(prompt, model_key, resolution, ratio, negative_prompt=""):
    """构造即梦 /mweb/v1/aigc_draft/generate 的请求体（结构参照逆向实现）"""
    user_model = model_key if model_key in JIMENG_MODEL_MAP else JIMENG_MODEL_DEFAULT
    model = JIMENG_MODEL_MAP[user_model]
    if resolution not in JIMENG_RESOLUTION_OPTIONS:
        raise ValueError(f"即梦分辨率只支持 {list(JIMENG_RESOLUTION_OPTIONS)}，收到 {resolution}")
    if ratio not in JIMENG_RESOLUTION_OPTIONS[resolution]:
        raise ValueError(f"{resolution} 下不支持比例 {ratio}，可选：{list(JIMENG_RESOLUTION_OPTIONS[resolution])}")
    width, height, image_ratio = JIMENG_RESOLUTION_OPTIONS[resolution][ratio]

    submit_id = str(uuid.uuid4())
    component_id = str(uuid.uuid4())
    core_param = {
        "type": "",
        "id": str(uuid.uuid4()),
        "model": model,
        "prompt": prompt,
        "sample_strength": 0.5,
        "large_image_info": {
            "type": "",
            "id": str(uuid.uuid4()),
            "min_version": JIMENG_DRAFT_MIN_VERSION,
            "height": height,
            "width": width,
            "resolution_type": resolution,
        },
        "intelligent_ratio": False,
        "image_ratio": image_ratio,
    }
    if negative_prompt:
        core_param["negative_prompt"] = negative_prompt

    draft_content = {
        "type": "draft",
        "id": str(uuid.uuid4()),
        "min_version": JIMENG_DRAFT_MIN_VERSION,
        "min_features": [],
        "is_from_tsn": True,
        "version": JIMENG_DRAFT_VERSION,
        "main_component_id": component_id,
        "component_list": [{
            "type": "image_base_component",
            "id": component_id,
            "min_version": JIMENG_DRAFT_MIN_VERSION,
            "aigc_mode": "workbench",
            "metadata": {
                "type": "",
                "id": str(uuid.uuid4()),
                "created_platform": 3,
                "created_platform_version": "",
                "created_time_in_ms": str(int(time.time() * 1000)),
                "created_did": "",
            },
            "generate_type": "generate",
            "abilities": {
                "type": "",
                "id": str(uuid.uuid4()),
                "generate": {
                    "type": "",
                    "id": str(uuid.uuid4()),
                    "core_param": core_param,
                    "gen_option": {"type": "", "id": str(uuid.uuid4()), "generate_all": False},
                },
            },
        }],
    }

    scene_option = {
        "type": "image",
        "scene": "ImageBasicGenerate",
        "modelReqKey": model,
        "resolutionType": resolution,
        "abilityList": [],
        "reportParams": {
            "enterSource": "generate",
            "vipSource": "generate",
            "extraVipFunctionKey": f"{model}-{resolution}",
            "useVipFunctionDetailsReporterHoc": True,
        },
        "benefitCount": 4,
    }
    metrics_extra = {
        "promptSource": "custom",
        "generateCount": 1,
        "enterFrom": "click",
        "sceneOptions": json.dumps([scene_option], ensure_ascii=False),
        "generateId": submit_id,
        "isRegenerate": False,
    }

    payload = {
        "extend": {"root_model": model},
        "submit_id": submit_id,
        "metrics_extra": json.dumps(metrics_extra, ensure_ascii=False),
        "draft_content": json.dumps(draft_content, ensure_ascii=False),
        "http_common_info": {"aid": JIMENG_AID},
    }
    return payload, submit_id, {"model": model, "user_model": user_model,
                                "width": width, "height": height}


def jimeng_extract_urls(item_list):
    """从 item_list 中提取图片地址（优先 image.large_images[0].image_url）"""
    urls = []
    for item in item_list or []:
        image = item.get("image") or {}
        large = image.get("large_images") or []
        if large and large[0].get("image_url"):
            url = large[0]["image_url"]
        else:                                # 兜底：正则从整个 item 里找 CDN 链接
            found = re.search(r"https?://[^\"\\\s]+?\.(?:jpe?g|png|webp)",
                              json.dumps(item, ensure_ascii=False))
            url = found.group(0) if found else None
        if url:
            urls.append(url.replace("\\u0026", "&").replace("\\/", "/"))
    return urls


def jimeng_submit_and_wait(session, prompt, sessionid, model_key, resolution, ratio,
                           negative_prompt="", poll_interval=10, poll_timeout=900,
                           timeout=60, verbose=True):
    """提交文生图任务并轮询直到出图，返回图片二进制列表"""
    web_id = jimeng_fake_web_id()
    payload, submit_id, meta = jimeng_build_payload(prompt, model_key, resolution,
                                                    ratio, negative_prompt)
    headers, params = jimeng_headers_and_params(JIMENG_SUBMIT_PATH, sessionid, web_id)
    if verbose:
        print(f"  → POST {JIMENG_BASE_URL}{JIMENG_SUBMIT_PATH}")
        print(f"    模型 {meta['user_model']} -> {meta['model']}  "
              f"{meta['width']}x{meta['height']}  resolution={resolution}")

    resp = session.post(JIMENG_BASE_URL + JIMENG_SUBMIT_PATH, params=params,
                        headers=headers, json=payload, timeout=timeout)
    body = resp.json()
    if str(body.get("ret")) != "0":
        raise RuntimeError(f"即梦提交失败：ret={body.get('ret')} "
                           f"errmsg={body.get('errmsg')} (HTTP {resp.status_code})")
    aigc_data = (body.get("data") or {}).get("aigc_data") or {}
    history_id = aigc_data.get("history_record_id")
    if not history_id:
        raise RuntimeError("即梦未返回 history_record_id："
                           + json.dumps(body, ensure_ascii=False)[:400])
    if verbose:
        print(f"    已提交 submit_id={submit_id} history_id={history_id}，开始轮询...")

    history_payload = {
        "history_ids": [history_id],
        "image_info": {
            "width": 2048, "height": 2048, "format": "webp",
            "image_scene_list": [
                {"scene": "normal", "width": 2400, "height": 2400,
                 "uniq_key": "2400", "format": "webp"},
                {"scene": "normal", "width": 1080, "height": 1080,
                 "uniq_key": "1080", "format": "webp"},
            ],
        },
    }
    deadline = time.time() + poll_timeout
    while time.time() < deadline:
        time.sleep(poll_interval)
        headers, params = jimeng_headers_and_params(JIMENG_HISTORY_PATH, sessionid, web_id)
        r = session.post(JIMENG_BASE_URL + JIMENG_HISTORY_PATH, params=params,
                         headers=headers, json=history_payload, timeout=timeout)
        task = (r.json().get("data") or {}).get(history_id)
        if not task:
            if verbose:
                print("    [轮询] 记录尚未出现，继续等待...")
            continue
        status = task.get("status")
        item_list = task.get("item_list") or []
        urls = jimeng_extract_urls(item_list)
        if verbose:
            print(f"    [轮询] status={status} item_list={len(item_list)} 图片={len(urls)}")
        if status == 30:
            raise RuntimeError(f"即梦生成失败 status=30 fail_code={task.get('fail_code')}")
        if urls and status in (10, 50):
            return [download_image(session, u) for u in urls]
    raise TimeoutError(f"即梦轮询超时（{poll_timeout}s），history_id={history_id}")


# ---------------------------------------------------------------------------
# 六、任务组织：提示词拼装、任务筛选
# ---------------------------------------------------------------------------
def build_prompt(task, no_style=False):
    """给画面描述拼上统一画风后缀，保证 12 张图风格一致"""
    return task["prompt"] if no_style else task["prompt"] + STYLE_SUFFIX


def select_tasks(prompts, only=None, limit=0):
    """按 --only（序号或关键字）与 --limit 挑选要生成的任务"""
    if not only:
        items = list(prompts)
    else:
        tokens = [t for t in re.split(r"[,，\s]+", only) if t]
        items = []
        for token in tokens:
            if token.isdigit():
                idx = int(token) - 1
                if 0 <= idx < len(prompts):
                    items.append(prompts[idx])
                else:
                    print(f"[警告] --only {token} 超出范围（共 {len(prompts)} 张）")
            else:
                matched = [p for p in prompts
                           if token.lower() in p["key"].lower() or token in p["title"]]
                if matched:
                    items.extend(matched)
                else:
                    print(f"[警告] --only {token} 未匹配到任何提示词")
        seen, uniq = set(), []
        for p in items:                      # 去重并保持顺序
            if p["key"] not in seen:
                seen.add(p["key"])
                uniq.append(p)
        items = uniq
    if limit and limit > 0:
        items = items[:limit]
    return items


def ark_size_for(model, ratio, explicit=None):
    """方舟尺寸：显式 --size 优先，否则按模型代次 + 比例查表"""
    if explicit:
        return explicit
    table = ARK_SIZES_3_0 if ("3-0" in model or "3_0" in model) else ARK_SIZES_4_0
    return table.get(ratio) or "2048x1152"


# ---------------------------------------------------------------------------
# 七、离线自检（不联网、不消耗额度，用于验证参数组装与本地保存逻辑）
# ---------------------------------------------------------------------------
def self_test():
    print("== 开始离线自检 ==")

    # 1) 即梦签名算法与 URI 末 7 位切片
    expected = hashlib.md5(b"9e2c|enerate|7|8.4.0|1700000000||11ac").hexdigest()
    assert jimeng_sign(JIMENG_SUBMIT_PATH, 1700000000) == expected, "签名算法不匹配"
    assert JIMENG_SUBMIT_PATH[-7:] == "enerate", "提交接口末 7 位错误"
    assert JIMENG_HISTORY_PATH[-7:] == "_by_ids", "查询接口末 7 位错误"
    print("  [1/6] 即梦 sign 计算正确")

    # 2) 方舟请求体字段
    payload = ark_build_payload("测试画面", ARK_MODEL_DEFAULT, ARK_SIZES_4_0["16:9"], seed=42)
    for field in ("model", "prompt", "size", "response_format",
                  "sequential_image_generation", "watermark", "stream"):
        assert field in payload, f"缺少字段 {field}"
    assert payload["size"] == "2048x1152" and payload["seed"] == 42
    json.dumps(payload, ensure_ascii=False)
    print("  [2/6] 方舟请求体字段完整")

    # 3) 即梦请求体字段（模型映射、尺寸、负面提示词、aid）
    body, submit_id, meta = jimeng_build_payload("测试画面", "jimeng-4.5", "2k", "16:9", NEGATIVE_PROMPT)
    draft = json.loads(body["draft_content"])
    core = draft["component_list"][0]["abilities"]["generate"]["core_param"]
    assert body["http_common_info"]["aid"] == 513695 and body["submit_id"] == submit_id
    assert meta["model"] == "high_aes_general_v40l" and meta["width"] == 2560 and meta["height"] == 1440
    assert core["prompt"] == "测试画面" and core["negative_prompt"] == NEGATIVE_PROMPT
    assert core["large_image_info"]["resolution_type"] == "2k"
    scene = json.loads(json.loads(body["metrics_extra"])["sceneOptions"])[0]
    assert scene["modelReqKey"] == "high_aes_general_v40l" and scene["resolutionType"] == "2k"
    print("  [3/6] 即梦请求体结构正确")

    # 4) 提示词清单
    assert len(PROMPTS) == 12, "应包含 12 张插画提示词"
    assert len({p["key"] for p in PROMPTS}) == 12, "提示词 key 重复"
    assert len(select_tasks(PROMPTS, "1,05,tribute")) == 3, "任务筛选异常"
    assert len(select_tasks(PROMPTS, None, 4)) == 4, "--limit 异常"
    print("  [4/6] 12 条提示词与筛选逻辑正常")

    # 5) 即梦结果 URL 提取
    demo = [{"image": {"large_images": [{"image_url": "https://cdn.example.com/a.webp\\u0026x=1"}]}},
            {"image": {}}]
    urls = jimeng_extract_urls(demo)
    assert urls == ["https://cdn.example.com/a.webp&x=1"], f"URL 提取异常：{urls}"
    print("  [5/6] 图片 URL 提取正常")

    # 6) 本地保存（PNG -> JPEG）与目录创建
    from io import BytesIO
    from PIL import Image
    buf = BytesIO()
    Image.new("RGB", (64, 36), (176, 96, 64)).save(buf, "PNG")
    test_dir = Path(tempfile.gettempdir()) / "jimeng_img_selftest"
    path = save_image(buf.getvalue(), test_dir / "demo.jpg", convert_jpg=True, max_side=32)
    with Image.open(path) as im:
        assert im.format == "JPEG" and max(im.size) == 32, "JPEG 转换/缩放异常"
    save_image(buf.getvalue(), test_dir / "raw.png", convert_jpg=False)
    assert (test_dir / "raw.png").stat().st_size > 0
    print(f"  [6/6] 图片保存与 JPG 转换正常（{test_dir}）")

    print("== 自检通过：参数组装与保存逻辑均可用 ==")
    return 0

