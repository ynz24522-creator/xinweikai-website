# -*- coding: utf-8 -*-
"""Static site generator for the Xinweikai Technology website.

Run:  python3 build.py
Output: ../../outputs/xinweikai-website/
No third-party dependency, no build tooling on the consumer side.
"""

import json
import os
import shutil

import catalog
import icons

HERE = os.path.dirname(os.path.abspath(__file__))


def resolve_out(here):
    """Support both the authoring layout (work/build/) and the shipped layout
    (site/tools/) so the generator can be run from either place."""
    parent = os.path.dirname(here)
    if os.path.isfile(os.path.join(parent, "index.html")):
        return parent
    return os.path.join(os.path.dirname(parent), "outputs", "xinweikai-website")


OUT = resolve_out(HERE)
SCRIPT_LABEL = os.path.basename(HERE) + "/build.py"

BASE_URL = "https://ynz24522-creator.github.io/xinweikai-website/"

COMPANY = {
    "nameZh": "深圳市鑫威凯科技有限公司",
    "nameEn": "Shenzhen Xinweikai Technology",
    "shortZh": "鑫威凯科技",
    "shortEn": "Xinweikai Technology",
    "personZh": "张维群",
    "personEn": "Zhang Weiqun",
    "phone": "13926520605",
    "wechat": "13926520605",
    "qq": "17317103",
    "email": "17317103@qq.com",
    "addressZh": "深圳市福田区中航路都会电子城 2C030",
    "addressEn": "2C030 Duhui Electronics City, Zhonghang Road, Futian District, Shenzhen",
    "marketZh": "都会电子城 2C030",
    "marketEn": "Duhui Electronics City 2C030",
    "regionZh": "广东省深圳市福田区",
    "regionEn": "Futian District, Shenzhen, Guangdong",
    "updated": "2026-09",
}

CATEGORIES, TOTAL_PARTS, TOTAL_SUBS = catalog.build_catalog()

NAV = [
    ("index.html", "nav.home"),
    ("products.html", "nav.products"),
    ("brands.html", "nav.brands"),
    ("about.html", "nav.about"),
    ("contact.html", "nav.contact"),
]

