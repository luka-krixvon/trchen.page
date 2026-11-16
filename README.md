# 學者個人網站 — A+C 版（英 / 繁中 / 日）

C 版的固定側欄導覽配 A 版的期刊式內文：介面用無襯線，內容用襯線。
每篇論文可以就地展開一支自己錄的講解影片，底下附章節時間軸。

## 只要改一個檔

全部文字都在 **`content.json`**。改完跑：

```bash
python3 build.py
```

就會重新產生 `index.html`（英）、`zh/index.html`（繁中）、`ja/index.html`（日），
以及 `sitemap.xml`、`robots.txt`。不要直接改產生出來的 HTML，下次 build 會被蓋掉。

論文與專利名稱三語共用（學術慣例不翻譯），其餘每種語言各寫一份。
新增一篇論文＝在 `publications` 加一個物件，再到 `en`/`zh`/`ja` 的 `chapters` 各加一組章節。

## 目前填好了什麼

| 欄位 | 值 |
|---|---|
| 姓名 | Teng-Ruei Chen（中文 陳騰瑞） |
| ORCID | `0000-0001-8995-334X` |
| 聯絡信箱 | `ymchen.bi04g@g2.nctu.edu.tw` |
| Bio、學歷、經歷 | 三語，取自 `Study/共用_跨論文/作者資訊_主檔.md` 與論文的 IEEE biography |
| 論文 | 7 篇，標題取自各專案 `main.tex` 的 `\title{}` |

## 還沒填

| 欄位 | 現況 |
|---|---|
| `site.domain` | `https://yourname.com` — canonical、hreflang、JSON-LD 都吃這個，上線前一定要改 |
| `site.scholar` | 還是 placeholder。側欄那張卡是全頁最顯眼的連結，沒有 profile 就先改成 ORCID 或拿掉 |
| `site.github` / `site.youtube` | placeholder |
| `cv.pdf` / `og.png` | 檔案還沒放（og.png 1200×630，分享連結時的預覽圖） |
| 各論文 `venues` | 七篇的 venue 全部是 `TODO — 確認狀態`，要逐篇填真實投稿狀態 |
| 各論文 `video` | 全部 `null`。錄好講解後填 `video` 和 `chapters`，講解按鈕、章節時間軸、`VideoObject` 標記會自動出現 |
| `patents` | 空陣列。空的時候整個 section 和側欄連結都自動隱藏 |
| `counts` | 全部 `null`，頁面顯示「—」。有真實數字再填 |

## 單位掛法（別改錯）

**側欄刻意不掛任何單位**（作者 2026-11-13 決定），只顯示研究領域與所在地。

`Study/共用_跨論文/作者資訊_主檔.md` 是作者資訊的唯一權威來源，它明訂：

> NYCU 是母校，不是現職 —— 2021 取得博士後已無現職關係。**不得**因為共同作者是 NYCU 教授、
> 或因為研究主題與 NYCU 相關，就把 NYCU 加回去。

所以 `Institute of Bioinformatics and Systems Biology, NYCU` **不可以**出現在側欄或任何
主張現職的位置。它目前只出現在 About 的學歷列（2021 博士），那是正確用法。

Krixvon 全站只出現在兩處：About 的經歷列表、JSON-LD 的 `worksFor`。兩者都是履歷事實。

## 網域：trchen.page（DNS 在 Cloudflare）

`CNAME` 檔的內容就是 `trchen.page`，GitHub Pages 靠它認自訂網域。

Cloudflare 的 DNS 設定（**先用 DNS only，不要開橘色雲朵代理**）：

| 類型 | 名稱 | 值 |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| AAAA | `@` | `2606:50c0:8000::153` |
| AAAA | `@` | `2606:50c0:8001::153` |
| AAAA | `@` | `2606:50c0:8002::153` |
| AAAA | `@` | `2606:50c0:8003::153` |
| CNAME | `www` | `<帳號>.github.io` |

IP 取自 `api.github.com/meta` 的 `pages` 欄位，要確認最新值就重跑那個 API。

