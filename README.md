# 深圳市鑫威凯科技有限公司 官网 / 鑫威凯科技 Website

> 纯静态、中英双语、零依赖的电子元器件供应商官网。
> Static, bilingual, dependency-free corporate website for a Shenzhen component supplier.

## 线上地址 / Live site

- 仓库 Repository：<https://github.com/ynz24522-creator/xinweikai-website>
- 线上地址 Live：<https://ynz24522-creator.github.io/xinweikai-website/>

## 特性 / Highlights

| 中文 | English |
| --- | --- |
| 8 个静态页面，双击 `index.html` 即可浏览，无需构建、无外部 CDN | 8 static pages, open `index.html` directly - no build step, no CDN |
| 中英双语切换（默认中文，`?lang=en` 分享英文链接） | Chinese / English switch (Chinese by default, share with `?lang=en`) |
| 收录 22 个大类、119 个小类、939 个型号 | 22 categories, 119 sub-categories, 939 part numbers |
| 全站即时搜索：型号 / 封装 / 品牌 / 分类关键词，下拉分组 + 高亮 | Instant site-wide search across model, package, brand and category with grouping and highlighting |
| 产品中心支持分类树 + 品牌 / 封装筛选，筛选状态写入 URL | Category tree plus brand / package filters, filters encoded in the URL |
| 询价清单：逐行加入型号、填数量备注、一键生成邮件或复制文本发微信 | Inquiry list: add parts, set quantity and notes, generate an email or copy text for WeChat |
| 响应式布局（手机导航抽屉、表格转卡片流）、可打印、无障碍友好 | Responsive layout, mobile drawer, card-style tables on phones, print friendly, a11y touches |
| 图片为内联 SVG 线稿与 CSS 渐变，整套站点资源 < 300KB | All artwork is inline SVG line art and CSS gradients; total asset weight under 300KB |

## 页面 / Pages

| 文件 File | 中文 | English |
| --- | --- | --- |
| `index.html` | 首页 | Home |
| `products.html` | 产品中心 | Products |
| `category.html` | 分类详情（`?cat=resistors`） | Category detail (`?cat=resistors`) |
| `brands.html` | 品牌合作 | Brands |
| `about.html` | 关于我们 | About |
| `contact.html` | 联系我们 | Contact |
| `inquiry.html` | 询价清单 | Inquiry list |
| `404.html` | 404 页 | Not found |

## 本地预览 / Local preview

直接双击 `index.html`；或在目录下执行 `python3 -m http.server` 后访问 <http://localhost:8000/>。

Open `index.html` directly, or serve the folder with any static server.

> 提示：`file://` 协议下部分浏览器禁用 `localStorage`，此时语言偏好与询价清单只在当前页面有效；部署到 http(s) 后功能完整，代码已做降级处理。

## 目录结构 / Layout

```
.
├── index.html … 404.html          8 个页面 / the 8 pages
├── assets/
│   ├── css/style.css              全站样式与设计变量
│   ├── js/data.js                 公司信息 + 分类 + 型号数据（唯一数据源）
│   ├── js/i18n.js                 中英文字典
│   ├── js/app.js                  渲染、搜索、筛选、询价清单
│   └── img/favicon.svg
├── docs/                          使用说明与数据说明
├── sitemap.xml / robots.txt       SEO
└── .nojekyll                      GitHub Pages：跳过 Jekyll
```

## 联系方式 / Company

- 公司：深圳市鑫威凯科技有限公司
- 负责人：张维群
- 电话 / 微信：13926520605
- QQ：17317103
- 邮箱：17317103@qq.com
- 地址：深圳市福田区中航路都会电子城 2C030

站内型号与参数为行业通用资料，实际库存与报价请以电话 / 微信确认为准。