I18N = {
    "zh": {
        "a11y.skip": "跳到主要内容",
        "a11y.menu": "打开导航菜单",
        "brand.short": "鑫威凯科技",
        "brand.sub": "Xinweikai Technology",
        "nav.home": "首页",
        "nav.products": "产品中心",
        "nav.brands": "品牌合作",
        "nav.about": "关于我们",
        "nav.contact": "联系我们",
        "nav.inquiry": "询价清单",
        "search.label": "搜索产品",
        "search.placeholder": "搜索型号 / 分类 / 品牌，例如 0603、STM32、电阻",
        "search.button": "搜索",
        "search.groupCategories": "分类",
        "search.groupParts": "型号",
        "search.groupBrands": "品牌",
        "search.viewAll": "查看全部 {n} 条结果",
        "search.emptyTitle": "没有找到匹配的型号",
        "search.emptyText": "换个关键词试试，例如 0603、SS34、STM32、电阻，或者直接联系我们报价。",
        "search.emptyCta": "联系我们询价",
        "footer.catsTitle": "热门分类",
        "footer.contactTitle": "联系方式",
        "footer.about": "电子元器件现货供应与 BOM 配单服务，覆盖常用料号，支持小批量与量产备料。",
        "footer.icp": "粤ICP备XXXXXXXX号（备案完成后替换）",
        "footer.note": "站内型号与参数为行业通用资料，实际库存与报价请以电话 / 微信确认为准。",
        "common.call": "拨打电话",
        "common.copy": "复制",
        "common.copied": "已复制",
        "common.wechat": "微信 / 同手机号",
        "common.qq": "QQ",
        "common.email": "邮箱",
        "common.address": "地址",
        "common.person": "负责人",
        "common.addInquiry": "加入询价",
        "common.added": "已加入",
        "common.copyModel": "复制型号",
        "common.more": "加载更多",
        "common.all": "全部",
        "common.reset": "重置筛选",
        "common.category": "分类",
        "common.brand": "品牌",
        "common.package": "封装",
        "common.model": "型号",
        "common.params": "关键参数",
        "common.desc": "说明",
        "common.actions": "操作",
        "common.results": "共 {n} 个型号",
        "common.disclaimer": "型号与参数为行业通用资料，实际库存、价格与交期请以电话 / 微信确认为准。",
        "hero.eyebrow": "深圳市福田区中航路都会电子城 2C030",
        "hero.title": "电子元器件现货供应",
        "hero.titleAccent": "一站式配单，最快找到你要的料",
        "hero.sub": "电阻、电容、IC、模块、连接器、工具耗材全品类覆盖，常用料号现货直发，支持 BOM 逐行核对与替代选型。",
        "hero.ctaProducts": "浏览产品中心",
        "hero.ctaInquiry": "立即询价",
        "hero.searchLabel": "直接搜索型号或品类",
        "hero.hint": "例如：0603 100nF、SS34、STM32F103C8T6、Type-C 母座",
        "stat.categories": "产品大类",
        "stat.subs": "细分小类",
        "stat.parts": "常备型号",
        "stat.service": "现货直发 / 当天可发",
        "home.catEyebrow": "产品体系",
        "home.catTitle": "按立创商城式分类，一站式找齐",
        "home.catLead": "22 个大类、{subs} 个小类，覆盖研发、维修与量产常用料号；点进分类查看型号、封装与关键参数。",
        "home.catMore": "进入产品中心",
        "home.hotEyebrow": "常备型号",
        "home.hotTitle": "华强北现货高频料号",
        "home.hotLead": "以下是客户问得最多的型号，可直接加入询价清单，也可以告诉我们数量，我们给你报价。",
        "home.serviceEyebrow": "服务能力",
        "home.serviceTitle": "不只是卖料，更帮你把单配齐",
        "home.brandEyebrow": "常备品牌",
        "home.brandTitle": "合作与常备品牌",
        "home.brandLead": "具体品牌授权情况以实际为准，出货前可核对批次与包装。",
        "home.contactTitle": "有需求？一个电话 / 一条微信就能报价",
        "home.contactLead": "说清型号与数量，我们尽快回复价格、库存与替代方案。",
        "products.title": "产品中心",
        "products.lead": "共 {parts} 个型号，支持按型号、封装、品牌与分类检索。",
        "products.searchPlaceholder": "输入型号或关键词，例如 SS34、0603、PC817",
        "products.empty": "没有匹配的型号，试试放宽筛选条件或直接联系我们。",
        "products.catList": "分类目录",
        "products.all": "全部型号",
        "category.tips": "选型要点",
        "category.subs": "小类",
        "category.back": "返回产品中心",
        "category.scopeSearch": "在本分类内查找",
        "brands.title": "品牌合作",
        "brands.lead": "以下品牌为我司常备与常用合作品牌，覆盖被动元件、分立器件、IC 与连接器；具体授权与批次请以实际出货文件为准。",
        "brands.noteTitle": "关于品牌授权的说明",
        "brands.note": "本站品牌信息用于说明常备货源方向，不代表全部为原厂授权代理。需要品牌授权书、原厂包装或指定批次时，请在询价时注明，我们会如实告知可行方案。",
        "brands.catCount": "涉及 {n} 个分类",
        "brands.partsCount": "{n} 个型号",
        "about.title": "关于我们",
        "about.lead": "华强北电子元器件现货供应商，专注「多品种、小批量、要货急」的配单需求。",
        "about.rangeTitle": "主营范围",
        "about.rangeLead": "覆盖下列分类的常用料号，也可按 BOM 逐行核对配齐。",
        "about.promiseTitle": "服务承诺",
        "about.promiseLead": "把话说清楚，把料配齐，是我们做长期生意的方式。",
        "about.warehouseTitle": "仓库与柜台",
        "about.warehouseText": "公司与柜台位于深圳市福田区中航路都会电子城 2C030，紧邻华强北元器件商圈，便于当天取货与快速配单。上门取货请先电话或微信确认库存与时间。",
        "about.dataTitle": "数据说明",
        "about.dataText": "站内 22 个大类、{subs} 个小类、{parts} 个型号的参数为行业通用资料，用于帮助你快速定位所需品类；具体品牌、批次、包装与价格以询价回复为准。",
        "about.contactTitle": "联系我们",
        "contact.title": "联系我们",
        "contact.lead": "电话、微信、QQ 与邮箱均可下单询价，说清型号与数量，回复更快。",
        "contact.hoursHint": "上门取货请提前电话或微信确认库存与时间。",
        "contact.mapTitle": "门店位置",
        "contact.mapAmap": "在高德地图中查看",
        "contact.mapBaidu": "在百度地图中查看",
        "contact.askTitle": "询价时建议提供",
        "contact.ask1": "型号 / 规格与品牌要求",
        "contact.ask2": "数量（样品或量产）",
        "contact.ask3": "封装、包装形式与是否有替代空间",
        "contact.ask4": "是否需要开票与对公付款",
        "inquiry.title": "询价清单",
        "inquiry.lead": "把需要的型号加进清单，填好数量与备注，一键生成邮件或复制文本发微信。",
        "inquiry.empty": "清单还是空的，去产品中心搜索型号并点「加入询价」吧。",
        "inquiry.emptyCta": "去搜索型号",
        "inquiry.qty": "数量",
        "inquiry.remark": "备注",
        "inquiry.remove": "删除",
        "inquiry.clear": "清空清单",
        "inquiry.mail": "生成询价邮件",
        "inquiry.copy": "复制询价内容",
        "inquiry.formTitle": "你的联系方式",
        "inquiry.company": "公司名称",
        "inquiry.person": "联系人",
        "inquiry.tel": "电话 / 微信",
        "inquiry.remarkAll": "其他要求",
        "inquiry.note": "生成邮件会调用本机默认邮件客户端，收件人 {email}；若不方便发邮件，点「复制询价内容」后直接发微信或 QQ 也可以。",
        "inquiry.savedHint": "清单保存在本机浏览器中，刷新或关闭页面都不会丢失。",
        "inquiry.needContact": "请至少填写电话 / 微信，方便我们回复报价。",
        "notfound.title": "页面没有找到",
        "notfound.lead": "你访问的页面可能已移动或链接有误。可以直接搜索产品，或从下面的常用入口进入。",
        "notfound.cta": "回到首页",
        "meta.home": "电子元器件现货供应 · 电阻电容 IC 模块 连接器",
        "meta.products": "产品中心 · 22 大类元器件型号查询",
        "meta.category": "产品分类",
        "meta.brands": "常备与常用合作品牌",
        "meta.about": "华强北电子元器件现货供应商",
        "meta.contact": "电话 13926520605 · 都会电子城 2C030",
        "meta.inquiry": "询价清单 · 一键生成询价邮件",
        "meta.404": "页面没有找到",
    },
    "en": {
        "a11y.skip": "Skip to main content",
        "a11y.menu": "Open navigation menu",
        "brand.short": "Xinweikai Technology",
        "brand.sub": "电子元器件现货供应",
        "nav.home": "Home",
        "nav.products": "Products",
        "nav.brands": "Brands",
        "nav.about": "About",
        "nav.contact": "Contact",
        "nav.inquiry": "Inquiry list",
        "search.label": "Search products",
        "search.placeholder": "Search model, category or brand, e.g. 0603, STM32, resistor",
        "search.button": "Search",
        "search.groupCategories": "Categories",
        "search.groupParts": "Part numbers",
        "search.groupBrands": "Brands",
        "search.viewAll": "View all {n} results",
        "search.emptyTitle": "No matching part",
        "search.emptyText": "Try another keyword such as 0603, SS34, STM32 or resistor, or contact us for a quote.",
        "search.emptyCta": "Contact us",
        "footer.catsTitle": "Popular categories",
        "footer.contactTitle": "Contact",
        "footer.about": "Electronic components from stock plus BOM kitting, covering everyday part numbers in small and production quantities.",
        "footer.icp": "ICP licence placeholder (to be replaced)",
        "footer.note": "Part numbers and parameters are industry-generic references. Actual stock and pricing are confirmed by phone or WeChat.",
        "common.call": "Call",
        "common.copy": "Copy",
        "common.copied": "Copied",
        "common.wechat": "WeChat / same as mobile",
        "common.qq": "QQ",
        "common.email": "Email",
        "common.address": "Address",
        "common.person": "Contact person",
        "common.addInquiry": "Add to inquiry",
        "common.added": "Added",
        "common.copyModel": "Copy model",
        "common.more": "Load more",
        "common.all": "All",
        "common.reset": "Reset filters",
        "common.category": "Category",
        "common.brand": "Brand",
        "common.package": "Package",
        "common.model": "Model",
        "common.params": "Key parameters",
        "common.desc": "Type",
        "common.actions": "Actions",
        "common.results": "{n} part numbers",
        "common.disclaimer": "Part numbers and parameters are industry references; confirm stock, price and lead time by phone or WeChat.",
        "hero.eyebrow": "2C030 Duhui Electronics City, Zhonghang Road, Futian, Shenzhen",
        "hero.title": "Electronic components from stock",
        "hero.titleAccent": "One-stop kitting - find your part fast",
        "hero.sub": "Resistors, capacitors, ICs, modules, connectors, tools and consumables. Common parts ship the same day, with line-by-line BOM checking and alternative suggestions.",
        "hero.ctaProducts": "Browse products",
        "hero.ctaInquiry": "Request a quote",
        "hero.searchLabel": "Search a model or category",
        "hero.hint": "e.g. 0603 100nF, SS34, STM32F103C8T6, Type-C receptacle",
        "stat.categories": "Product categories",
        "stat.subs": "Sub-categories",
        "stat.parts": "Listed part numbers",
        "stat.service": "Stock shipping same day",
        "home.catEyebrow": "Catalogue",
        "home.catTitle": "An LCSC-style tree - everything in one place",
        "home.catLead": "22 categories and {subs} sub-categories covering everyday R&D, repair and production parts. Open a category for models, packages and key parameters.",
        "home.catMore": "Open product centre",
        "home.hotEyebrow": "Stock favourites",
        "home.hotTitle": "Huaqiangbei's most requested part numbers",
        "home.hotLead": "These are the parts customers ask for most. Add them to your inquiry list, or send quantities and we will quote.",
        "home.serviceEyebrow": "Capabilities",
        "home.serviceTitle": "More than parts - we complete the order",
        "home.brandEyebrow": "Brands",
        "home.brandTitle": "Stocked and partner brands",
        "home.brandLead": "Authorisation varies by line; batch and packaging can be verified before shipment.",
        "home.contactTitle": "Need a quote? One call or message is enough",
        "home.contactLead": "Send the model and quantity, and we will reply with price, stock and alternatives.",
        "products.title": "Products",
        "products.lead": "{parts} part numbers, searchable by model, package, brand and category.",
        "products.searchPlaceholder": "Type a model or keyword, e.g. SS34, 0603, PC817",
        "products.empty": "No matching part. Loosen the filters or contact us directly.",
        "products.catList": "Category tree",
        "products.all": "All parts",
        "category.tips": "Selection notes",
        "category.subs": "Sub-categories",
        "category.back": "Back to products",
        "category.scopeSearch": "Search within this category",
        "brands.title": "Brands",
        "brands.lead": "These are the brands we commonly stock and work with across passives, discretes, ICs and connectors. Authorisation and batch details follow the actual shipment documents.",
        "brands.noteTitle": "About brand authorisation",
        "brands.note": "Brand names here describe our usual supply directions and do not mean every line is an original-authorised franchise. If you need authorisation letters, original packaging or a specific batch, tell us at inquiry and we will confirm honestly.",
        "brands.catCount": "Used in {n} categories",
        "brands.partsCount": "{n} part numbers",
        "about.title": "About us",
        "about.lead": "A Huaqiangbei component supplier focused on many-lines, small-quantity, urgent orders.",
        "about.rangeTitle": "What we supply",
        "about.rangeLead": "Everyday part numbers across the categories below, matched line by line against your BOM.",
        "about.promiseTitle": "Our commitments",
        "about.promiseLead": "Clear answers and complete orders are how we build long-term business.",
        "about.warehouseTitle": "Counter & stock",
        "about.warehouseText": "Our counter is at 2C030, Duhui Electronics City, Zhonghang Road, Futian District, Shenzhen, inside the Huaqiangbei component district - convenient for same-day pickup and fast kitting. Please confirm stock and timing by phone or WeChat before visiting.",
        "about.dataTitle": "About the data",
        "about.dataText": "The parameters of 22 categories, {subs} sub-categories and {parts} part numbers are industry-generic references to help you locate the right family quickly. Brand, batch, packaging and price are confirmed in the quotation.",
        "about.contactTitle": "Contact",
        "contact.title": "Contact us",
        "contact.lead": "Phone, WeChat, QQ or email - send the model and quantity for the fastest reply.",
        "contact.hoursHint": "For pickup, please confirm stock and timing by phone or WeChat first.",
        "contact.mapTitle": "Location",
        "contact.mapAmap": "Open in Amap",
        "contact.mapBaidu": "Open in Baidu Maps",
        "contact.askTitle": "Helpful details for a quote",
        "contact.ask1": "Model / specification and brand preference",
        "contact.ask2": "Quantity (sample or production)",
        "contact.ask3": "Package, packing style and whether alternatives are acceptable",
        "contact.ask4": "Whether you need an invoice and corporate payment",
        "inquiry.title": "Inquiry list",
        "inquiry.lead": "Add the parts you need, set quantity and notes, then generate an email or copy the text to WeChat.",
        "inquiry.empty": "Your list is empty. Search in the product centre and press “Add to inquiry”.",
        "inquiry.emptyCta": "Search parts",
        "inquiry.qty": "Qty",
        "inquiry.remark": "Remark",
        "inquiry.remove": "Remove",
        "inquiry.clear": "Clear list",
        "inquiry.mail": "Generate email",
        "inquiry.copy": "Copy inquiry text",
        "inquiry.formTitle": "Your contact details",
        "inquiry.company": "Company",
        "inquiry.person": "Contact person",
        "inquiry.tel": "Phone / WeChat",
        "inquiry.remarkAll": "Other requirements",
        "inquiry.note": "Generating the email opens your default mail client addressed to {email}. If email is inconvenient, copy the inquiry text and send it by WeChat or QQ.",
        "inquiry.savedHint": "The list is stored in this browser, so it survives a refresh.",
        "inquiry.needContact": "Please fill in at least a phone or WeChat number so we can reply.",
        "notfound.title": "Page not found",
        "notfound.lead": "The page may have moved or the link is wrong. Search for a part, or use one of the shortcuts below.",
        "notfound.cta": "Back to home",
        "meta.home": "Electronic components from stock - resistors, capacitors, ICs, modules, connectors",
        "meta.products": "Products - 22 component categories with model lookup",
        "meta.category": "Product category",
        "meta.brands": "Stocked and partner brands",
        "meta.about": "Huaqiangbei electronic component supplier",
        "meta.contact": "Tel 13926520605 - Duhui Electronics City 2C030",
        "meta.inquiry": "Inquiry list - generate a quote request email",
        "meta.404": "Page not found",
    },
}