**為什麼先不要開代理**：橘色雲朵開著的時候 GitHub 看不到真實的 DNS，沒辦法簽發憑證，
「Enforce HTTPS」會一直是灰的。而且 Cloudflare 的 SSL 模式若是 Flexible 會造成無限轉址。
等 GitHub 簽好憑證、網站正常之後，要開代理再開，並把 SSL/TLS 模式設成 **Full (strict)**。

**`.page` 是 HSTS preload 的 TLD**：瀏覽器一律強制 HTTPS，所以憑證簽好之前網站完全打不開，
那是正常的，等就好（通常幾分鐘到一小時）。

## 部署到 GitHub Pages

```bash
git init && git add -A && git commit -m "personal site"
```

```bash
git remote add origin https://github.com/<你的帳號>/<你的帳號>.github.io.git && git push -u origin main
```

Repo 取名 `<帳號>.github.io` 就會直接上線在 `https://<帳號>.github.io`。
要自己的網域：在 repo 根目錄放一個 `CNAME` 檔（內容就是 `yourname.com`），
再到網域商把 DNS 指向 GitHub Pages，然後在 Settings → Pages 勾 Enforce HTTPS。

**建議用自己的網域。**學校給的 `university.edu/~username` 在你換單位時會整個失效，
累積的連結與搜尋排名全部歸零。

## 影片怎麼接

`content.json` 裡每篇論文的 `video.id` 填 YouTube 影片 ID（網址 `watch?v=` 後面那段）。

播放器是 **click-to-load**：一開始只載入縮圖，點了才建立 iframe。
好處是首頁載入快很多，而且在使用者按下播放前，YouTube 不會植入任何追蹤。
用的是 `youtube-nocookie.com`。

`chapters` 的秒數會變成兩件事：頁面上可點的章節（點了從那秒開始播），
以及 `schema.org` 的 `Clip` 標記 — 這是讓 Google 在搜尋結果直接顯示「影片章節」的東西。
記得 YouTube 影片描述欄也要貼一份同樣的時間軸，兩邊都要有才會生效。

## SEO 已經內建

- 三個語言各自獨立網址 + 互相的 `hreflang` + `x-default`（用 JS 切語言只會收錄一種）
- `schema.org` 的 `Person`、`ScholarlyArticle`、`VideoObject`、`Clip`
- `canonical`、Open Graph、Twitter card
- `sitemap.xml` 與 `robots.txt`

上線後到 Google Search Console 提交 `sitemap.xml`。

## 引用數

頁面不自己顯示引用數，交給側欄的 Google Scholar 連結
（`scholar.google.com/citations?user=PiuFUZ8AAAAJ`）。Scholar 的計數永遠是最新的，
而且收錄範圍比第三方 API 廣，自己再放一個比較小的數字只會互相打架。

要放回來就在 `content.json` 的 `counts` 加回 `citations`，`refresh_metrics.py` 會重新開始抓。

## 數字每天自動更新

`.github/workflows/refresh-metrics.yml` 每天台北時間凌晨 03:17 在 GitHub 上跑一次：
抓引用數與 Zenodo 的瀏覽／下載，重新 build，**只有數字真的變了才 commit**，
Pages 接著自動重新部署。Actions 頁面也有 Run workflow 按鈕可以手動觸發。

改成每週一次就把 cron 換成 `17 19 * * 1`。引用數本來就動得慢，每週其實夠用。

數字是 build 時寫進 HTML 的，不是在訪客瀏覽器裡抓的 —— 靜態頁面那樣做會有 CORS 問題、
每個訪客都打一次 API，而且爬蟲看不到數字。

## 手動更新引用數

```bash
python3 refresh_metrics.py && python3 build.py
```

從 Semantic Scholar 取每篇的引用數並寫回 `content.json`。寫死的數字會過期，所以改內容時順手跑一次。

## 重新產生 og.png

`og.html` 是分享預覽圖（1200×630）的原始檔，用網站同一套 token 和字型。改完跑：

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --hide-scrollbars --force-device-scale-factor=2 --virtual-time-budget=6000 \
  --window-size=1200,630 --screenshot=og.png file://$PWD/og.html
```

## 其他

- 深淺色主題跟隨系統，側欄有手動切換，選擇記在瀏覽器裡。
- 沒有任何建置工具或相依套件，只需要 Python 3。
- `preview/` 是給預覽工具用的副本，播放器是示意的，**不要部署這個目錄**。
