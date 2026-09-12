/* ==========================================================================
   part-art.js — 每个型号的确定性矢量示意图 / deterministic part illustrations

   公开接口 / Public API:
     window.XWK_PART_ART.svgFor(part, opts)   -> <svg> 字符串 / svg markup string
     window.XWK_PART_ART.html(part, opts)     -> <svg> 或实拍图 <img>（有 img 字段时）
     window.XWK_PART_ART.shapeFor(part)       -> 形状 id 字符串
     window.XWK_PART_ART.paletteFor(catId)    -> 分类主色
     window.XWK_PART_ART.typeShapes           -> 类型 -> 形状映射表

   规则：同一型号 + 同一尺寸永远得到完全相同的图；纯函数，无随机，无外部请求。
   opts.size: "sm"（缩略图，不排文字）/ "md"（默认，型号）/ "lg"（大图，型号 + 封装）
   ========================================================================== */
(function () {
  "use strict";

  var INK = "#1b3350";
  var CARD_BG = "#f7fafd";
  var CARD_LINE = "#dde7f3";

  /* 分类主色：让同一大类的型号在列表里颜色相近，便于扫读 */
  var PALETTE = {
    resistors: "#1f6fd0",
    capacitors: "#d98300",
    inductors: "#0f8a6a",
    diodes: "#c2410c",
    transistors: "#7c3aed",
    power: "#0e7490",
    mcu: "#166534",
    memory: "#4338ca",
    amplifiers: "#b91c1c",
    interface: "#0e7490",
    logic: "#7c3aed",
    crystals: "#0369a1",
    sensors: "#0d9488",
    connectors: "#475569",
    switches: "#a16207",
    opto: "#dc2626",
    rf: "#6d28d9",
    protection: "#b45309",
    "battery-power": "#15803d",
    tools: "#334155",
    "pcb-wire": "#0f766e",
    thermal: "#7c2d12"
  };

  /* 123 个类型键全部显式映射，保证任何一个型号都有对应形状 */
  var TYPE_SHAPE = {
    "res-thick": "chip", "res-prec": "chip", "res-array": "chipArray", "res-lead": "resistorAxial",
    "res-power": "chipPower", "res-ntc": "discPart", "res-ptc": "discPart", "pot": "trimmer",
    "cap-mlcc": "mlcc", "cap-tantalum": "tantalum", "cap-electrolytic": "ecap", "cap-film": "filmCap",
    "cap-super": "superCap", "cap-safety": "filmCap",
    "ind-chip": "inductorShielded", "ind-hf": "inductorCoil", "bead": "bead",
    "cmc": "commonMode", "xfmr": "transformer",
    "diode-rect": "diodeAxial", "diode-switch": "diodeAxial", "diode-schottky": "diodeSchottky",
    "diode-zener": "diodeZener", "diode-tvs": "diodeTvs", "diode-array": "sotArray", "bridge": "bridge",
    "bjt": "canTo92", "mosfet": "sotMosfet", "igbt": "powerTab", "thyristor": "powerTab",
    "ldo": "icDual", "dcdc": "icDual", "acdc": "icDual", "charger": "icDual",
    "reference": "sotIc", "pmic": "icDual", "led-driver": "icDual", "gate-driver": "icDual",
    "motor-driver": "icDual",
    "mcu32": "icQuad", "mcu8": "icDual", "dsp": "icQuad",
    "eeprom": "icDual", "flash": "icDual", "sram": "icDual", "dram": "icBga",
    "opamp": "icDual", "comparator": "icDual", "audiamp": "icDual", "inamp": "icDual",
    "uart": "icDual", "usb": "icDual", "can": "icDual", "eth": "icQuad",
    "display-driver": "icDual", "level-shift": "icDual",
    "logic-gate": "icDual", "logic-shift": "icDual", "logic-decoder": "icDual", "logic-counter": "icDual",
    "xtal": "crystalSmd", "osc": "oscillator", "rtc": "icDual", "resonator": "resonator",
    "sensor-temp": "sensorChip", "sensor-humidity": "sensorChip", "sensor-pressure": "sensorChip",
    "sensor-motion": "sensorChip", "sensor-magnetic": "canTo92", "sensor-current": "icDual",
    "sensor-light": "sensorChip", "sensor-distance": "sensorChip",
    "conn-header": "headerPins", "conn-wire": "wireHeader", "conn-usb": "usbReceptacle",
    "conn-av": "audioJack", "conn-card": "cardSocket", "conn-terminal": "terminalBlock",
    "conn-ffc": "ffcConnector", "conn-rf": "rfConnector",
    "sw-tact": "tactSwitch", "sw-slide": "slideSwitch", "sw-encoder": "encoder",
    "relay": "relayBox", "relay-ssr": "ssrBox", "opto-coupler": "optoDual",
    "led-smd": "ledSmd", "led-tht": "ledDome", "led-power": "ledPower", "led-addressable": "ledRgb",
    "seg-display": "sevenSeg", "ir-emitter": "ledDome", "ir-receiver": "irReceiver",
    "wireless-module": "moduleAntenna", "wifi-module": "moduleAntenna", "ble-module": "moduleCan",
    "lora-module": "moduleAntenna", "cellular-module": "moduleCan", "gnss-module": "moduleAntenna",
    "antenna": "antennaArt",
    "fuse": "fuseTube", "ptc-resettable": "discPart", "esd": "esdChip", "tvs-array": "sotArray",
    "gdt": "gdtTube",
    "battery": "batteryCell", "battery-holder": "batteryHolder", "power-module": "powerModule",
    "adapter": "adapterBox",
    "tool-solder": "solderingIron", "tool-meter": "meter", "tool-hand": "handTool", "tool-esd": "esdStrap",
    "cons-wire": "wireSpool", "cons-breadboard": "breadboard", "cons-heat": "tapeRoll",
    "cons-clean": "cleanerBottle", "pcb-blank": "pcbBoard",
    "thermal-heatsink": "heatsink", "thermal-fan": "fan", "thermal-paste": "thermalPad",
    "hardware-standoff": "standoff", "hardware-screw": "screw"
  };

  var CAT_FALLBACK = {
    resistors: "chip", capacitors: "mlcc", inductors: "inductorShielded", diodes: "diodeAxial",
    transistors: "sotMosfet", power: "icDual", mcu: "icQuad", memory: "icDual",
    amplifiers: "icDual", interface: "icDual", logic: "icDual", crystals: "crystalSmd",
    sensors: "sensorChip", connectors: "headerPins", switches: "tactSwitch", opto: "ledSmd",
    rf: "moduleAntenna", protection: "fuseTube", "battery-power": "batteryCell",
    tools: "handTool", "pcb-wire": "pcbBoard", thermal: "heatsink"
  };

  /* ---------------------------------------------------------------- 基础图元 */
  function esc(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function rect(x, y, w, h, rx, fill, stroke, sw, op) {
    return '<rect x="' + r2(x) + '" y="' + r2(y) + '" width="' + r2(w) + '" height="' + r2(h) +
      '" rx="' + r2(rx) + '" fill="' + fill + '"' +
      (op == null ? "" : ' fill-opacity="' + op + '"') +
      ' stroke="' + (stroke || "none") + '" stroke-width="' + (sw || 1.6) + '"/>';
  }

  function circ(cx, cy, r, fill, stroke, sw, op) {
    return '<circle cx="' + r2(cx) + '" cy="' + r2(cy) + '" r="' + r2(r) + '" fill="' + fill + '"' +
      (op == null ? "" : ' fill-opacity="' + op + '"') +
      ' stroke="' + (stroke || "none") + '" stroke-width="' + (sw || 1.6) + '"/>';
  }

  function line(x1, y1, x2, y2, stroke, sw, dash) {
    return '<path d="M' + r2(x1) + ' ' + r2(y1) + 'L' + r2(x2) + ' ' + r2(y2) + '" fill="none" stroke="' +
      stroke + '" stroke-width="' + (sw || 2) + '" stroke-linecap="round"' +
      (dash ? ' stroke-dasharray="' + dash + '"' : "") + "/>";
  }

  function path(d, fill, stroke, sw, op) {
    return '<path d="' + d + '" fill="' + (fill || "none") + '"' +
      (op == null ? "" : ' fill-opacity="' + op + '"') +
      ' stroke="' + (stroke || "none") + '" stroke-width="' + (sw || 1.6) +
      '" stroke-linecap="round" stroke-linejoin="round"/>';
  }

  function r2(n) {
    return Math.round(Number(n) * 100) / 100;
  }

  /* ------------------------------------------------------------ 封装解析 */
  var CHIP_SIZE = {
    "0402": [30, 16], "0603": [34, 18], "0805": [40, 20], "1206": [46, 22], "1210": [46, 24],
    "1812": [52, 26], "2012": [36, 20], "2520": [38, 24], "3215": [36, 18], "3216": [38, 24],
    "3225": [40, 26], "3528": [44, 24], "4030": [46, 30], "5040": [52, 34], "5050": [52, 34],
    "6032": [54, 34], "6045": [54, 38], "6530": [58, 38], "7050": [60, 38], "7343": [58, 40],
    "1060": [62, 42], "2512": [58, 30], "3535": [48, 42], "5730": [50, 30], "2835": [42, 26],
    "2020": [38, 38], "1204": [36, 28]
  };

  function parsePkg(pkg) {
    var k = String(pkg || "").trim();
    var out = { pins: null, sides: null, kind: "other", bw: 54, bh: 34, big: false };
    var m;

    if ((m = k.match(/BGA-?(\d+)?/i))) {
      out.kind = "bga"; out.sides = 4; out.pins = m[1] ? parseInt(m[1], 10) : null;
      out.bw = 62; out.bh = 62; return out;
    }
    if ((m = k.match(/(?:LQFP|TQFP|EQFP|QFN|DFN|VQFN)-?(\d+)?/i))) {
      out.kind = "quad"; out.sides = 4; out.pins = m[1] ? parseInt(m[1], 10) : 32;
      out.bw = 62; out.bh = 62; return out;
    }
    if ((m = k.match(/(?:SOIC|SOP|TSSOP|MSOP|SSOP|SO)-?(\d+)?/i))) {
      out.kind = "dual"; out.sides = 2; out.pins = m[1] ? parseInt(m[1], 10) : 8;
      out.bw = 58; out.bh = 40; return out;
    }
    if ((m = k.match(/DIP-?(\d+)/i))) {
      out.kind = "dual"; out.sides = 2; out.pins = parseInt(m[1], 10);
      out.bw = 66; out.bh = 34; out.big = true; return out;
    }
    if ((m = k.match(/SOT-?(23|25|26|89|563)-\d|SOT-2[35]|SOT-?89|SC-70|SOD-?(123|323|523|923|123FL)\b/i))) {
      out.kind = "sot"; out.sides = 2; out.pins = 3;
      out.bw = 40; out.bh = 26; return out;
    }
    if (/SOT-23-5|SOT-25|SOT-23-6|SOT-563|SOT-89|SOT-23-8/i.test(k)) {
      out.kind = "sot"; out.sides = 2; out.pins = 5; out.bw = 42; out.bh = 28; return out;
    }
    if (/TO-?220|TO-?263|TO-?252|TO-?247|TO-?3P|TOP-?3|TO-?126|CB-?5|DO-201|TO-?247/i.test(k)) {
      out.kind = "tab"; out.pins = 3; out.bw = 62; out.bh = 52; out.big = true; return out;
    }
    if (/TO-?92|TO-?92/i.test(k)) {
      out.kind = "can92"; out.pins = 3; out.bw = 46; out.bh = 46; return out;
    }
    if ((m = k.match(/^(0402|0603|0805|1206|1210|1812|2012|2520|3215|3216|3225|3528|4030|5040|5050|6032|6045|6530|7050|7343|1060|2512|3535|5730|2835|2020|1204)$/))) {
      out.kind = "chip"; out.bw = CHIP_SIZE[m[1]][0]; out.bh = CHIP_SIZE[m[1]][1];
      out.sides = 2; out.pins = 2; return out;
    }
    if ((m = k.match(/^([ABCD])\s*型\s*(\d+)/))) {
      out.kind = "tantalum"; out.sides = 2; out.pins = 2;
      out.bw = m[1] === "A" ? 40 : m[1] === "B" ? 48 : m[1] === "C" ? 56 : 62;
      out.bh = m[1] === "A" ? 24 : m[1] === "B" ? 28 : m[1] === "C" ? 34 : 40;
      return out;
    }
    if ((m = k.match(/D(\d+(?:\.\d+)?)\s*(?:×|x)/i)) || (m = k.match(/^插件\s*D(\d+(?:\.\d+)?)/))) {
      var d = parseFloat(m[1]);
      out.kind = "radial"; out.pins = 2; out.bw = Math.min(64, Math.max(28, d * 4.2));
      out.bh = out.bw; return out;
    }
    if ((m = k.match(/(\d+)\s*(?:×|x)\s*(\d+)\s*mm/i))) {
      out.kind = "board"; out.bw = Math.min(78, Math.max(40, parseInt(m[1], 10) * 0.62));
      out.bh = Math.min(58, Math.max(30, parseInt(m[2], 10) * 0.42)); return out;
    }
    if (/灯带/.test(k)) { out.kind = "strip"; return out; }
    if (/焊线式/.test(k)) { out.kind = "pigtail"; return out; }
    if (/模块|成品|盒装|一双|一对|卷|条$|根|只|袋|针管|罐装|瓶/.test(k)) { out.kind = "commodity"; return out; }
    if (/(\d+)\s*脚|(\d+)P|P=/.test(k)) {
      var mm = k.match(/(\d+)\s*脚/);
      out.kind = "leadFrame"; out.pins = mm ? parseInt(mm[1], 10) : 4; out.sides = 2; return out;
    }
    if (/插件|直插|立式|卧式|90°|SMT|贴片|COG|焊线/.test(k)) { out.kind = "chip"; return out; }
    return out;
  }

  /* ---------------------------------------------------------------- 形状库 */
  function body(c, ratio) {
    var w = c.bw, h = c.bh * (ratio == null ? 1 : ratio);
    return { x: 80 - w / 2, y: 52 - h / 2, w: w, h: h };
  }

  function leadsX(c, b, n, len) {
    var out = "", i, y;
    var gap = b.h / (n + 1);
    for (i = 1; i <= n; i += 1) {
      y = b.y + gap * i;
      out += line(b.x - len, y, b.x, y, c.a, 2.2);
      out += line(b.x + b.w, y, b.x + b.w + len, y, c.a, 2.2);
    }
    return out;
  }

  function leadsY(c, b, n, len) {
    var out = "", i, x;
    var gap = b.w / (n + 1);
    for (i = 1; i <= n; i += 1) {
      x = b.x + gap * i;
      out += line(x, b.y - len, x, b.y, c.a, 2.2);
      out += line(x, b.y + b.h, x, b.y + b.h + len, c.a, 2.2);
    }
    return out;
  }

  var SHAPES = {
    /* 两脚片式元件：电阻、电容、磁珠、LED 等 */
    chip: function (c) {
      var b = body(c);
      return rect(b.x, b.y, b.w, b.h, 3, c.a, c.a, 1.6, 0.14) +
        rect(b.x, b.y, b.w * 0.2, b.h, 2, c.a, "none", 0, 0.85) +
        rect(b.x + b.w * 0.8, b.y, b.w * 0.2, b.h, 2, c.a, "none", 0, 0.85) +
        line(b.x - 10, b.y + b.h / 2, b.x, b.y + b.h / 2, c.a, 2.4) +
        line(b.x + b.w, b.y + b.h / 2, b.x + b.w + 10, b.y + b.h / 2, c.a, 2.4);
    },
    chipPower: function (c) {
      var b = body(c, 1.1);
      return rect(b.x, b.y, b.w, b.h, 4, c.a, c.a, 1.8, 0.16) +
        rect(b.x + b.w * 0.08, b.y + b.h * 0.16, b.w * 0.12, b.h * 0.68, 2, c.a, "none", 0, 0.9) +
        rect(b.x + b.w * 0.8, b.y + b.h * 0.16, b.w * 0.12, b.h * 0.68, 2, c.a, "none", 0, 0.9) +
        line(b.x - 12, b.y + b.h / 2, b.x, b.y + b.h / 2, c.a, 2.6) +
        line(b.x + b.w, b.y + b.h / 2, b.x + b.w + 12, b.y + b.h / 2, c.a, 2.6);
    },
    chipArray: function (c) {
      var b = body(c, 1.05);
      var out = rect(b.x, b.y, b.w, b.h, 3, c.a, c.a, 1.6, 0.12);
      var i, x, seg = b.w / 4;
      for (i = 0; i < 4; i += 1) {
        x = b.x + seg * i + seg * 0.16;
        out += rect(x, b.y, seg * 0.68, b.h, 2, c.a, "none", 0, 0.55);
      }
      out += line(b.x - 10, b.y + b.h / 2, b.x, b.y + b.h / 2, c.a, 2.4);
      out += line(b.x + b.w, b.y + b.h / 2, b.x + b.w + 10, b.y + b.h / 2, c.a, 2.4);
      return out;
    },
    resistorAxial: function (c) {
      return rect(50, 40, 60, 24, 8, c.a, c.a, 1.8, 0.12) +
        line(18, 52, 50, 52, c.a, 2.6) + line(110, 52, 142, 52, c.a, 2.6) +
        path("M62 40v24M74 40v24M86 40v24M98 40v24", "none", c.a, 1.4);
    },
    mlcc: function (c) {
      var b = body(c);
      return rect(b.x, b.y, b.w, b.h, 2.5, c.a, c.a, 1.6, 0.12) +
        rect(b.x, b.y, b.w * 0.24, b.h, 2, c.a, "none", 0, 0.85) +
        rect(b.x + b.w * 0.76, b.y, b.w * 0.24, b.h, 2, c.a, "none", 0, 0.85) +
        path("M" + r2(b.x + b.w * 0.36) + " " + r2(b.y + 5) + "v" + r2(b.h - 10) +
          "M" + r2(b.x + b.w * 0.5) + " " + r2(b.y + 5) + "v" + r2(b.h - 10) +
          "M" + r2(b.x + b.w * 0.64) + " " + r2(b.y + 5) + "v" + r2(b.h - 10), "none", c.a, 1.2, "3 3");
    },
    tantalum: function (c) {
      var b = body(c, 1.05);
      return rect(b.x, b.y, b.w, b.h, 3, c.a, c.a, 1.7, 0.12) +
        rect(b.x, b.y, b.w * 0.16, b.h, 2, c.a, "none", 0, 0.9) +
        rect(b.x + b.w * 0.72, b.y + 3, b.w * 0.16, b.h - 6, 2, c.a, "none", 0, 0.55) +
        line(b.x + b.w * 0.8, b.y + b.h * 0.36, b.x + b.w * 0.8, b.y + b.h * 0.64, "#ffffff", 2.4) +
        line(b.x + b.w * 0.72, b.y + b.h * 0.5, b.x + b.w * 0.88, b.y + b.h * 0.5, "#ffffff", 2.4) +
        line(b.x - 10, b.y + b.h / 2, b.x, b.y + b.h / 2, c.a, 2.4) +
        line(b.x + b.w, b.y + b.h / 2, b.x + b.w + 10, b.y + b.h / 2, c.a, 2.4);
    },
    ecap: function (c) {
      var r = Math.min(38, c.bw / 2);
      return circ(80, 52, r, c.a, c.a, 1.9, 0.12) +
        path("M" + r2(80 - r * 0.62) + " " + r2(52 - r * 0.62) + "L" + r2(80 + r * 0.62) + " " +
          r2(52 + r * 0.62), "none", c.a, 2.2) +
        line(80 - r * 0.86, 52 + r * 0.86, 80 - r * 0.86, 52 + r + 16, c.a, 2.4) +
        line(80 + r * 0.86, 52 + r * 0.86, 80 + r * 0.86, 52 + r + 16, c.a, 2.4);
    },
    filmCap: function (c) {
      return rect(42, 30, 76, 46, 5, c.a, c.a, 1.8, 0.1) +
        line(20, 42, 42, 42, c.a, 2.4) + line(20, 64, 42, 64, c.a, 2.4) +
        line(58, 40, 102, 40, c.a, 1.4) + line(58, 52, 102, 52, c.a, 1.4) +
        line(58, 64, 102, 64, c.a, 1.4);
    },
    superCap: function (c) {
      return circ(80, 52, 38, c.a, c.a, 2, 0.1) + circ(80, 52, 26, "none", c.a, 1.4, 0) +
        path("M80 30v44M58 52h44", "none", c.a, 1.2, "3 3") +
        line(62, 88, 62, 104, c.a, 2.4) + line(98, 88, 98, 104, c.a, 2.4);
    },
    trimmer: function (c) {
      return rect(44, 32, 72, 40, 5, c.a, c.a, 1.8, 0.12) +
        circ(80, 52, 13, "#ffffff", c.a, 1.6) + line(70, 52, 90, 52, c.a, 2.2) +
        line(52, 72, 52, 94, c.a, 2.4) + line(80, 72, 80, 94, c.a, 2.4) +
        line(108, 72, 108, 94, c.a, 2.4);
    },
    discPart: function (c) {
      return circ(80, 50, 34, c.a, c.a, 2, 0.12) +
        path("M62 34l18 16-18 16", "none", c.a, 1.8) +
        line(68, 84, 60, 104, c.a, 2.4) + line(92, 84, 100, 104, c.a, 2.4);
    },
    inductorShielded: function (c) {
      var b = body(c, 1.05);
      return rect(b.x, b.y, b.w, b.h, 6, c.a, c.a, 1.8, 0.14) +
        path("M" + r2(b.x + 10) + " " + r2(b.y + b.h * 0.66) + "a5 5 0 0 1 10 0a5 5 0 0 1 10 0a5 5 0 0 1 10 0", "none", c.a, 2) +
        line(b.x - 11, b.y + b.h / 2, b.x, b.y + b.h / 2, c.a, 2.4) +
        line(b.x + b.w, b.y + b.h / 2, b.x + b.w + 11, b.y + b.h / 2, c.a, 2.4);
    },
    inductorCoil: function (c) {
      var i, out = "";
      for (i = 0; i < 4; i += 1) {
        out += path("M" + r2(36 + i * 22) + " 66a11 11 0 0 1 22 0", "none", c.a, 2.4);
      }
      return out + line(14, 66, 36, 66, c.a, 2.4) + line(124, 66, 146, 66, c.a, 2.4);
    },
    bead: function (c) {
      var b = body(c);
      return rect(b.x, b.y, b.w, b.h, 3, c.a, c.a, 1.6, 0.14) +
        path("M" + r2(b.x + 6) + " " + r2(b.y + b.h * 0.3) + "h" + r2(b.w - 12) +
          "M" + r2(b.x + 6) + " " + r2(b.y + b.h * 0.5) + "h" + r2(b.w - 12) +
          "M" + r2(b.x + 6) + " " + r2(b.y + b.h * 0.7) + "h" + r2(b.w - 12), "none", c.a, 1.6) +
        line(b.x - 10, b.y + b.h / 2, b.x, b.y + b.h / 2, c.a, 2.4) +
        line(b.x + b.w, b.y + b.h / 2, b.x + b.w + 10, b.y + b.h / 2, c.a, 2.4);
    },
    commonMode: function (c) {
      return rect(28, 34, 104, 40, 5, c.a, c.a, 1.8, 0.1) +
        path("M40 62a6 6 0 0 1 12 0a6 6 0 0 1 12 0a6 6 0 0 1 12 0", "none", c.a, 2) +
        path("M40 42a6 6 0 0 1 12 0a6 6 0 0 1 12 0a6 6 0 0 1 12 0", "none", c.a, 2) +
        path("M92 30v48", "none", c.a, 2.4) +
        line(12, 42, 40, 42, c.a, 2.2) + line(12, 62, 40, 62, c.a, 2.2) +
        line(120, 42, 148, 42, c.a, 2.2) + line(120, 62, 148, 62, c.a, 2.2);
    },
    transformer: function (c) {
      return rect(62, 24, 36, 60, 4, c.a, c.a, 1.8, 0.1) +
        rect(58, 24, 5, 60, 2, c.a, "none", 0, 0.9) + rect(97, 24, 5, 60, 2, c.a, "none", 0, 0.9) +
        path("M34 34a8 8 0 0 1 16 0a8 8 0 0 1 16 0a8 8 0 0 1 16 0", "none", c.a, 2) +
        path("M126 34a8 8 0 0 1 16 0a8 8 0 0 1 16 0", "none", c.a, 2) +
        line(20, 34, 34, 34, c.a, 2.2) + line(142, 34, 150, 34, c.a, 2.2) +
        path("M34 74a8 8 0 0 1 16 0a8 8 0 0 1 16 0a8 8 0 0 1 16 0", "none", c.a, 2) +
        line(20, 74, 34, 74, c.a, 2.2) + line(108, 74, 126, 74, c.a, 2.2);
    },
    diodeAxial: function (c) {
      return rect(46, 36, 68, 32, 5, c.a, c.a, 1.8, 0.12) +
        rect(96, 36, 12, 32, 3, c.a, "none", 0, 0.85) +
        path("M14 52h32M114 52h32", "none", c.a, 2.6) +
        path("M62 44h-8v16h8", "none", c.a, 1.6);
    },
    diodeSchottky: function (c) {
      return rect(46, 36, 68, 32, 5, c.a, c.a, 1.8, 0.12) +
        rect(96, 36, 12, 32, 3, c.a, "none", 0, 0.85) +
        path("M14 52h32M114 52h32", "none", c.a, 2.6) +
        path("M60 44v10h-8v-6M104 44v16h8v-6", "none", c.a, 1.6);
    },
    diodeZener: function (c) {
      return rect(46, 36, 68, 32, 5, c.a, c.a, 1.8, 0.12) +
        rect(96, 36, 12, 32, 3, c.a, "none", 0, 0.85) +
        path("M14 52h32M114 52h32", "none", c.a, 2.6) +
        path("M59 44h-6v16h6M100 44h6v16h-6", "none", c.a, 1.6);
    },
    diodeTvs: function (c) {
      return rect(44, 34, 72, 36, 5, c.a, c.a, 1.8, 0.12) +
        path("M62 52l14-14v28z", "none", c.a, 1.8) +
        path("M98 52l-14-14v28z", "none", c.a, 1.8) +
        path("M14 52h30M116 52h30", "none", c.a, 2.6);
    },
    sotArray: function (c) {
      var b = body(c, 1.15);
      return rect(b.x, b.y, b.w, b.h, 4, c.a, c.a, 1.8, 0.14) +
        line(b.x + b.w * 0.3, b.y - 9, b.x + b.w * 0.3, b.y, c.a, 2.2) +
        line(b.x + b.w * 0.7, b.y - 9, b.x + b.w * 0.7, b.y, c.a, 2.2) +
        line(b.x + b.w * 0.5, b.y + b.h, b.x + b.w * 0.5, b.y + b.h + 9, c.a, 2.2) +
        path("M" + r2(b.x + 8) + " " + r2(b.y + b.h * 0.7) + "l10-10v20z", "none", c.a, 1.4) +
        path("M" + r2(b.x + b.w - 8) + " " + r2(b.y + b.h * 0.3) + "l-10 10v-20z", "none", c.a, 1.4);
    },
    bridge: function (c) {
      return rect(38, 28, 84, 50, 6, c.a, c.a, 1.9, 0.1) +
        path("M38 61l14-14 12 12 12-12 12 12 14-14", "none", c.a, 1.6) +
        line(24, 40, 38, 40, c.a, 2.2) + line(38, 66, 24, 66, c.a, 2.2) +
        line(122, 40, 136, 40, c.a, 2.2) + line(122, 66, 136, 66, c.a, 2.2);
    },
    canTo92: function (c) {
      return path("M56 62a24 24 0 0 1 48 0z", c.a, c.a, 1.9, 0.12) +
        line(62, 62, 62, 62, c.a, 2) +
        line(66, 62, 60, 100, c.a, 2.4) + line(80, 62, 80, 100, c.a, 2.4) +
        line(94, 62, 100, 100, c.a, 2.4);
    },
    sotMosfet: function (c) {
      var b = body(c, 1.15);
      return rect(b.x, b.y, b.w, b.h, 4, c.a, c.a, 1.8, 0.14) +
        line(b.x + b.w * 0.3, b.y - 9, b.x + b.w * 0.3, b.y, c.a, 2.2) +
        line(b.x + b.w * 0.7, b.y - 9, b.x + b.w * 0.7, b.y, c.a, 2.2) +
        line(b.x + b.w * 0.5, b.y + b.h, b.x + b.w * 0.5, b.y + b.h + 9, c.a, 2.2) +
        path("M" + r2(b.x + 10) + " " + r2(b.y + b.h / 2) + "h10M" + r2(b.x + b.w - 20) + " " +
          r2(b.y + b.h * 0.28) + "v" + r2(b.h * 0.44), "none", c.a, 1.6);
    },
    powerTab: function (c) {
      return rect(50, 22, 60, 52, 4, c.a, c.a, 2, 0.12) +
        rect(66, 22, 28, 10, 2, c.a, "none", 0, 0.85) +
        line(62, 74, 62, 100, c.a, 2.6) + line(80, 74, 80, 100, c.a, 2.6) +
        line(98, 74, 98, 100, c.a, 2.6) +
        path("M50 40h60", "none", c.a, 1.2, "4 3");
    },
    icDual: function (c) {
      var n = Math.max(2, Math.min(14, Math.round((c.pins || 8) / 2)));
      var b = body(c, 0.86);
      return rect(b.x, b.y, b.w, b.h, 4, c.a, c.a, 1.9, 0.12) +
        leadsX(c, b, n, 12) +
        circ(b.x + 10, b.y + 10, 3.2, "none", c.a, 1.4) +
        path("M" + r2(b.x + b.w * 0.3) + " " + r2(b.y + b.h * 0.5) + "h" + r2(b.w * 0.4), "none", c.a, 1.3, "5 4");
    },
    icQuad: function (c) {
      var per = Math.max(2, Math.min(16, Math.round((c.pins || 32) / 4)));
      var b = body(c, 1);
      return rect(b.x, b.y, b.w, b.h, 5, c.a, c.a, 2, 0.12) +
        leadsY(c, b, per, 12) + leadsX(c, b, per, 12) +
        circ(b.x + 12, b.y + 12, 3.4, "none", c.a, 1.5) +
        rect(b.x + b.w * 0.28, b.y + b.h * 0.28, b.w * 0.44, b.h * 0.44, 3, c.a, c.a, 1.2, 0.5);
    },
    icBga: function (c) {
      var i, j, out = rect(48, 22, 64, 60, 6, c.a, c.a, 2, 0.12);
      for (i = 0; i < 4; i += 1) {
        for (j = 0; j < 4; j += 1) {
          out += circ(60 + i * 13, 34 + j * 13, 3, c.a, "none", 0, 0.75);
        }
      }
      return out + circ(58, 32, 3.6, "none", c.a, 1.4);
    },
    sotIc: function (c) {
      var b = body(c, 1.2);
      return rect(b.x, b.y, b.w, b.h, 4, c.a, c.a, 1.8, 0.14) +
        line(b.x + b.w * 0.25, b.y - 9, b.x + b.w * 0.25, b.y, c.a, 2.2) +
        line(b.x + b.w * 0.5, b.y - 9, b.x + b.w * 0.5, b.y, c.a, 2.2) +
        line(b.x + b.w * 0.75, b.y - 9, b.x + b.w * 0.75, b.y, c.a, 2.2) +
        line(b.x + b.w * 0.3, b.y + b.h, b.x + b.w * 0.3, b.y + b.h + 9, c.a, 2.2) +
        line(b.x + b.w * 0.7, b.y + b.h, b.x + b.w * 0.7, b.y + b.h + 9, c.a, 2.2);
    },
    moduleCan: function (c) {
      return rect(26, 22, 108, 60, 6, c.a, c.a, 2, 0.1) +
        rect(42, 32, 62, 40, 4, "#ffffff", c.a, 1.7) +
        line(112, 32, 112, 72, c.a, 1.4) +
        path("M32 30h8M32 40h8M32 50h8M32 60h8M32 70h8", "none", c.a, 2) +
        path("M120 30h8M120 40h8M120 50h8M120 60h8M120 70h8", "none", c.a, 2);
    },
    moduleAntenna: function (c) {
      return rect(24, 30, 112, 54, 6, c.a, c.a, 2, 0.1) +
        path("M34 44v26a6 6 0 0 0 6 6h44a6 6 0 0 0 6-6V44", "none", c.a, 1.8) +
        path("M104 40h24M104 48h24M104 56h24M104 64h24M104 72h24", "none", c.a, 1.6) +
        path("M34 44h-10M34 52h-10M34 60h-10", "none", c.a, 2) +
        path("M126 34v32", "none", c.a, 2.4);
    },
    relayBox: function (c) {
      return rect(34, 24, 92, 56, 5, c.a, c.a, 2, 0.1) +
        rect(46, 34, 68, 36, 3, "#ffffff", c.a, 1.6) +
        path("M56 44h22a8 8 0 0 1 8 8v8", "none", c.a, 1.8) +
        line(44, 80, 44, 98, c.a, 2.4) + line(62, 80, 62, 98, c.a, 2.4) +
        line(98, 80, 98, 98, c.a, 2.4) + line(116, 80, 116, 98, c.a, 2.4);
    },
    ssrBox: function (c) {
      return rect(36, 26, 88, 52, 5, c.a, c.a, 2, 0.1) +
        path("M56 52l14-16 10 22 12-18", "none", c.a, 2) +
        rect(44, 34, 12, 12, 2, "#ffffff", c.a, 1.4) +
        rect(104, 34, 12, 12, 2, "#ffffff", c.a, 1.4) +
        line(40, 78, 40, 96, c.a, 2.4) + line(120, 78, 120, 96, c.a, 2.4);
    },
    optoDual: function (c) {
      var b = body(c, 1);
      return rect(b.x, b.y, b.w, b.h, 4, c.a, c.a, 1.9, 0.12) +
        path("M" + r2(b.x + 14) + " " + r2(b.y + b.h * 0.5) + "l12-12v24z", "none", c.a, 1.6) +
        line(b.x + b.w * 0.62, b.y + 8, b.x + b.w * 0.62, b.y + b.h - 8, c.a, 1.6) +
        path("M" + r2(b.x + b.w * 0.72) + " " + r2(b.y + b.h * 0.34) + "l10-8M" +
          r2(b.x + b.w * 0.72) + " " + r2(b.y + b.h * 0.66) + "l10 8", "none", c.a, 1.4) +
        leadsX(c, b, 2, 12) + circ(b.x + 11, b.y + 11, 3, "none", c.a, 1.4);
    },
    ledSmd: function (c) {
      var b = body(c, 1.1);
      return rect(b.x, b.y, b.w, b.h, 3, c.a, c.a, 1.7, 0.2) +
        circ(80, b.y + b.h / 2, Math.min(9, b.h * 0.3), "#ffffff", c.a, 1.4) +
        path("M" + r2(b.x + b.w * 0.5) + " " + r2(b.y - 12) + "l-6 9h9l-6 9", "none", c.a, 1.8) +
        path("M" + r2(b.x + b.w * 0.16) + " " + r2(b.y - 8) + "l-5 8M" +
          r2(b.x + b.w * 0.84) + " " + r2(b.y - 8) + "l5 8", "none", c.a, 1.6);
    },
    ledDome: function (c) {
      return path("M58 62a22 22 0 0 1 44 0z", c.a, c.a, 2, 0.2) +
        rect(58, 62, 44, 6, 3, c.a, c.a, 1.6, 0.4) +
        line(66, 68, 62, 100, c.a, 2.4) + line(94, 68, 98, 100, c.a, 2.4) +
        path("M108 34l8-8M112 46h12M108 58l8 8", "none", c.a, 2);
    },
    ledPower: function (c) {
      return rect(46, 26, 68, 52, 8, c.a, c.a, 2, 0.14) +
        circ(80, 52, 16, "#ffffff", c.a, 1.6) +
        path("M80 26v-8M56 40l-8-6M104 40l8-6", "none", c.a, 1.6) +
        path("M40 78h80", "none", c.a, 1.3, "4 3");
    },
    ledRgb: function (c) {
      var b = body(c, 1.15);
      return rect(b.x, b.y, b.w, b.h, 3, c.a, c.a, 1.7, 0.12) +
        circ(b.x + b.w * 0.3, b.y + b.h * 0.5, 6, "#e53935", "none", 0, 0.9) +
        circ(b.x + b.w * 0.5, b.y + b.h * 0.5, 6, "#43a047", "none", 0, 0.9) +
        circ(b.x + b.w * 0.7, b.y + b.h * 0.5, 6, "#1e88e5", "none", 0, 0.9);
    },
    sevenSeg: function (c) {
      return rect(46, 16, 68, 78, 6, c.a, c.a, 2, 0.1) +
        path("M60 28h28M92 32v20M92 56v20M60 84h28M56 78v-20M56 34v20M60 56h28",
          "none", c.a, 2.6) +
        line(44, 94, 44, 108, c.a, 2.2) + line(60, 94, 60, 108, c.a, 2.2) +
        line(100, 94, 100, 108, c.a, 2.2) + line(116, 94, 116, 108, c.a, 2.2);
    },
    irReceiver: function (c) {
      return path("M58 64a22 22 0 0 1 44 0z", c.a, c.a, 2, 0.18) +
        circ(80, 58, 9, "#ffffff", c.a, 1.6) +
        line(66, 66, 62, 100, c.a, 2.4) + line(80, 66, 80, 100, c.a, 2.4) +
        line(94, 66, 98, 100, c.a, 2.4) +
        path("M112 30l10-6M116 44h12", "none", c.a, 1.8, "4 3");
    },
    crystalSmd: function (c) {
      var b = body(c, 1.15);
      return rect(b.x, b.y, b.w, b.h, 4, c.a, c.a, 1.8, 0.12) +
        rect(b.x + b.w * 0.18, b.y + b.h * 0.2, b.w * 0.64, b.h * 0.6, 3, "#ffffff", c.a, 1.5) +
        line(b.x, b.y + b.h / 2, b.x - 10, b.y + b.h / 2, c.a, 2.4) +
        line(b.x + b.w, b.y + b.h / 2, b.x + b.w + 10, b.y + b.h / 2, c.a, 2.4);
    },
    crystalCan: function (c) {
      return rect(46, 34, 68, 36, 6, c.a, c.a, 2, 0.12) +
        path("M56 52h48", "none", c.a, 1.4, "4 3") +
        line(64, 70, 60, 100, c.a, 2.4) + line(96, 70, 100, 100, c.a, 2.4);
    },
    oscillator: function (c) {
      return rect(48, 26, 64, 52, 5, c.a, c.a, 2, 0.12) +
        rect(58, 36, 44, 32, 3, "#ffffff", c.a, 1.5) +
        path("M62 52h8l4-8 6 16 5-8h13", "none", c.a, 1.8) +
        line(56, 78, 56, 96, c.a, 2.4) + line(70, 78, 70, 96, c.a, 2.4) +
        line(90, 78, 90, 96, c.a, 2.4) + line(104, 78, 104, 96, c.a, 2.4);
    },
    resonator: function (c) {
      return path("M52 62a28 28 0 0 1 56 0z", c.a, c.a, 2, 0.14) +
        path("M62 56h36M62 48h36", "none", c.a, 1.4) +
        line(62, 62, 58, 98, c.a, 2.4) + line(80, 62, 80, 98, c.a, 2.4) +
        line(98, 62, 102, 98, c.a, 2.4);
    },
    sensorChip: function (c) {
      var b = body(c, 1.1);
      return rect(b.x, b.y, b.w, b.h, 5, c.a, c.a, 1.8, 0.12) +
        circ(b.x + b.w * 0.35, b.y + b.h * 0.5, 9, "#ffffff", c.a, 1.5) +
        path("M" + r2(b.x + b.w * 0.62) + " " + r2(b.y + b.h * 0.34) + "h14a7 7 0 0 1 0 14h-14",
          "none", c.a, 1.8) +
        path("M" + r2(b.x + b.w * 0.62) + " " + r2(b.y + b.h * 0.5) + "h20", "none", c.a, 1.6, "4 3") +
        leadsX(c, b, 2, 11);
    },
    headerPins: function (c) {
      var i, n = Math.max(4, Math.min(10, c.pins ? c.pins : 8)), out = "";
      var x0 = 80 - (n * 12) / 2;
      out += rect(x0 - 4, 40, n * 12 + 8, 22, 3, c.a, c.a, 1.8, 0.14);
      for (i = 0; i < n; i += 1) {
        out += rect(x0 + i * 12 + 1, 14, 8, 26, 1.5, c.a, c.a, 1.4, 0.7);
        out += rect(x0 + i * 12 + 1, 62, 8, 26, 1.5, c.a, c.a, 1.4, 0.7);
      }
      return out;
    },
    wireHeader: function (c) {
      var i, out = "";
      out += rect(34, 30, 92, 46, 6, c.a, c.a, 2, 0.12);
      out += rect(46, 40, 68, 26, 3, "#ffffff", c.a, 1.6);
      for (i = 0; i < 4; i += 1) {
        out += line(54 + i * 16, 66, 54 + i * 16, 94, c.a, 2.4);
      }
      out += path("M104 34h16a6 6 0 0 1 6 6v6", "none", c.a, 1.8);
      return out;
    },
    usbReceptacle: function (c) {
      return rect(38, 34, 84, 40, 12, c.a, c.a, 2, 0.12) +
        rect(56, 44, 48, 20, 10, "#ffffff", c.a, 1.8) +
        path("M30 76h100M46 26v8M114 26v8", "none", c.a, 2);
    },
    audioJack: function (c) {
      return circ(78, 52, 26, c.a, c.a, 2, 0.12) +
        circ(78, 52, 12, "#ffffff", c.a, 1.8) +
        path("M104 40h24v24h-24", "none", c.a, 1.8) +
        line(66, 76, 60, 100, c.a, 2.4) + line(78, 76, 78, 100, c.a, 2.4) +
        line(90, 76, 96, 100, c.a, 2.4);
    },
    cardSocket: function (c) {
      return rect(34, 30, 92, 48, 5, c.a, c.a, 2, 0.12) +
        rect(44, 80, 72, 12, 3, c.a, c.a, 1.6, 0.4) +
        path("M44 46h72M44 56h56", "none", c.a, 1.4) +
        path("M120 38h10v30h-10", "none", c.a, 1.6);
    },
    terminalBlock: function (c) {
      var i, out = rect(30, 34, 100, 40, 5, c.a, c.a, 2, 0.14);
      for (i = 0; i < 3; i += 1) {
        out += circ(52 + i * 28, 54, 9, "#ffffff", c.a, 1.6);
        out += path("M" + r2(52 + i * 28 - 5) + " 54h10", "none", c.a, 1.6);
        out += rect(46 + i * 28, 74, 12, 14, 2, c.a, c.a, 1.4, 0.6);
      }
      return out;
    },
    ffcConnector: function (c) {
      var i, out = rect(28, 42, 104, 26, 3, c.a, c.a, 1.9, 0.12);
      for (i = 0; i < 12; i += 1) {
        out += line(34 + i * 8, 42, 34 + i * 8, 30, c.a, 1.6);
        out += line(34 + i * 8, 68, 34 + i * 8, 78, c.a, 1.6);
      }
      out += rect(28, 74, 104, 8, 3, c.a, c.a, 1.5, 0.5);
      return out;
    },
    rfConnector: function (c) {
      return circ(80, 50, 28, c.a, c.a, 2, 0.12) +
        circ(80, 50, 12, "#ffffff", c.a, 1.8) +
        circ(80, 50, 4, c.a, "none", 0, 0.85) +
        path("M56 78l-8 22M104 78l8 22", "none", c.a, 2.4) +
        path("M104 34l14-6M104 50h16", "none", c.a, 1.8, "4 3");
    },
    antennaArt: function (c) {
      return line(80, 100, 80, 34, c.a, 2.8) +
        path("M64 42a22 22 0 0 1 32 0", "none", c.a, 2.2) +
        path("M54 30a36 36 0 0 1 52 0", "none", c.a, 2.2) +
        path("M44 18a50 50 0 0 1 72 0", "none", c.a, 2.2) +
        circ(80, 100, 5, c.a, "none", 0, 0.9);
    },
    tactSwitch: function (c) {
      return rect(48, 30, 64, 46, 6, c.a, c.a, 2, 0.12) +
        rect(66, 22, 28, 12, 4, c.a, c.a, 1.8, 0.5) +
        circ(80, 53, 12, "#ffffff", c.a, 1.6) +
        line(52, 76, 52, 98, c.a, 2.4) + line(66, 76, 66, 98, c.a, 2.4) +
        line(94, 76, 94, 98, c.a, 2.4) + line(108, 76, 108, 98, c.a, 2.4);
    },
    slideSwitch: function (c) {
      return rect(40, 40, 80, 26, 4, c.a, c.a, 2, 0.12) +
        rect(68, 30, 24, 16, 4, c.a, c.a, 1.8, 0.6) +
        line(52, 66, 52, 96, c.a, 2.4) + line(80, 66, 80, 96, c.a, 2.4) +
        line(108, 66, 108, 96, c.a, 2.4);
    },
    encoder: function (c) {
      return circ(80, 48, 24, c.a, c.a, 2, 0.12) +
        rect(70, 16, 20, 16, 3, c.a, c.a, 1.8, 0.6) +
        circ(80, 48, 8, "#ffffff", c.a, 1.5) +
        line(58, 72, 54, 96, c.a, 2.4) + line(70, 72, 70, 96, c.a, 2.4) +
        line(90, 72, 90, 96, c.a, 2.4) + line(102, 72, 106, 96, c.a, 2.4);
    },
    fuseTube: function (c) {
      return rect(46, 38, 68, 28, 12, c.a, c.a, 2, 0.1) +
        rect(42, 42, 16, 20, 3, c.a, c.a, 1.6, 0.7) +
        rect(102, 42, 16, 20, 3, c.a, c.a, 1.6, 0.7) +
        path("M64 52h32", "none", c.a, 2);
    },
    gdtTube: function (c) {
      return rect(44, 36, 72, 32, 12, c.a, c.a, 2, 0.1) +
        path("M62 44v16M72 44v16M92 44v16M102 44v16", "none", c.a, 1.8) +
        path("M14 52h30M116 52h30", "none", c.a, 2.4);
    },
    esdChip: function (c) {
      var b = body(c, 1.15);
      return rect(b.x, b.y, b.w, b.h, 4, c.a, c.a, 1.8, 0.12) +
        path("M" + r2(b.x + b.w * 0.5) + " " + r2(b.y + 4) + "l-9 15h12l-9 15", "none", c.a, 2) +
        line(b.x, b.y + b.h / 2, b.x - 10, b.y + b.h / 2, c.a, 2.4) +
        line(b.x + b.w, b.y + b.h / 2, b.x + b.w + 10, b.y + b.h / 2, c.a, 2.4);
    },
    batteryCell: function (c) {
      return rect(38, 32, 78, 42, 6, c.a, c.a, 2, 0.12) +
        rect(116, 42, 12, 22, 3, c.a, c.a, 1.8, 0.7) +
        line(58, 40, 58, 66, c.a, 2) + line(74, 40, 74, 66, c.a, 2) +
        line(90, 40, 90, 66, c.a, 2) + line(106, 40, 106, 66, c.a, 2);
    },
    batteryHolder: function (c) {
      return rect(30, 34, 100, 40, 6, "#ffffff", c.a, 1.9) +
        rect(46, 28, 68, 34, 6, c.a, c.a, 1.8, 0.14) +
        path("M40 74v18M120 74v18", "none", c.a, 2.2) +
        path("M114 44a8 8 0 0 1 0 16", "none", c.a, 1.8);
    },
    powerModule: function (c) {
      return rect(28, 26, 104, 56, 5, c.a, c.a, 2, 0.1) +
        rect(42, 36, 34, 34, 4, c.a, c.a, 1.7, 0.5) +
        path("M46 66a5 5 0 0 1 10 0a5 5 0 0 1 10 0", "none", c.a, 1.6) +
        rect(86, 40, 30, 24, 3, "#ffffff", c.a, 1.5) +
        line(92, 82, 92, 98, c.a, 2.4) + line(120, 82, 120, 98, c.a, 2.4);
    },
    adapterBox: function (c) {
      return rect(30, 30, 74, 46, 6, c.a, c.a, 2, 0.12) +
        rect(44, 42, 46, 22, 3, "#ffffff", c.a, 1.5) +
        path("M104 46h14a6 6 0 0 1 6 6v30a6 6 0 0 1-6 6", "none", c.a, 2) +
        rect(96, 84, 22, 12, 3, c.a, c.a, 1.7, 0.7);
    },
    solderingIron: function (c) {
      return path("M34 84l58-46", "none", c.a, 5) +
        path("M92 38l16-12 10 14-16 12z", c.a, c.a, 1.8, 0.3) +
        path("M50 76l-12 12", "none", c.a, 3) +
        path("M112 22l10-6M124 32h12M118 42l8 8", "none", c.a, 1.8, "4 3");
    },
    meter: function (c) {
      return rect(38, 22, 84, 62, 7, c.a, c.a, 2, 0.1) +
        rect(50, 32, 60, 24, 3, "#ffffff", c.a, 1.6) +
        path("M58 48l10-8 8 6 12-10", "none", c.a, 1.6) +
        circ(62, 70, 6, "#ffffff", c.a, 1.6) + circ(80, 70, 6, "#ffffff", c.a, 1.6) +
        circ(98, 70, 6, "#ffffff", c.a, 1.6) +
        path("M28 92l16-10M132 92l-16-10", "none", c.a, 2.2);
    },
    handTool: function (c) {
      return path("M46 30a16 16 0 0 0 16 22l26 26a8 8 0 0 0 12-12L74 40a16 16 0 0 0-22 2", "none", c.a, 4) +
        circ(54, 34, 9, "none", c.a, 2.4) +
        path("M96 22l12 12-8 8-12-12z", c.a, c.a, 1.7, 0.4) +
        path("M40 92l24-24", "none", c.a, 3);
    },
    esdStrap: function (c) {
      return rect(34, 40, 60, 30, 15, c.a, c.a, 2, 0.14) +
        circ(64, 55, 8, "#ffffff", c.a, 1.6) +
        path("M94 55h16l14 22", "none", c.a, 2.4) +
        rect(112, 74, 26, 16, 3, c.a, c.a, 1.7, 0.5) +
        path("M40 40h48", "none", c.a, 1.4, "3 3");
    },
    wireSpool: function (c) {
      return circ(80, 54, 32, c.a, c.a, 2, 0.1) + circ(80, 54, 12, "#ffffff", c.a, 1.6) +
        path("M80 22a32 32 0 0 1 28 16M52 70a32 32 0 0 0 28 16", "none", c.a, 1.8) +
        path("M112 54h30a8 8 0 0 1 0 16h-14", "none", c.a, 2.2);
    },
    breadboard: function (c) {
      var i, j, out = rect(28, 32, 104, 44, 4, "#ffffff", c.a, 1.9);
      for (i = 0; i < 11; i += 1) {
        for (j = 0; j < 3; j += 1) {
          out += circ(38 + i * 9, 44 + j * 10, 1.9, c.a, "none", 0, 0.8);
        }
      }
      out += path("M28 54h104", "none", c.a, 1.2, "4 3");
      return out;
    },
    tapeRoll: function (c) {
      return circ(76, 54, 32, c.a, c.a, 2, 0.1) + circ(76, 54, 11, "#ffffff", c.a, 1.8) +
        path("M92 30l30 12v24L92 78", "none", c.a, 2) +
        path("M104 44h24", "none", c.a, 1.4, "3 3");
    },
    cleanerBottle: function (c) {
      return rect(58, 40, 44, 56, 6, c.a, c.a, 2, 0.12) +
        rect(70, 24, 20, 16, 3, c.a, c.a, 1.8, 0.5) +
        path("M90 32h28", "none", c.a, 2.2) +
        path("M112 32l10-6", "none", c.a, 2.2) +
        rect(62, 56, 36, 24, 3, "#ffffff", c.a, 1.5);
    },
    pcbBoard: function (c) {
      var i, out = rect(26, 24, 108, 60, 5, c.a, c.a, 2, 0.1);
      out += rect(38, 36, 34, 22, 3, "#ffffff", c.a, 1.5);
      out += rect(84, 36, 38, 22, 3, "#ffffff", c.a, 1.5);
      out += circ(52, 70, 4, c.a, "none", 0, 0.85) + circ(80, 70, 4, c.a, "none", 0, 0.85) +
        circ(106, 70, 4, c.a, "none", 0, 0.85);
      for (i = 0; i < 4; i += 1) {
        out += line(30, 30 + i * 16, 38, 30 + i * 16, c.a, 1.4);
      }
      return out;
    },
    heatsink: function (c) {
      var i, out = rect(28, 30, 104, 12, 3, c.a, c.a, 2, 0.3);
      for (i = 0; i < 6; i += 1) {
        out += rect(34 + i * 17, 42, 10, 42, 2, c.a, c.a, 1.5, 0.2);
      }
      out += rect(28, 84, 104, 10, 3, c.a, c.a, 1.8, 0.45);
      return out;
    },
    fan: function (c) {
      var i, out = rect(28, 20, 104, 72, 8, c.a, c.a, 2, 0.1);
      out += circ(80, 56, 26, "#ffffff", c.a, 1.6);
      for (i = 0; i < 5; i += 1) {
        out += path("M80 56q" + r2(18 * Math.cos(i * 1.26)) + " " + r2(18 * Math.sin(i * 1.26)) +
          " " + r2(24 * Math.cos(i * 1.26 + 0.5)) + " " + r2(24 * Math.sin(i * 1.26 + 0.5)), "none", c.a, 3);
      }
      out += circ(80, 56, 6, c.a, "none", 0, 0.8);
      out += circ(40, 28, 3, c.a, "none", 0, 0.7) + circ(40, 84, 3, c.a, "none", 0, 0.7) +
        circ(120, 28, 3, c.a, "none", 0, 0.7) + circ(120, 84, 3, c.a, "none", 0, 0.7);
      return out;
    },
    thermalPad: function (c) {
      return rect(40, 26, 80, 56, 8, c.a, c.a, 2, 0.12) +
        path("M40 66l18-18 14 14 16-16 32 30", "none", c.a, 1.6, "4 3") +
        path("M104 26l16 16-16 3z", c.a, c.a, 1.6, 0.5);
    },
    standoff: function (c) {
      return path("M62 34l18-10 18 10v34l-18 10-18-10z", c.a, c.a, 2, 0.14) +
        path("M62 34l18 10 18-10M80 44v34", "none", c.a, 1.5) +
        circ(80, 24, 8, "#ffffff", c.a, 1.7) + circ(80, 84, 8, "#ffffff", c.a, 1.7);
    },
    screw: function (c) {
      return circ(74, 40, 18, c.a, c.a, 2, 0.16) +
        path("M60 40h28M74 26v28", "none", c.a, 2) +
        path("M74 58v40", "none", c.a, 3) +
        path("M68 66h12M68 74h12M68 82h12M68 90h12", "none", c.a, 1.5);
    }
  };

  /* ------------------------------------------------------------ 对外接口 */
  var CACHE = {};

  function norm(part) {
    part = part || {};
    return {
      model: part.model || part.m || "",
      pkg: part.pkg || part.k || "",
      type: part.type || part.t || "",
      catId: part.catId || part.cat || "",
      img: part.img || ""
    };
  }

  function paletteFor(catId) {
    return PALETTE[catId] || "#0f3d75";
  }

  function shapeFor(part) {
    var p = norm(part);
    var base = TYPE_SHAPE[p.type] || CAT_FALLBACK[p.catId] || "chip";
    /* 少量按封装细化的例外：插件晶振、直插 LED、插件电解 */
    if (base === "crystalSmd" && /HC-49|插件|直插/i.test(p.pkg)) { return "crystalCan"; }
    if (base === "ledSmd" && /D\d|插件|直插/i.test(p.pkg)) { return "ledDome"; }
    if (base === "moduleAntenna" && /插件|成品/i.test(p.pkg)) { return "moduleCan"; }
    return base;
  }

  function clip(value, max) {
    var s = String(value == null ? "" : value);
    return s.length > max ? s.slice(0, max - 1) + "…" : s;
  }

  /* 粗略估算文字宽度：CJK 按全宽，拉丁/数字按 0.62em */
  function textWidth(value, size) {
    var s = String(value || ""), w = 0, i, code;
    for (i = 0; i < s.length; i += 1) {
      code = s.charCodeAt(i);
      w += (code > 0x2e80 ? 1 : 0.62) * size;
    }
    return w;
  }

  function fitText(value, size, maxWidth) {
    var s = String(value == null ? "" : value);
    if (textWidth(s, size) <= maxWidth) { return s; }
    var out = s;
    while (out.length > 1 && textWidth(out + "…", size) > maxWidth) {
      out = out.slice(0, -1);
    }
    return out + "…";
  }

  function svgFor(part, opts) {
    var p = norm(part);
    opts = opts || {};
    var size = opts.size === "sm" || opts.size === "lg" ? opts.size : "md";
    var typeLabel = opts.typeLabel || "";
    var key = [p.model, p.pkg, p.type, size, typeLabel].join("|");
    if (CACHE[key]) { return CACHE[key]; }

    var shapeId = shapeFor(p);
    var pk = parsePkg(p.pkg);
    var c = { a: paletteFor(p.catId), bw: pk.bw, bh: pk.bh, pins: pk.pins, sides: pk.sides, kind: pk.kind };
    var inner = (SHAPES[shapeId] || SHAPES.chip)(c);
    var text = "";
    if (size !== "sm") {
      var modelSize = size === "lg" ? 15 : 13;
      text += '<text x="80" y="' + (size === "lg" ? 101 : 100) + '" text-anchor="middle" font-size="' +
        modelSize + '" font-weight="600" fill="' + INK + '" font-family="ui-monospace, Menlo, monospace">' +
        esc(fitText(p.model, modelSize, 144)) + "</text>";
      if (size === "lg") {
        text += '<text x="80" y="115" text-anchor="middle" font-size="12" fill="#6b7d93" ' +
          'font-family="system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif">' +
          esc(fitText(p.pkg, 12, 144)) + "</text>";
      }
    }
    var label = [p.model, p.pkg, typeLabel].filter(Boolean).join(" · ");
    var svg = '<svg class="part-art" viewBox="0 0 160 120" role="img" aria-label="' + esc(label) +
      '" xmlns="http://www.w3.org/2000/svg">' +
      "<title>" + esc(label) + "</title>" +
      rect(2, 2, 156, 116, 10, CARD_BG, CARD_LINE, 1.4) +
      inner + text + "</svg>";
    CACHE[key] = svg;
    return svg;
  }

  function html(part, opts) {
    var p = norm(part);
    var typeLabel = (opts && opts.typeLabel) || "";
    if (p.img) {
      var alt = [p.model, p.pkg, typeLabel].filter(Boolean).join(" · ");
      return '<img class="part-art part-art--photo" src="' + esc(p.img) + '" alt="' + esc(alt) +
        '" loading="lazy" decoding="async">';
    }
    return svgFor(part, opts);
  }

  window.XWK_PART_ART = {
    svgFor: svgFor,
    html: html,
    shapeFor: shapeFor,
    paletteFor: paletteFor,
    parsePkg: parsePkg,
    typeShapes: TYPE_SHAPE,
    shapeIds: Object.keys(SHAPES),
    cacheSize: function () { return Object.keys(CACHE).length; }
  };
})();