def page_head(page, title_key, desc_key):
    """Build <head> contents. Every page carries the same SEO scaffolding."""
    zh = I18N["zh"]
    en = I18N["en"]
    title = "%s | %s" % (zh[title_key], COMPANY["shortZh"])
    desc = zh[desc_key]
    jsonld = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": COMPANY["nameZh"],
        "alternateName": COMPANY["shortZh"],
        "description": zh["meta.home"],
        "telephone": COMPANY["phone"],
        "email": COMPANY["email"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "中航路都会电子城 2C030",
            "addressLocality": "深圳市",
            "addressRegion": "广东省",
            "addressCountry": "CN",
        },
        "areaServed": "CN",
        "knowsAbout": [c["zh"] for c in CATEGORIES],
        "url": BASE_URL,
    }
    return """<meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="keywords" content="电子元器件,现货,华强北,都会电子城,电阻,电容,IC,模块,连接器,{short}">
  <meta name="theme-color" content="#0f3d75">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{name}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{url}{page}">
  <meta name="twitter:card" content="summary">
  <link rel="icon" type="image/svg+xml" href="assets/img/favicon.svg">
  <link rel="stylesheet" href="assets/css/style.css">
  <script type="application/ld+json">{jsonld}</script>""".format(
        title=title,
        desc=desc,
        short=COMPANY["shortZh"],
        name=COMPANY["nameZh"],
        url=BASE_URL,
        page="" if page == "index.html" else page,
        jsonld=json.dumps(jsonld, ensure_ascii=False, separators=(",", ":")),
    )


def icon_svg(name):
    return icons.service_icon(name)


SEARCH_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
               'stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/>'
               '<path d="M16.5 16.5L21 21"/></svg>')


def header(page):
    links = []
    for href, key in NAV:
        current = ' aria-current="page"' if href == page else ""
        links.append('<a href="%s" data-i18n="%s"%s>%s</a>' % (href, key, current, I18N["zh"][key]))
    return """<header class="site-header" data-header>
    <div class="container header-inner">
      <a class="brand" href="index.html">
        {logo}
        <span class="brand-text">
          <b data-i18n="brand.short">{short}</b>
          <span data-i18n="brand.sub">{subEn}</span>
        </span>
      </a>
      <form class="search" role="search" data-search-form autocomplete="off">
        <label class="sr-only" for="site-search" data-i18n="search.label">搜索产品</label>
        <input id="site-search" class="search-input" type="search" data-search-input
               placeholder="{ph}" data-i18n-placeholder="search.placeholder">
        <button class="search-submit" type="submit" data-i18n-title="search.button"
                aria-label="搜索">{searchIcon}</button>
        <div class="search-panel" data-search-panel hidden></div>
      </form>
      <nav class="nav" data-nav aria-label="主导航">
        {links}
      </nav>
      <div class="header-tools">
        <div class="lang-switch" role="group" aria-label="Language / 语言">
          <button type="button" data-lang-btn="zh" aria-pressed="true">中文</button>
          <button type="button" data-lang-btn="en" aria-pressed="false">EN</button>
        </div>
        <a class="btn btn-primary btn-sm inquiry-btn" href="inquiry.html">
          <span data-i18n="nav.inquiry">询价清单</span>
          <span class="inquiry-count" data-inquiry-count hidden>0</span>
        </a>
        <button class="menu-toggle" type="button" data-menu-toggle aria-expanded="false"
                aria-label="菜单" data-i18n-title="a11y.menu"><span></span></button>
      </div>
    </div>
  </header>""".format(
        logo=icons.LOGO,
        short=I18N["zh"]["brand.short"],
        subEn=COMPANY["shortEn"],
        ph=I18N["zh"]["search.placeholder"],
        searchIcon=SEARCH_ICON,
        links="\n        ".join(links),
    )


