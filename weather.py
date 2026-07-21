#!/usr/bin/env python3
"""Open-Meteo 綜合氣象數據展示工具 (Rich 正體中文版)"""

import requests
from datetime import datetime
from urllib3.util.ssl_ import create_urllib3_context
from requests.adapters import HTTPAdapter

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

# ================= 設定區 =================
緯度 = 30.14
經度 = 120.29
預報天數 = 7
# ==========================================

# WMO 天氣代碼對照表
WMO_天氣代碼 = {
    0: "☀️ 晴", 1: "🌤️ 大致晴朗", 2: "⛅ 多雲", 3: "☁️ 陰天",
    45: "🌫️ 霧", 48: "🌫️ 凍霧",
    51: "🌦️ 小雨毛", 53: "🌦️ 中雨毛", 55: "🌧️ 大雨毛",
    61: "🌧️ 小雨", 63: "🌧️ 中雨", 65: "🌧️ 大雨",
    71: "🌨️ 小雪", 73: "🌨️ 中雪", 75: "❄️ 大雪",
    80: "🌦️ 陣雨(小)", 81: "🌧️ 陣雨(中)", 82: "⛈️ 陣雨(大)",
    95: "⛈️ 雷暴", 96: "⛈️ 雷暴伴冰雹", 99: "⛈️ 強雷暴伴冰雹"
}

console = Console()


def 建立安全連線():
    """建立帶有 SSL 容錯機制的請求工作階段"""
    session = requests.Session()
    try:
        ctx = create_urllib3_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        adapter = HTTPAdapter(ssl_context=ctx)
        session.mount('https://', adapter)
    except Exception:
        pass
    return session


def 獲取氣象數據():
    """從 Open-Meteo API 獲取綜合氣象資料"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 緯度,
        "longitude": 經度,
        "daily": ["sunrise", "sunset", "temperature_2m_max",
                  "temperature_2m_min", "precipitation_sum",
                  "weathercode", "wet_bulb_temperature_2m_max",
                  "wet_bulb_temperature_2m_min"],
        "hourly": ["wet_bulb_temperature_2m", "temperature_2m",
                   "relativehumidity_2m", "weathercode"],
        "timezone": "auto",
        "forecast_days": 預報天數
    }
    session = 建立安全連線()
    resp = session.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def 渲染元資訊面板(data):
    """渲染位置與時間資訊面板"""
    tz = data.get("timezone", "未知")
    utc_off = data.get("utc_offset_seconds", 0)
    hours = utc_off // 3600
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    info_text = Text()
    info_text.append(f"📍 座標: ({data['latitude']}, {data['longitude']})\n", style="cyan")
    info_text.append(f"⛰️  海拔: {data['elevation']} m\n", style="green")
    info_text.append(f"🕐 時區: {tz} (UTC{hours:+d})\n", style="yellow")
    info_text.append(f"📅 查詢時間: {now_str}", style="dim")

    return Panel(info_text, title="🌦️ 氣象概覽", border_style="blue", padding=(1, 2))


def 渲染每日預報表格(data):
    """渲染多日預報與濕球溫度摘要表格"""
    daily = data["daily"]
    table = Table(title=f"📊 {預報天數}日天氣與濕球溫度摘要", show_lines=True, pad_edge=False)

    table.add_column("日期", style="cyan", justify="center", min_width=12)
    table.add_column("天氣", justify="center", min_width=14)
    table.add_column("氣溫 (°C)", justify="right", style="green", min_width=10)
    table.add_column("濕球 (°C)", justify="right", style="magenta", min_width=10)
    table.add_column("降水 (mm)", justify="right", style="blue", min_width=10)
    table.add_column("日出 / 日落", justify="center", style="yellow", min_width=14)

    for i in range(len(daily["time"])):
        date = daily["time"][i]
        code = daily["weathercode"][i]
        weather = WMO_天氣代碼.get(code, f"未知({code})")
        t_max = daily["temperature_2m_max"][i]
        t_min = daily["temperature_2m_min"][i]
        wb_max = daily["wet_bulb_temperature_2m_max"][i]
        wb_min = daily["wet_bulb_temperature_2m_min"][i]
        precip = daily["precipitation_sum"][i]
        sr = daily["sunrise"][i].split("T")[1]
        ss = daily["sunset"][i].split("T")[1]

        temp_str = f"{t_min:.0f} ~ {t_max:.0f}" if t_min is not None else "N/A"
        wb_str = f"{wb_min:.1f} ~ {wb_max:.1f}" if wb_min is not None else "N/A"
        precip_str = f"{precip:.1f}" if precip is not None else "0.0"

        # 根據濕球溫度動態標色
        wb_style = "magenta"
        if wb_max and wb_max >= 28:
            wb_style = "bold red"
        elif wb_max and wb_max >= 25:
            wb_style = "bold yellow"

        table.add_row(
            date, weather, temp_str,
            Text(wb_str, style=wb_style),
            precip_str, f"{sr} / {ss}"
        )

    return table


def 渲染逐時濕球表格(data):
    """渲染今日24小時濕球溫度詳情表格"""
    hourly = data["hourly"]
    today = datetime.now().strftime("%Y-%m-%d")

    indices = [i for i, t in enumerate(hourly["time"]) if t.startswith(today)]
    if not indices:
        return Panel("⚠️ 未找到今日的小時級數據", style="red")

    table = Table(title=f"🌡️ 今日 ({today}) 24小時濕球溫度詳情", show_lines=False, pad_edge=False)
    table.add_column("時間", style="cyan", justify="center", min_width=8)
    table.add_column("濕球 (°C)", justify="right", style="magenta", min_width=10)
    table.add_column("氣溫 (°C)", justify="right", style="green", min_width=10)
    table.add_column("濕度 (%)", justify="right", style="blue", min_width=10)
    table.add_column("天氣", justify="left", min_width=16)

    for i in indices:
        time_str = hourly["time"][i].split("T")[1]
        wb = hourly["wet_bulb_temperature_2m"][i]
        temp = hourly["temperature_2m"][i]
        rh = hourly["relativehumidity_2m"][i]
        code = hourly["weathercode"][i]
        weather = WMO_天氣代碼.get(code, str(code))

        wb_s = f"{wb:.1f}" if wb is not None else "N/A"
        temp_s = f"{temp:.1f}" if temp is not None else "N/A"
        rh_s = f"{rh}" if rh is not None else "N/A"

        # 當前小時高亮顯示
        row_style = ""
        if time_str[:2] == datetime.now().strftime("%H"):
            row_style = "bold white on dark_blue"

        table.add_row(time_str, wb_s, temp_s, rh_s, weather, style=row_style)

    return table


if __name__ == "__main__":
    try:
        data = 獲取氣象數據()

        meta_panel = 渲染元資訊面板(data)
        daily_table = 渲染每日預報表格(data)
        hourly_table = 渲染逐時濕球表格(data)

        console.print()
        console.print(meta_panel)
        console.print()
        console.print(daily_table)
        console.print()
        console.print(hourly_table)
        console.print()
        console.print(
            "💡 注意: 濕球溫度為2米高度熱力學濕球溫度，非 WBGT 指數",
            style="dim italic"
        )
        console.print()

    except requests.exceptions.SSLError as e:
        console.print(f"[bold red]❌ SSL 錯誤:[/] 請檢查網路代理或升級 OpenSSL\n   {e}")
    except requests.RequestException as e:
        console.print(f"[bold red]❌ 請求失敗:[/] {e}")
