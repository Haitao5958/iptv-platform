
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TVBox 浠搴�ㄩ�存� v4 �ü�ü ���锛��″ㄧ�绾�锛
============================================================
- �ㄦ�″ㄤ��存ヨ�琛锛�  paramiko 渚璧锛
- 娴璇�ü��ュｅ�ㄦü�
- �ü�绾胯矾缁涓ü娣诲  " 路" ���缂ü
- ��� /opt/iptv/tvbox/repo.json + �存� index.html
"""
import json
import time
import concurrent.futures
from urllib.parse import quote
from urllib.request import urlopen, Request
from urllib.error import HTTPError

# ===================== ��璁剧疆 =====================
BRAND_NAME = ""

def get_branded_name(raw_name):
    """灏�濮�绉扮�涓ü�瑁涓�  路 xxx"""
    clean_name = raw_name.strip()
    if BRAND_NAME in clean_name:
        return clean_name
    return f"{BRAND_NAME} 路 {clean_name}"


def encode_url(url):
    """澶�涓���锛IDNA 缂� 锛"""
    if '://' not in url:
        return url
    scheme, rest = url.split('://', 1)
    if '/' in rest:
        host_part, path = rest.split('/', 1)
        try:
            host_encoded = host_part.encode('idna').decode('ascii')
        except Exception:
            host_encoded = host_part
        path = quote(path, safe='/')
        return f"{scheme}://{host_encoded}/{path}"
    else:
        try:
            return f"{scheme}://{rest.encode('idna').decode('ascii')}"
        except Exception:
            return url


# ===================== 寰娴璧婧�琛� =====================
# 璇存锛raw.githubusercontent.com 婧� �藉� �ü浠ｇ�缂ü锛�藉 TVBox �存ユ GitHub 甯稿け璐ワ�
# 浠ｇ锛ghfast.top / ghproxy.net �澶�ü
GH = "https://ghfast.top/https://raw.githubusercontent.com/"
GH2 = "https://ghproxy.net/https://raw.githubusercontent.com/"

URLS_TO_TEST = [
    # --- �ü1. ��ü�规���ü ---
    {"name": "�� �ョ�", "url": "http://�ョ�.net", "type": "single", "force": True},
    {"name": "�� 楗�お纭�", "url": "http://www.楗�お纭�.net/tv", "type": "single", "force": True},
    {"name": "�� �灏浜(��)", "url": "https://9280.kstore.vip/newwex.json", "type": "single"},
    {"name": "�� �哄ソ�浜�", "url": "http://ztha.top/TVBox/thdjk.json", "type": "single"},
    {"name": "�� 椹搁┈", "url": "http://fmys.top/fmys.json", "type": "single"},
    {"name": "�� �澶", "url": "https://raw.liucn.cc/box/m.json", "type": "single", "force": True},
    {"name": "�� dxawi", "url": GH + "dxawi/0/main/0.json", "type": "single"},
    {"name": "�� 棣��", "url": GH + "xyq254245/xyqonlinerule/main/XYQTVBox.json", "type": "single"},
    {"name": "�� ���", "url": "https://g.3344550.xyz/" + GH2 + "jigedos/1024/master/jsm.json", "type": "single"},
    {"name": "�� �遍", "url": GH + "xuexuguang/tvbox_spider/main/tv/kk/heroaku_dtes.json", "type": "single"},
    {"name": "�� 楂澶╂�浜", "url": GH2 + "gaotianliuyun/gao/master/js.json", "type": "single"},
    {"name": "�� 灏灞", "url": "https://git.acwing.com/shhentu/lzxw/-/raw/main/Monster.json", "type": "single"},
    {"name": "�� 灏�瀛", "url": "http://xhztv.top/xhz", "type": "single", "force": True},
    {"name": "�� 灏�瀛4K", "url": "http://xhztv.top/4k.json", "type": "single", "force": True},
    {"name": "�� ��虹背", "url": "https://17264.kstore.space/��虹背.png", "type": "single"},
    {"name": "�� �ㄦ极�", "url": "https://www.yingm.cc/dm/dm.json", "type": "single"},
    {"name": "�� HG�ュ�", "url": "https://api.hgyx.vip/hgyx.json", "type": "single"},
    {"name": "�� 娼娲", "url": "https://9877.kstore.space/ONE/one.json", "type": "single"},
    {"name": "�� 灏�规", "url": "https://bitbucket.org/xduo/duoapi/raw/master/xpg.json", "type": "single"},
    {"name": "�� 瀹�VIP", "url": GH + "guot55/YGBH/main/vip2.json", "type": "single"},
    {"name": "�� 娆ф�", "url": "https://xn--anna-wn6lw489o.v.nxog.top/m/", "type": "single", "force": True},
    {"name": "�� �蹇", "url": "https://www.252035.xyz/z/FongMi.json", "type": "single"},
    {"name": "�� �浜�", "url": GH2 + "maoystv/6/main/000.json", "type": "single"},
    {"name": "�� ���", "url": "https://cnb.cool/fish2018/duanju/-/git/raw/main/tvbox.json", "type": "single"},
    {"name": "�� 涓绡辩嚎璺�", "url": GH + "chitue/dongliTV/main/api.json", "type": "single"},
    {"name": "�� �峰绾胯矾", "url": "https://cnb.cool/aooooowuuuuu/FreeSpider/-/git/raw/main/config", "type": "single"},
    {"name": "�� L浣�嚎璺�", "url": "https://android.lushunming.qzz.io/json/index.json", "type": "single"},
    {"name": "�� �规CMS", "url": "https://pastebin.com/raw/gtbKvnE1", "type": "single"},
    {"name": "�� CandyMuj", "url": "https://tv.520993.xyz/candymuj.json", "type": "single"},
    {"name": "�� CandyMuj(� 绂��)", "url": "https://tv.520993.xyz/candymuj1.json", "type": "single"},
    {"name": "�� tvyuan�ㄩ�", "url": "https://tv.cc0cd.cc.cd", "type": "single"},
    {"name": "�� �濡��", "url": "https://tv.xn--yhqu5zs87a.top", "type": "single"},
    {"name": "�� 榫浼", "url": "https://xn--qoqw77q.top/", "type": "single"},

    # --- �ü3. 澶浠婧�ü ---
    {"name": "�� 灏�瀛澶浠", "url": "http://xhztv.top/dc/", "type": "multi"},
    {"name": "�� �惧澶浠", "url": "http://xmbjm.fh4u.org/dc.txt", "type": "multi"},

    # --- �ü4. 澶�ㄧ存���ü ---
    {"name": "�� �︾剁存�", "url": GH + "YueChan/Live/refs/heads/main/IPTV.m3u", "type": "live"},
    {"name": "� �︾跺ㄧ", "url": GH + "YueChan/Live/refs/heads/main/Global.m3u", "type": "live"},
    {"name": "�� �存�佃�IPV4", "url": "https://live.zbds.top/tv/iptv4.txt", "type": "live"},
    {"name": "�帮� �戒��存�", "url": GH2 + "Guovin/iptv-api/gd/output/result.m3u", "type": "live"},
    {"name": "�� �缈�存�", "url": GH + "suxuang/myIPTV/refs/heads/main/ipv4.m3u", "type": "live"},
]


def test_url(item):
    """涓ユ 兼 ¢�锛GET �瀹� + 绫诲妫ü�ワ�TVBox 瑙ｆ�煎��üэ�"""
    url = encode_url(item["url"])
    name = item["name"]
    try:
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 TVBox/1.0",
            "Accept": "*/*"
        })
        with urlopen(req, timeout=12) as resp:
            content = resp.read(200000)
            status = resp.status
            text = content.decode('utf-8', errors='ignore')[:10000]
            low = text.lower()
            ct = resp.headers.get('Content-Type', '')
            if 'application/json' in ct or text.strip().startswith(('{', '[')):
                return name, item["url"], status, "OK-JSON", item["type"]
            elif low.startswith('#extm3u') or '#extinf' in low or '.m3u8' in low:
                return name, item["url"], status, "OK-M3U", item["type"]
            elif ',#' in low or '#genre#' in low:
                return name, item["url"], status, "OK-TXT", item["type"]
            else:
                return name, item["url"], status, f"BAD({ct[:20]})", item["type"]
    except HTTPError as e:
        return name, item["url"], e.code, "HTTP Error", item["type"]
    except Exception as e:
        return name, item["url"], 0, str(e)[:60], item["type"]


def main():
    print("=" * 70)
    print(f"�� {BRAND_NAME} | TVBox 浠搴�ㄩ�存� v4锛��″ㄧ�锛")
    print("=" * 70)
    print("姝ｅㄦ�璇�ü��ュｅ�ㄦü�...")
    print()

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        future_to_url = {executor.submit(test_url, item): item for item in URLS_TO_TEST}
        for future in concurrent.futures.as_completed(future_to_url):
            result = future.result()
            results.append(result)
            status_icon = "�" if result[3] in ("OK-JSON", "OK-M3U", "OK-TXT") else "�"
            print(f"{status_icon} {result[0][:30]:<30} HTTP {result[2]:<4} {result[3]}")

    # �����瀹圭被�� ¢��ü杩锛OK-JSON/OK-M3U/OK-TXT锛�绾胯矾 + force � 璁扮锛�ㄦ风‘璁ゅ���
    force_names = {item["name"] for item in URLS_TO_TEST if item.get("force")}
    ok_results = [r for r in results if r[3] in ("OK-JSON", "OK-M3U", "OK-TXT") or r[0] in force_names]
    fail_results = [r for r in results if r[3] not in ("OK-JSON", "OK-M3U", "OK-TXT") and r[0] not in force_names]

    print("\n" + "=" * 70)
    print(f"� ���: {len(ok_results)} / {len(results)}")
    print(f"� 涓���: {len(fail_results)} / {len(results)}")
    print("=" * 70)

    # �绫伙�famous 涔褰�� single锛
    single_ok = [r for r in ok_results if r[4] in ("single", "famous")]
    multi_ok = [r for r in ok_results if r[4] == "multi"]
    live_ok = [r for r in ok_results if r[4] == "live"]

    # ===================== �寤哄�浠搴 =====================
    urls = []

    # 1) 澶浠婧锛���锛
    for r in multi_ok:
        urls.append({"name": get_branded_name(r[0]), "url": r[1]})

    # 2) �浠婧
    for r in single_ok:
        urls.append({"name": get_branded_name(r[0]), "url": r[1]})

    # 3) 澶�ㄧ存��锛涓�� �ヤ�搴锛"绾胯矾褰绾胯矾锛�存��繁�"锛
    #    �存���存ュ� TVBox �存�〉娣诲  m3u 婧锛
    #      http://YOUR_SERVER_IP/m3u/all.m3u   锛�存�ü绘�锛16324 棰� 29 �缁锛
    #      http://YOUR_SERVER_IP/m3u/cn.m3u    锛�藉绮剧�ü�锛1588 棰�锛
    #    live_ok 浠淇�缁璁＄ㄩü

    # 4) ��缓�存��锛����藉锛棰��板ㄦü璇诲锛
    # TVBox 澶浠�ü绾胯矾�惰�姹姣涓�嚎璺��ü瀹�� TVBox �缃� JSON�ü�ü
    # �ü�存�姝/涓绘�绾胯矾� lives � 煎�锛姣涓� live 蹇椤诲甫 type/playerType/timeout 绛瀛娈碉�
    # �﹀�ㄥ TVBox ���榛蹇界ワ�瀵艰�"�ü绾胯矾涓�ラ浣�存���剧ず"�ü
    def count_channels(m3u_name):
        try:
            with open(f"/opt/iptv/m3u/{m3u_name}", 'r', encoding='utf-8') as f:
                return sum(1 for line in f if line.startswith("#EXTINF:"))
        except Exception:
            return 0

    def make_live(name, m3u_path, epg_url=""):
        """��ü  TVBox � � live �＄��妯′豢娆ф�� 煎�锛"""
        live = {
            "name": name,
            "type": 0,
            "url": f"http://YOUR_SERVER_IP/m3u/{m3u_path}",
            "playerType": 2,
            "timeout": 10
        }
        if epg_url:
            live["epg"] = epg_url
        return live

    def write_live_config(json_name, lives, cfg_name="�存�"):
        """��ュ��� TVBox �存�缃� JSON�ü

        �瑕锛蹇椤讳互"娆ф��哄骇"锛spider 瀹��URL + 127涓�sites + parses锛涓烘ā�匡�
        ��挎� lives�ü瀹娴褰辫�浠澶浠�ü绾胯矾�讹��ラ缃� sites 涓虹┖ / spider 涓虹┖锛
        浼�ゅ��缃� ��ü�翠�蹇界ワ��� lives锛锛瀵艰�"�ü绾胯矾涓�ラ浣�存���剧ず"�ü
        娆ф�/椹搁┈/楗�お纭���芥�甯告剧ず�存��缃���ㄩㄦ� spider+sites+lives 榻�ㄧ�ü
        """
        try:
            with open("/opt/iptv/tvbox/ouge_base.json", "r", encoding="utf-8") as f:
                base = json.load(f)
        except Exception as e:
            print(f"  � 锔 ouge_base.json � 杞藉け璐�({e})锛��üü涓烘ü灏缁�")
            base = {"spider": "", "sites": [], "parses": []}
        cfg = dict(base)
        cfg["name"] = cfg_name
        cfg["lives"] = lives
        with open(f"/opt/iptv/tvbox/{json_name}", "w", encoding="utf-8") as f:
            f.write(json.dumps(cfg, ensure_ascii=False, indent=1))

    cn_count = count_channels("cn.m3u")
    cctv_count = count_channels("cctv.m3u")
    weishi_count = count_channels("weishi.m3u")
    local_count = count_channels("local.m3u")
    hktwmo_count = count_channels("hktwmo.m3u")
    all_count = count_channels("all.m3u")

    # 姣涓�绫讳�ü涓����缃���ü绾胯矾���剧ず瀵瑰��绫荤�存��锛
    write_live_config("live_cn.json", [make_live(f"{BRAND_NAME} 路 ��� 涓�介��锛{cn_count}锛", "cn.m3u")], "涓�介��")
    write_live_config("live_cctv.json", [make_live(f"{BRAND_NAME} 路 �� 澶��棰�锛{cctv_count}锛", "cctv.m3u")], "澶��")
    write_live_config("live_weishi.json", [make_live(f"{BRAND_NAME} 路 �� ���棰�锛{weishi_count}锛", "weishi.m3u")], "���")
    write_live_config("live_local.json", [make_live(f"{BRAND_NAME} 路 �  �版瑰帮�{local_count}锛", "local.m3u")], "�版瑰�")
    write_live_config("live_hktwmo.json", [make_live(f"{BRAND_NAME} 路 ��� 娓�境�帮�{hktwmo_count}锛", "hktwmo.m3u")], "娓�境��")
    write_live_config("live_all.json", [make_live(f"{BRAND_NAME} 路 � �ㄧ棰�锛{all_count}锛", "all.m3u")], "�ㄧ")

    # 涓ü绔寮�缃��6 涓�存����涓ü涓�缃���ü涓ü�＄嚎璺�存�〉灏辨�ㄩ� 6 涓��锛�ü�ヨ�娆ф�浣楠锛
    all_lives = [
        make_live(f"{BRAND_NAME} 路 ��� 涓�介��锛{cn_count}锛", "cn.m3u"),
        make_live(f"{BRAND_NAME} 路 �� 澶��棰�锛{cctv_count}锛", "cctv.m3u"),
        make_live(f"{BRAND_NAME} 路 �� ���棰�锛{weishi_count}锛", "weishi.m3u"),
        make_live(f"{BRAND_NAME} 路 �  �版瑰帮�{local_count}锛", "local.m3u"),
        make_live(f"{BRAND_NAME} 路 ��� 娓�境�帮�{hktwmo_count}锛", "hktwmo.m3u"),
        make_live(f"{BRAND_NAME} 路 � �ㄧ棰�锛{all_count}锛", "all.m3u"),
    ]
    write_live_config("live_all_in_one.json", all_lives, "�存�ü绘�")

    # 4) ��缓�存�缃��涓�� �ヤ�搴锛"绾胯矾褰绾胯矾锛�存��繁�"锛
    #    �ㄦ风存ュ� TVBox �存�〉娣诲  m3u �ü绘��冲��
    #      http://YOUR_SERVER_IP/m3u/all.m3u   锛涓ü涓����ㄩ��澶��/���/�版瑰�/娓�境��/��斤�
    #      http://YOUR_SERVER_IP/m3u/cn.m3u    锛�藉绮剧�ü�锛
    #    live_*.json 浠淇���锛渚�缃�瑰�澶���锛浣涓��� repo.json

    repo_json = {
        "name": f"�� {BRAND_NAME} - �ㄨ藉奖瑙�存��搴",
        "description": f"{BRAND_NAME}澶浠�缃���规�负涓伙��存���存ユ坊�  m3u �存��锛锛��ㄦ�璇绛�ü锛姣6灏�舵存�",
        "version": time.strftime("%Y-%m-%d"),
        "update_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "urls": urls
    }

    # ===================== �存ュ�浠讹���″ㄧ�锛 =====================
    with open("/opt/iptv/tvbox/repo.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(repo_json, ensure_ascii=False, indent=2))
    print("� repo.json 宸叉存�")

    # �存� HTML
    try:
        with open("/opt/iptv/tvbox/index.html", "r", encoding="utf-8") as f:
            html = f.read()
        html = html.replace('Last updated:', f"Last updated: {repo_json['update_time']} |")
        with open("/opt/iptv/tvbox/index.html", "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        print(f"HTML update error: {e}")

    # ===================== 姹�ü昏��� =====================
    print("\n" + "=" * 70)
    print(f"� TVBox 浠搴宸叉存帮�{BRAND_NAME} ���锛")
    print("=" * 70)
    print(f"�� ���绉�: {BRAND_NAME}")
    print(f"�� ��ㄧ嚎璺�: {len(urls)} �★��涓虹规�嚎璺��")
    print(f"  - 澶浠: {len(multi_ok)} ��")
    print(f"  - �浠: {len(single_ok)} ��")
    print(f"\n�� �存��锛TVBox �存�〉�存ユ坊� 锛涓璧扮嚎璺��:")
    print(f"  - �存�ü绘�: http://YOUR_SERVER_IP/m3u/all.m3u")
    print(f"  - �藉绮剧�ü�:      http://YOUR_SERVER_IP/m3u/cn.m3u")
    print(f"\n� 澶浠�板ü: http://YOUR_SERVER_IP/tvbox/repo.json")
    print(f"� �存版堕�: {repo_json['update_time']}")


if __name__ == "__main__":
    main()