def footer():
    top_cats = CATEGORIES[:8]
    cat_links = "\n        ".join(
        '<a href="category.html?cat=%s" data-cat-name="%s">%s</a>' % (c["id"], c["id"], c["zh"])
        for c in top_cats
    )
    return """<footer class="site-footer">
    <div class="container footer-grid">
      <div class="footer-brand">
        <a class="brand brand--footer" href="index.html">
          {logo}
          <span class="brand-text"><b>{short}</b><span>{subEn}</span></span>
        </a>
        <p data-i18n="footer.about">{about}</p>
        <p class="footer-note" data-i18n="footer.note">{note}</p>
      </div>
      <div class="footer-col">
        <h4 data-i18n="footer.catsTitle">热门分类</h4>
        <div class="footer-links">
        {catLinks}
        </div>
      </div>
      <div class="footer-col">
        <h4 data-i18n="footer.contactTitle">联系方式</h4>
        <ul class="footer-contact">
          <li><span data-i18n="common.person">负责人</span>：{person}</li>
          <li><span data-i18n="common.call">拨打电话</span>：
            <a href="tel:{phone}">{phone}</a></li>
          <li><span data-i18n="common.wechat">微信 / 同手机号</span>：{phone}</li>
          <li><span data-i18n="common.qq">QQ</span>：{qq}</li>
          <li><span data-i18n="common.email">邮箱</span>：
            <a href="mailto:{email}">{email}</a></li>
          <li><span data-i18n="common.address">地址</span>：{address}</li>
        </ul>
      </div>
    </div>
    <div class="container footer-bottom">
      <span>© <span data-year>2026</span> {name}</span>
      <span class="footer-icp" data-i18n="footer.icp">粤ICP备XXXXXXXX号（备案完成后替换）</span>
    </div>
  </footer>""".format(
        logo=icons.LOGO,
        short=COMPANY["shortZh"],
        subEn=COMPANY["shortEn"],
        about=I18N["zh"]["footer.about"],
        note=I18N["zh"]["footer.note"],
        catLinks=cat_links,
        person=COMPANY["personZh"],
        phone=COMPANY["phone"],
        qq=COMPANY["qq"],
        email=COMPANY["email"],
        address=COMPANY["addressZh"],
        name=COMPANY["nameZh"],
    )


def drawer_and_scripts():
    return """<div class="drawer-backdrop" data-drawer-backdrop hidden></div>
  <div class="toast" data-toast hidden></div>
  <script src="assets/js/data.js"></script>
  <script src="assets/js/i18n.js"></script>
  <script src="assets/js/app.js"></script>"""


def page(filename, page_id, title_key, desc_key, content):
    return """<!DOCTYPE html>
<html lang="zh-CN" data-lang="zh">
<head>
  {head}
</head>
<body data-page="{page_id}">
  <a class="skip-link" href="#main" data-i18n="a11y.skip">跳到主要内容</a>
  {header}
  <main id="main">
{content}
  </main>
  {footer}
  {scripts}
</body>
</html>
""".format(
        head=page_head(page_id, title_key, desc_key),
        page_id=page_id,
        header=header(filename),
        content=content,
        footer=footer(),
        scripts=drawer_and_scripts(),
    )


def t(key):
    return I18N["zh"][key]


def stat_card(label_key, value):
    return ('<div class="stat-card"><b>%s</b><span data-i18n="%s">%s</span></div>'
            % (value, label_key, t(label_key)))


def hero_search_form():
    return """<form class="hero-search-form" role="search" data-search-form autocomplete="off">
            <span class="hero-search-icon">{icon}</span>
            <input type="search" class="hero-search-input" data-search-input
                   aria-label="搜索产品" data-i18n-aria="hero.searchLabel"
                   placeholder="{ph}" data-i18n-placeholder="search.placeholder">
            <button type="submit" class="btn btn-primary hero-search-btn" data-i18n="search.button">搜索</button>
            <div class="search-panel search-panel--hero" data-search-panel hidden></div>
          </form>""".format(icon=SEARCH_ICON, ph=t("search.placeholder"))


def home_content():
    return """    <section class="hero">
      <div class="hero-bg" aria-hidden="true"></div>
      <div class="container hero-inner">
        <div class="hero-copy">
          <span class="eyebrow" data-i18n="hero.eyebrow">{eyebrow}</span>
          <h1 class="hero-title">
            <span data-i18n="hero.title">{title}</span>
            <span class="accent" data-i18n="hero.titleAccent">{accent}</span>
          </h1>
          <p class="hero-sub" data-i18n="hero.sub">{sub}</p>
          <div class="hero-actions">
            <a class="btn btn-primary btn-lg" href="products.html" data-i18n="hero.ctaProducts">{cta1}</a>
            <a class="btn btn-ghost btn-lg" href="inquiry.html" data-i18n="hero.ctaInquiry">{cta2}</a>
          </div>
          <div class="hero-search">
            {searchForm}
            <p class="hero-hint" data-i18n="hero.hint">{hint}</p>
          </div>
        </div>
        <div class="hero-visual">{art}</div>
      </div>
      <div class="container">
        <div class="hero-stats">
          {s1}
          {s2}
          {s3}
          {s4}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow" data-i18n="home.catEyebrow">{catEyebrow}</span>
          <h2 data-i18n="home.catTitle">{catTitle}</h2>
          <p class="lead" data-i18n="home.catLead">{catLead}</p>
        </div>
        <div class="cat-grid" data-cat-grid></div>
        <div class="section-more">
          <a class="btn btn-outline" href="products.html" data-i18n="home.catMore">{catMore}</a>
        </div>
      </div>
    </section>

    <section class="section section--soft">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow" data-i18n="home.hotEyebrow">{hotEyebrow}</span>
          <h2 data-i18n="home.hotTitle">{hotTitle}</h2>
          <p class="lead" data-i18n="home.hotLead">{hotLead}</p>
        </div>
        <div class="table-wrap table-wrap--parts" data-hot-table></div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow" data-i18n="home.serviceEyebrow">{svcEyebrow}</span>
          <h2 data-i18n="home.serviceTitle">{svcTitle}</h2>
        </div>
        <div class="service-grid" data-service-grid></div>
      </div>
    </section>

    <section class="section section--soft">
      <div class="container">
        <div class="section-head section-head--split">
          <div>
            <span class="eyebrow" data-i18n="home.brandEyebrow">{brandEyebrow}</span>
            <h2 data-i18n="home.brandTitle">{brandTitle}</h2>
          </div>
          <p class="lead lead--tight" data-i18n="home.brandLead">{brandLead}</p>
        </div>
        <div class="brand-strip" data-brand-strip></div>
        <div class="section-more">
          <a class="btn btn-outline" href="brands.html" data-i18n="nav.brands">{navBrands}</a>
        </div>
      </div>
    </section>

    <section class="section contact-band">
      <div class="container contact-band-inner">
        <div>
          <h2 data-i18n="home.contactTitle">{contactTitle}</h2>
          <p class="lead" data-i18n="home.contactLead">{contactLead}</p>
        </div>
        <div class="contact-band-actions">
          <a class="btn btn-primary btn-lg" href="tel:{phone}">{phone} · <span data-i18n="common.call">拨打电话</span></a>
          <a class="btn btn-ghost btn-lg" href="contact.html" data-i18n="nav.contact">{navContact}</a>
        </div>
      </div>
    </section>""".format(
        eyebrow=t("hero.eyebrow"),
        title=t("hero.title"),
        accent=t("hero.titleAccent"),
        sub=t("hero.sub"),
        cta1=t("hero.ctaProducts"),
        cta2=t("hero.ctaInquiry"),
        searchForm=hero_search_form(),
        hint=t("hero.hint"),
        art=icons.HERO_BOARD,
        s1=stat_card("stat.categories", len(CATEGORIES)),
        s2=stat_card("stat.subs", TOTAL_SUBS),
        s3=stat_card("stat.parts", TOTAL_PARTS),
        s4=stat_card("stat.service", "24h"),
        catEyebrow=t("home.catEyebrow"),
        catTitle=t("home.catTitle"),
        catLead=t("home.catLead").format(subs=TOTAL_SUBS),
        catMore=t("home.catMore"),
        hotEyebrow=t("home.hotEyebrow"),
        hotTitle=t("home.hotTitle"),
        hotLead=t("home.hotLead"),
        svcEyebrow=t("home.serviceEyebrow"),
        svcTitle=t("home.serviceTitle"),
        brandEyebrow=t("home.brandEyebrow"),
        brandTitle=t("home.brandTitle"),
        brandLead=t("home.brandLead"),
        contactTitle=t("home.contactTitle"),
        contactLead=t("home.contactLead"),
        navBrands=t("nav.brands"),
        navContact=t("nav.contact"),
        phone=COMPANY["phone"],
    )


def products_content():
    return """    <section class="page-head">
      <div class="container">
        <nav class="breadcrumb" aria-label="breadcrumb">
          <a href="index.html" data-i18n="nav.home">{home}</a><span>/</span>
          <span data-i18n="products.title">{title}</span>
        </nav>
        <h1 data-i18n="products.title">{title}</h1>
        <p class="lead" data-i18n="products.lead">{lead}</p>
      </div>
    </section>
    <section class="section section--tight">
      <div class="container products-layout">
        <aside class="cat-sidebar">
          <h2 class="sidebar-title" data-i18n="products.catList">{catList}</h2>
          <div class="cat-tree" data-cat-tree></div>
        </aside>
        <div class="products-main">
          <div class="filter-bar">
            <div class="filter-search">
              <span class="filter-search-icon">{icon}</span>
              <input type="search" class="filter-input" data-filter-q
                     placeholder="{ph}" data-i18n-placeholder="products.searchPlaceholder">
            </div>
            <select class="filter-select" data-filter-brand aria-label="品牌"></select>
            <select class="filter-select" data-filter-pkg aria-label="封装"></select>
            <button type="button" class="btn btn-outline btn-sm" data-filter-reset
                    data-i18n="common.reset">{reset}</button>
          </div>
          <div class="filter-chips" data-active-filters></div>
          <div class="result-bar">
            <span data-result-count></span>
            <span class="result-hint" data-i18n="common.disclaimer">{disclaimer}</span>
          </div>
          <div class="table-wrap table-wrap--parts" data-results></div>
          <div class="load-more-wrap">
            <button type="button" class="btn btn-outline" data-load-more hidden
                    data-i18n="common.more">{more}</button>
          </div>
          <p class="empty-state" data-results-empty hidden data-i18n="products.empty">{empty}</p>
        </div>
      </div>
    </section>""".format(
        home=t("nav.home"),
        title=t("products.title"),
        lead=t("products.lead").format(parts=TOTAL_PARTS),
        catList=t("products.catList"),
        icon=SEARCH_ICON,
        ph=t("products.searchPlaceholder"),
        reset=t("common.reset"),
        disclaimer=t("common.disclaimer"),
        more=t("common.more"),
        empty=t("products.empty"),
    )


def category_content():
    return """    <section class="page-head">
      <div class="container" data-category-head>
        <nav class="breadcrumb" aria-label="breadcrumb">
          <a href="index.html" data-i18n="nav.home">{home}</a><span>/</span>
          <a href="products.html" data-i18n="products.title">{products}</a><span>/</span>
          <span data-category-name></span>
        </nav>
        <h1 data-category-title>—</h1>
        <p class="lead" data-category-blurb></p>
      </div>
    </section>
    <section class="section section--tight">
      <div class="container">
        <div class="category-body" data-category-body>
          <div class="tips-card">
            <h2 data-i18n="category.tips">{tips}</h2>
            <ul data-category-tips></ul>
          </div>
          <div class="filter-bar filter-bar--inline">
            <div class="filter-search">
              <span class="filter-search-icon">{icon}</span>
              <input type="search" class="filter-input" data-category-q
                     placeholder="{scope}" data-i18n-placeholder="category.scopeSearch">
            </div>
            <div class="sub-chips" data-sub-chips></div>
          </div>
          <div class="sub-sections" data-sub-sections></div>
        </div>
        <div class="category-footer">
          <a class="btn btn-outline" href="products.html" data-i18n="category.back">{back}</a>
        </div>
      </div>
    </section>""".format(
        home=t("nav.home"),
        products=t("products.title"),
        tips=t("category.tips"),
        icon=SEARCH_ICON,
        scope=t("category.scopeSearch"),
        back=t("category.back"),
    )


def brands_content():
    return """    <section class="page-head">
      <div class="container">
        <nav class="breadcrumb" aria-label="breadcrumb">
          <a href="index.html" data-i18n="nav.home">{home}</a><span>/</span>
          <span data-i18n="brands.title">{title}</span>
        </nav>
        <h1 data-i18n="brands.title">{title}</h1>
        <p class="lead" data-i18n="brands.lead">{lead}</p>
      </div>
    </section>
    <section class="section section--tight">
      <div class="container">
        <div class="brand-grid" data-brand-grid></div>
        <div class="note-card">
          <h2 data-i18n="brands.noteTitle">{noteTitle}</h2>
          <p data-i18n="brands.note">{note}</p>
        </div>
      </div>
    </section>""".format(
        home=t("nav.home"),
        title=t("brands.title"),
        lead=t("brands.lead"),
        noteTitle=t("brands.noteTitle"),
        note=t("brands.note"),
    )


def about_content():
    return """    <section class="page-head">
      <div class="container">
        <nav class="breadcrumb" aria-label="breadcrumb">
          <a href="index.html" data-i18n="nav.home">{home}</a><span>/</span>
          <span data-i18n="about.title">{title}</span>
        </nav>
        <h1 data-i18n="about.title">{title}</h1>
        <p class="lead" data-i18n="about.lead">{lead}</p>
      </div>
    </section>
    <section class="section section--tight">
      <div class="container about-grid">
        <div class="about-copy" data-about-profile></div>
        <div class="about-visual">{shelf}</div>
      </div>
    </section>
    <section class="section section--soft">
      <div class="container">
        <div class="section-head">
          <h2 data-i18n="about.rangeTitle">{rangeTitle}</h2>
          <p class="lead" data-i18n="about.rangeLead">{rangeLead}</p>
        </div>
        <div class="range-chips" data-range-chips></div>
      </div>
    </section>
    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2 data-i18n="about.promiseTitle">{promiseTitle}</h2>
          <p class="lead" data-i18n="about.promiseLead">{promiseLead}</p>
        </div>
        <div class="promise-list" data-promise-list></div>
      </div>
    </section>
    <section class="section section--soft">
      <div class="container two-col">
        <div class="info-card">
          <h2 data-i18n="about.warehouseTitle">{warehouseTitle}</h2>
          <p data-i18n="about.warehouseText">{warehouseText}</p>
          <p class="muted" data-i18n="contact.hoursHint">{hoursHint}</p>
        </div>
        <div class="info-card">
          <h2 data-i18n="about.dataTitle">{dataTitle}</h2>
          <p data-i18n="about.dataText">{dataText}</p>
        </div>
      </div>
    </section>
    <section class="section contact-band">
      <div class="container contact-band-inner">
        <div>
          <h2 data-i18n="about.contactTitle">{contactTitle}</h2>
          <p class="lead">{address}</p>
        </div>
        <div class="contact-band-actions">
          <a class="btn btn-primary btn-lg" href="tel:{phone}">{phone} · <span data-i18n="common.call">{call}</span></a>
          <a class="btn btn-ghost btn-lg" href="contact.html" data-i18n="nav.contact">{navContact}</a>
        </div>
      </div>
    </section>""".format(
        home=t("nav.home"),
        title=t("about.title"),
        lead=t("about.lead"),
        shelf=icons.SHELF_ART,
        rangeTitle=t("about.rangeTitle"),
        rangeLead=t("about.rangeLead"),
        promiseTitle=t("about.promiseTitle"),
        promiseLead=t("about.promiseLead"),
        warehouseTitle=t("about.warehouseTitle"),
        warehouseText=t("about.warehouseText"),
        hoursHint=t("contact.hoursHint"),
        dataTitle=t("about.dataTitle"),
        dataText=t("about.dataText").format(subs=TOTAL_SUBS, parts=TOTAL_PARTS),
        contactTitle=t("about.contactTitle"),
        address=COMPANY["addressZh"],
        phone=COMPANY["phone"],
        call=t("common.call"),
        navContact=t("nav.contact"),
    )


def map_links():
    q = COMPANY["addressZh"].replace(" ", "")
    from urllib.parse import quote
    return {
        "amap": "https://uri.amap.com/search?keyword=" + quote(q),
        "baidu": "https://map.baidu.com/search?query=" + quote(q),
    }


def contact_content():
    links = map_links()
    return """    <section class="page-head">
      <div class="container">
        <nav class="breadcrumb" aria-label="breadcrumb">
          <a href="index.html" data-i18n="nav.home">{home}</a><span>/</span>
          <span data-i18n="contact.title">{title}</span>
        </nav>
        <h1 data-i18n="contact.title">{title}</h1>
        <p class="lead" data-i18n="contact.lead">{lead}</p>
      </div>
    </section>
    <section class="section section--tight">
      <div class="container">
        <div class="contact-grid">
          <div class="contact-card contact-card--primary">
            <span class="contact-label" data-i18n="common.call">{call}</span>
            <a class="contact-value contact-value--phone" href="tel:{phone}">{phone}</a>
            <div class="contact-actions">
              <a class="btn btn-primary btn-sm" href="tel:{phone}" data-i18n="common.call">{call}</a>
              <button type="button" class="btn btn-outline btn-sm" data-copy="{phone}"
                      data-i18n="common.copy">{copy}</button>
            </div>
          </div>
          <div class="contact-card">
            <span class="contact-label" data-i18n="common.wechat">{wechat}</span>
            <span class="contact-value">{phone}</span>
            <div class="contact-actions">
              <button type="button" class="btn btn-outline btn-sm" data-copy="{phone}"
                      data-i18n="common.copy">{copy}</button>
            </div>
          </div>
          <div class="contact-card">
            <span class="contact-label" data-i18n="common.qq">{qqLabel}</span>
            <span class="contact-value">{qq}</span>
            <div class="contact-actions">
              <button type="button" class="btn btn-outline btn-sm" data-copy="{qq}"
                      data-i18n="common.copy">{copy}</button>
            </div>
          </div>
          <div class="contact-card">
            <span class="contact-label" data-i18n="common.email">{emailLabel}</span>
            <a class="contact-value" href="mailto:{email}">{email}</a>
            <div class="contact-actions">
              <button type="button" class="btn btn-outline btn-sm" data-copy="{email}"
                      data-i18n="common.copy">{copy}</button>
            </div>
          </div>
          <div class="contact-card">
            <span class="contact-label" data-i18n="common.person">{personLabel}</span>
            <span class="contact-value">{person}</span>
          </div>
          <div class="contact-card contact-card--address">
            <span class="contact-label" data-i18n="common.address">{addressLabel}</span>
            <span class="contact-value">{address}</span>
            <div class="contact-actions">
              <button type="button" class="btn btn-outline btn-sm" data-copy="{address}"
                      data-i18n="common.copy">{copy}</button>
              <a class="btn btn-outline btn-sm" href="{amap}" target="_blank" rel="noopener"
                 data-i18n="contact.mapAmap">{amapLabel}</a>
              <a class="btn btn-outline btn-sm" href="{baidu}" target="_blank" rel="noopener"
                 data-i18n="contact.mapBaidu">{baiduLabel}</a>
            </div>
          </div>
        </div>

        <div class="location-panel">
          <div class="location-art">{art}</div>
          <div class="location-info">
            <h2 data-i18n="contact.mapTitle">{mapTitle}</h2>
            <p class="location-address">{name}</p>
            <p class="location-address">{address}</p>
            <p class="muted">{region}</p>
            <p class="muted" data-i18n="contact.hoursHint">{hoursHint}</p>
          </div>
        </div>

        <div class="info-card info-card--wide">
          <h2 data-i18n="contact.askTitle">{askTitle}</h2>
          <ul class="check-list">
            <li data-i18n="contact.ask1">{ask1}</li>
            <li data-i18n="contact.ask2">{ask2}</li>
            <li data-i18n="contact.ask3">{ask3}</li>
            <li data-i18n="contact.ask4">{ask4}</li>
          </ul>
          <a class="btn btn-primary" href="inquiry.html" data-i18n="nav.inquiry">{inquiry}</a>
        </div>
      </div>
    </section>""".format(
        home=t("nav.home"),
        title=t("contact.title"),
        lead=t("contact.lead"),
        call=t("common.call"),
        copy=t("common.copy"),
        wechat=t("common.wechat"),
        qqLabel=t("common.qq"),
        emailLabel=t("common.email"),
        personLabel=t("common.person"),
        addressLabel=t("common.address"),
        person=COMPANY["personZh"],
        phone=COMPANY["phone"],
        qq=COMPANY["qq"],
        email=COMPANY["email"],
        address=COMPANY["addressZh"],
        region=COMPANY["regionZh"],
        name=COMPANY["nameZh"],
        amap=links["amap"],
        baidu=links["baidu"],
        amapLabel=t("contact.mapAmap"),
        baiduLabel=t("contact.mapBaidu"),
        mapTitle=t("contact.mapTitle"),
        hoursHint=t("contact.hoursHint"),
        art=location_art(),
        askTitle=t("contact.askTitle"),
        ask1=t("contact.ask1"),
        ask2=t("contact.ask2"),
        ask3=t("contact.ask3"),
        ask4=t("contact.ask4"),
        inquiry=t("nav.inquiry"),
    )


def location_art():
    return """<svg viewBox="0 0 420 260" fill="none" aria-hidden="true" class="map-art">
          <rect x="4" y="4" width="412" height="252" rx="16" fill="#eef4fb" stroke="#d7e3f2" stroke-width="2"/>
          <g stroke="#cfdcec" stroke-width="10" stroke-linecap="round">
            <path d="M40 20v220M380 20v220M20 60h380M20 200h380"/>
          </g>
          <g stroke="#dbe6f4" stroke-width="4" stroke-linecap="round">
            <path d="M110 20v220M300 20v220M20 130h380"/>
          </g>
          <rect x="128" y="78" width="150" height="104" rx="10" fill="#ffffff" stroke="#9dbde0" stroke-width="2"/>
          <text x="203" y="120" text-anchor="middle" font-size="16" fill="#20456f"
                font-family="system-ui, -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif">都会电子城</text>
          <text x="203" y="146" text-anchor="middle" font-size="14" fill="#4c6b8f"
                font-family="ui-monospace, SFMono-Regular, Menlo, monospace">2C030</text>
          <g transform="translate(203 176)">
            <path d="M0-22c-9 0-16 7-16 16 0 12 16 26 16 26s16-14 16-26c0-9-7-16-16-16z" fill="#e53935"/>
            <circle cx="0" cy="-6" r="6" fill="#ffffff"/>
          </g>
          <g fill="#7ba7d4" font-size="12"
             font-family="system-ui, -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif">
            <text x="36" y="48">中航路</text>
            <text x="312" y="48">华强北路</text>
          </g>
        </svg>"""


def inquiry_content():
    return """    <section class="page-head">
      <div class="container">
        <nav class="breadcrumb" aria-label="breadcrumb">
          <a href="index.html" data-i18n="nav.home">{home}</a><span>/</span>
          <span data-i18n="inquiry.title">{title}</span>
        </nav>
        <h1 data-i18n="inquiry.title">{title}</h1>
        <p class="lead" data-i18n="inquiry.lead">{lead}</p>
      </div>
    </section>
    <section class="section section--tight">
      <div class="container inquiry-layout">
        <div class="inquiry-main">
          <div class="table-wrap table-wrap--parts" data-inquiry-table></div>
          <div class="empty-state empty-state--card" data-inquiry-empty hidden>
            <p data-i18n="inquiry.empty">{empty}</p>
            <a class="btn btn-primary" href="products.html" data-i18n="inquiry.emptyCta">{emptyCta}</a>
          </div>
          <p class="muted" data-i18n="inquiry.savedHint">{savedHint}</p>
        </div>
        <aside class="inquiry-side">
          <h2 data-i18n="inquiry.formTitle">{formTitle}</h2>
          <div class="form-grid">
            <label>
              <span data-i18n="inquiry.company">{companyLabel}</span>
              <input type="text" data-inquiry-field="company" autocomplete="organization">
            </label>
            <label>
              <span data-i18n="inquiry.person">{personLabel}</span>
              <input type="text" data-inquiry-field="person" autocomplete="name">
            </label>
            <label>
              <span data-i18n="inquiry.tel">{telLabel}</span>
              <input type="text" data-inquiry-field="tel" autocomplete="tel">
            </label>
            <label>
              <span data-i18n="inquiry.remarkAll">{remarkLabel}</span>
              <textarea rows="3" data-inquiry-field="remark"></textarea>
            </label>
          </div>
          <div class="inquiry-actions">
            <button type="button" class="btn btn-primary" data-inquiry-mail
                    data-i18n="inquiry.mail">{mail}</button>
            <button type="button" class="btn btn-outline" data-inquiry-copy
                    data-i18n="inquiry.copy">{copy}</button>
            <button type="button" class="btn btn-text" data-inquiry-clear
                    data-i18n="inquiry.clear">{clear}</button>
          </div>
          <p class="muted" data-i18n="inquiry.note">{note}</p>
          <div class="quick-contact">
            <a class="btn btn-outline btn-sm" href="tel:{phone}">{phone}</a>
            <button type="button" class="btn btn-outline btn-sm" data-copy="{qq}">QQ {qq}</button>
            <a class="btn btn-outline btn-sm" href="mailto:{email}">{email}</a>
          </div>
        </aside>
      </div>
    </section>""".format(
        home=t("nav.home"),
        title=t("inquiry.title"),
        lead=t("inquiry.lead"),
        empty=t("inquiry.empty"),
        emptyCta=t("inquiry.emptyCta"),
        savedHint=t("inquiry.savedHint"),
        formTitle=t("inquiry.formTitle"),
        companyLabel=t("inquiry.company"),
        personLabel=t("inquiry.person"),
        telLabel=t("inquiry.tel"),
        remarkLabel=t("inquiry.remarkAll"),
        mail=t("inquiry.mail"),
        copy=t("inquiry.copy"),
        clear=t("inquiry.clear"),
        note=t("inquiry.note").format(email=COMPANY["email"]),
        phone=COMPANY["phone"],
        qq=COMPANY["qq"],
        email=COMPANY["email"],
    )


def notfound_content():
    quick = "\n        ".join(
        '<a class="chip" href="category.html?cat=%s" data-cat-name="%s">%s</a>' % (c["id"], c["id"], c["zh"])
        for c in CATEGORIES[:6]
    )
    return """    <section class="notfound">
      <div class="container notfound-inner">
        <span class="notfound-code">404</span>
        <h1 data-i18n="notfound.title">{title}</h1>
        <p class="lead" data-i18n="notfound.lead">{lead}</p>
        <div class="notfound-search">{searchForm}</div>
        <div class="chips">
        {quick}
        </div>
        <div class="notfound-actions">
          <a class="btn btn-primary" href="index.html" data-i18n="notfound.cta">{cta}</a>
          <a class="btn btn-outline" href="contact.html" data-i18n="nav.contact">{contact}</a>
        </div>
      </div>
    </section>""".format(
        title=t("notfound.title"),
        lead=t("notfound.lead"),
        searchForm=hero_search_form(),
        quick=quick,
        cta=t("notfound.cta"),
        contact=t("nav.contact"),
    )


def build_data():
    return {
        "meta": {
            "updated": COMPANY["updated"],
            "categories": len(CATEGORIES),
            "subs": TOTAL_SUBS,
            "parts": TOTAL_PARTS,
            "noteZh": "站内型号与参数为行业通用资料，不含价格与库存；实际库存、报价与交期请以电话 / 微信确认为准。",
            "noteEn": "Part numbers and parameters are industry-generic reference data without prices or stock; confirm stock, quotation and lead time by phone or WeChat.",
        },
        "company": COMPANY,
        "nav": [{"href": href, "key": key} for href, key in NAV],
        "brands": [{"id": k, "zh": v[0], "en": v[1]} for k, v in catalog.BRANDS.items()],
        "types": [{"id": k, "zh": v[0], "en": v[1]} for k, v in catalog.TYPES.items()],
        "icons": icons.ICONS,
        "categories": CATEGORIES,
        "hot": catalog.HOT_MODELS,
        "services": [
            {"icon": s["icon"], "zhT": s["zh"][0], "zhD": s["zh"][1], "enT": s["en"][0], "enD": s["en"][1]}
            for s in catalog.SERVICES
        ],
        "profileZh": catalog.PROFILE_ZH,
        "profileEn": catalog.PROFILE_EN,
        "promisesZh": catalog.SERVICE_PROMISES_ZH,
        "promisesEn": catalog.SERVICE_PROMISES_EN,
    }


def write_js_file(path, varname, payload):
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("/* Generated by %s - do not edit by hand. */\n" % SCRIPT_LABEL)
        fh.write("window.%s = %s;\n" % (varname, body))


def write_sitemap():
    urls = ["index.html", "products.html", "brands.html", "about.html", "contact.html", "inquiry.html"]
    urls += ["category.html?cat=" + c["id"] for c in CATEGORIES]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append("  <url><loc>%s%s</loc><changefreq>weekly</changefreq></url>" % (BASE_URL, u))
    lines.append("</urlset>")
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_robots():
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write("User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n" % BASE_URL)


def write_readme():
    text = """# {name} 官网 / {short} Website

> 纯静态、中英双语、零依赖的电子元器件供应商官网。
> Static, bilingual, dependency-free corporate website for a Shenzhen component supplier.

## 线上地址 / Live site

- 仓库 Repository：<https://github.com/ynz24522-creator/xinweikai-website>
- 线上地址 Live：<{base}>

## 特性 / Highlights

| 中文 | English |
| --- | --- |
| 8 个静态页面，双击 `index.html` 即可浏览，无需构建、无外部 CDN | 8 static pages, open `index.html` directly - no build step, no CDN |
| 中英双语切换（默认中文，`?lang=en` 分享英文链接） | Chinese / English switch (Chinese by default, share with `?lang=en`) |
| 收录 {cats} 个大类、{subs} 个小类、{parts} 个型号 | {cats} categories, {subs} sub-categories, {parts} part numbers |
| 全站即时搜索：型号 / 封装 / 品牌 / 分类关键词，下拉分组 + 高亮 | Instant site-wide search across model, package, brand and category with grouping and highlighting |
| 产品中心支持分类树 + 品牌 / 封装筛选，筛选状态写入 URL | Category tree plus brand / package filters, filters encoded in the URL |
| 询价清单：逐行加入型号、填数量备注、一键生成邮件或复制文本发微信 | Inquiry list: add parts, set quantity and notes, generate an email or copy text for WeChat |
| 响应式布局（手机导航抽屉、表格转卡片流）、可打印、无障碍友好 | Responsive layout, mobile drawer, card-style tables on phones, print friendly, a11y touches |
| 视觉为内联 SVG 线稿与 CSS 渐变，全站资源约 350KB、无图片文件 | Artwork is inline SVG line work and CSS gradients; about 350KB total with no image files |

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

- 公司：{name}
- 负责人：{person}
- 电话 / 微信：{phone}
- QQ：{qq}
- 邮箱：{email}
- 地址：{address}

站内型号与参数为行业通用资料，实际库存与报价请以电话 / 微信确认为准。
""".format(
        name=COMPANY["nameZh"],
        short=COMPANY["shortZh"],
        base=BASE_URL,
        cats=len(CATEGORIES),
        subs=TOTAL_SUBS,
        parts=TOTAL_PARTS,
        person=COMPANY["personZh"],
        phone=COMPANY["phone"],
        qq=COMPANY["qq"],
        email=COMPANY["email"],
        address=COMPANY["addressZh"],
    )
    with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(text)


def write_docs():
    usage = """# __SHORT__官网 · 使用与维护说明

> 本文件描述站点仓库本身的结构与维护方式，适合交给后续维护者。

- 仓库：<https://github.com/ynz24522-creator/xinweikai-website>
- 线上地址：<__BASE__>
- 站点形态：纯静态（HTML + CSS + 原生 JavaScript），无构建步骤、无依赖、无外部 CDN。

## 一、日常维护改哪里

| 想改什么 | 改哪里 |
| --- | --- |
| 公司名称、负责人、电话 / 微信、QQ、邮箱、地址 | `assets/js/data.js` 的 `company` 对象（同时 `assets/js/i18n.js` 里的中英文文案可一并核对） |
| 页面静态文案（中 / 英） | `assets/js/i18n.js` 的 `zh` / `en` 字典，页面用 `data-i18n="键名"` 引用 |
| 产品分类、小类、型号与参数 | `assets/js/data.js` 的 `categories[].subs[].parts[]`（字段：`m` 型号、`b` 品牌键、`k` 封装、`p` 关键参数、`t` 类型键） |
| 品牌清单 | `assets/js/data.js` 的 `brands[]` |
| 首页常备型号 | `assets/js/data.js` 的 `hot[]`（填型号字符串即可） |
| 颜色、圆角、间距等视觉变量 | `assets/css/style.css` 顶部的 `:root` |
| 图标 | `assets/js/data.js` 的 `icons`（48×48 SVG 路径，`stroke=currentColor`） |
| 备案号 | `assets/js/i18n.js` 的 `footer.icp`（中英两处） |

## 二、产品数据格式

```js
{ m: "STM32F103C8T6", b: "st", k: "LQFP-48", p: "Cortex-M3 72MHz 64KB Flash", t: "mcu32" }
```

- `b` 必须存在于 `brands[]` 的 `id` 中，否则品牌显示为原始键名。
- `t` 必须存在于 `types[]` 的 `id` 中，用于生成「说明」列的品类名称（中英自动切换）。
- 新增分类时，同时在 `categories[]` 中补 `id / zh / en / blurbZh / blurbEn / tipsZh / tipsEn / count / subs`。
- 每个分类的 `count` 用于首页卡片显示，等于该分类下所有 `parts` 数量之和。

## 三、搜索与筛选

- 站头搜索框：输入即出结果，匹配型号、分类、小类、品牌、封装与参数；下拉按分类 / 型号分组，命中片段高亮。
- 键盘：`/` 聚焦搜索框，`↑` `↓` 选择，`Enter` 打开，`Esc` 关闭。
- 产品中心：左侧分类树 + 品牌 / 封装筛选，筛选条件写入 URL（`products.html?q=&cat=&sub=&brand=&pkg=`），可直接分享。
- 分类页：`category.html?cat=<分类 id>`，页内搜索框只在该分类内过滤。

## 四、询价清单

- 任意表格行的「加入询价」会把型号、品牌、封装、参数写入浏览器 `localStorage`（键 `xwk_inquiry_v1`）。
- 询价页可填数量与备注，点「生成询价邮件」调用本机邮件客户端，收件人 __EMAIL__；「复制询价内容」可粘贴到微信 / QQ。
- 语言偏好存在 `xwk_lang_v1`。

## 五、发布与更新

1. 修改文件 → `git add -A` → `git commit -m "说明"` → `git push`。
2. GitHub Pages 会在 1 分钟内自动更新（仓库 Settings → Pages → Source 选 `main` / `(root)`）。
3. 也可把除 `.git/` 以外的全部文件上传到任意虚拟主机的网站根目录，无需服务端配置。

## 六、上线前建议补充

- 备案号（`footer.icp`）与公司营业执照全称核对。
- 微信二维码图片、门店与仓库实拍图（可放在 `assets/img/` 并在页面中替换占位插图）。
- 品牌授权清单（如具备），用于替换 `brands.note` 中的说明口径。

## 七、上线前自检清单

1. 用浏览器打开 `index.html`：首页标题、电话、地址是否正确；点「浏览产品中心」能跳转。
2. 在搜索框输入 `0603`、`STM32`、`电阻`、`国巨`、`MOS`、`SMA`：下拉是否出现结果并可点击进入。
3. 产品中心：切换左侧分类、品牌下拉与封装下拉，列表数量与 URL 参数是否同步。
4. 分类页：`category.html?cat=resistors` 的选型要点、小类锚点与表格是否正常。
5. 任意表格行点「加入询价」→ 打开右上角「询价清单」：型号、数量、备注是否保留（刷新后仍在）。
6. 询价页填电话后点「生成询价邮件」：是否能唤起邮件客户端且收件人为 __EMAIL__。
7. 右上角切到 EN：全站文案是否变英文、产品「说明」列是否变成英文品类名。
8. 手机（或浏览器窗口缩到 375px 宽）：导航是否收进菜单按钮、表格是否变成卡片流、右下角是否出现拨号按钮。
"""
    usage = (usage.replace("__SHORT__", COMPANY["shortZh"])
                  .replace("__BASE__", BASE_URL)
                  .replace("__EMAIL__", COMPANY["email"]))

    data_doc = """# 数据说明与免责声明

## 一、数据构成

- 分类体系：参考立创商城式的元器件分类方法整理，共 {cats} 个大类、{subs} 个小类。
- 型号条目：{parts} 条，字段为「型号 / 品牌 / 封装 / 关键参数 / 类型」。
- 品牌表：{brands} 个常见元器件品牌（中文名 + 英文名）。

## 二、数据口径

1. 型号与参数为**行业通用资料**，用于帮助客户快速定位品类与常见料号，便于询价时说明需求。
2. 站内**不列价格、不列库存数量、不承诺交期**，统一提示「以电话 / 微信确认为准」。
3. 品牌栏表示我司常备与常用的货源方向，**不代表全部为原厂授权代理**；需要授权书、原厂包装或指定批次时，请在询价时说明，我们如实告知可行方案。
4. 公司简介只描述经营定位、主营范围与服务方式，**不包含成立年份、员工人数、厂房产能、认证资质、获奖情况**等未经确认的硬指标。

## 三、维护建议

- 若要以真实经营数据替换通用资料，建议按「分类 → 小类 → 型号」逐条替换 `assets/js/data.js` 中的 `parts`，保持字段结构不变。
- 替换后建议按 `docs/使用说明.md` 的「上线前自检清单」逐项核对：页面能否打开、搜索是否命中、询价清单是否正常。
- 若替换成自家报价或库存表，请同步修改 `footer.note` 与 `common.disclaimer` 两句提示，避免口径不一致。

## 四、隐私

- 站点为纯静态页面，没有后端与数据库，不收集、不上传访客数据。
- 语言偏好与询价清单仅保存在访客本机浏览器（`localStorage`），清除浏览器数据即会丢失。
- 询价邮件由访客本机邮件客户端发送，站点不代发、不留存。
""".format(cats=len(CATEGORIES), subs=TOTAL_SUBS, parts=TOTAL_PARTS, brands=len(catalog.BRANDS))

    with open(os.path.join(OUT, "docs", "使用说明.md"), "w", encoding="utf-8") as fh:
        fh.write(usage)
    with open(os.path.join(OUT, "docs", "数据说明.md"), "w", encoding="utf-8") as fh:
        fh.write(data_doc)


def write_site_files():
    pages = [
        ("index.html", "index", "meta.home", "meta.home", home_content()),
        ("products.html", "products", "products.title", "meta.products", products_content()),
        ("category.html", "category", "products.title", "meta.category", category_content()),
        ("brands.html", "brands", "brands.title", "meta.brands", brands_content()),
        ("about.html", "about", "about.title", "meta.about", about_content()),
        ("contact.html", "contact", "contact.title", "meta.contact", contact_content()),
        ("inquiry.html", "inquiry", "inquiry.title", "meta.inquiry", inquiry_content()),
        ("404.html", "404", "notfound.title", "meta.404", notfound_content()),
    ]
    for filename, page_id, title_key, desc_key, content in pages:
        with open(os.path.join(OUT, filename), "w", encoding="utf-8") as fh:
            fh.write(page(filename, page_id, title_key, desc_key, content))
    write_js_file(os.path.join(OUT, "assets", "js", "data.js"), "XWK_DATA", build_data())
    write_js_file(os.path.join(OUT, "assets", "js", "i18n.js"), "XWK_I18N", I18N)
    with open(os.path.join(OUT, "assets", "img", "favicon.svg"), "w", encoding="utf-8") as fh:
        fh.write(icons.FAVICON)
    with open(os.path.join(OUT, ".nojekyll"), "w", encoding="utf-8") as fh:
        fh.write("")
    write_sitemap()
    write_robots()
    write_readme()
    write_docs()


def main():
    for sub in ("assets/css", "assets/js", "assets/img", "docs"):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    write_site_files()
    print("site written to %s" % OUT)
    print("categories=%d subs=%d parts=%d brands=%d types=%d"
          % (len(CATEGORIES), TOTAL_SUBS, TOTAL_PARTS, len(catalog.BRANDS), len(catalog.TYPES)))


if __name__ == "__main__":
    main()
