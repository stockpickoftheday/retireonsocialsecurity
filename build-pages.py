#!/usr/bin/env python3
"""Generate the Social Security calculator site pages.
Shared header/footer/nav so every page matches. Run: python3 gen_ss.py
Writes into ~/workspace/social-security-site/ (same dir as this script
when run from there; output dir is the script's directory).
"""
import json
import os

OUT = "/home/hatch/workspace/social-security-site"
SITE = "Social Security Calculator"
TAGLINE = "A Social Security calculator for Americans. No sign-up, no sales pitch."

NAV = [
    ("index.html", "Calculator"),
    ("62-vs-67-vs-70.html", "62 vs 67 vs 70"),
    ("break-even.html", "Break-Even Age"),
    ("full-retirement-age.html", "Full Retirement Age"),
    ("spousal-survivor.html", "Spousal & Survivor"),
    ("tax-on-benefits.html", "Is It Taxable?"),
    ("cola.html", "COLA"),
    ("where-to-retire.html", "Where to Retire"),
    ("about.html", "About"),
    ("privacy.html", "Privacy"),
    ("contact.html", "Contact"),
]

def nav_html(current):
    links = []
    for href, label in NAV:
        cls = ' class="current"' if href == current else ""
        links.append(f'      <a href="{href}"{cls}>{label}</a>')
    return "\n".join(links)

def header(current):
    return f"""<header class="site">
  <div class="wrap">
    <p class="site-title"><a href="index.html">{SITE}</a></p>
    <p class="tagline">{TAGLINE}</p>
    <nav class="main" aria-label="Main navigation">
{nav_html(current)}
    </nav>
  </div>
</header>"""

FOOTER = f"""<footer class="site">
  <div class="wrap">
    <nav aria-label="Footer navigation">
{nav_html("")}
    </nav>
    <p>{SITE} — an educational calculator. Not financial advice. Figures verified November 2026; rules and amounts change, so confirm them with the Social Security Administration at ssa.gov before you claim.</p>
  </div>
</footer>"""

AD = '<div class="ad-slot" data-ad-slot="{slot}"><!-- AdSense code goes here when approved --></div>'

def page(filename, title, description, body, lang="en-US"):
    url = "https://retireonsocialsecurity.com/" if filename == "index.html" else "https://retireonsocialsecurity.com/" + filename
    ld = json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": url, "description": description}, ensure_ascii=False)
    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<script type="application/ld+json">
{ld}
</script>
<link rel="stylesheet" href="style.css">
{'' if filename == 'index.html' else ''}
</head>
<body>
{header(filename)}
{AD.format(slot='leaderboard')}
<main>
  <div class="wrap">
{body}
  </div>
</main>
{AD.format(slot='footer')}
{FOOTER}
</body>
</html>
"""
    # index.html needs the calculator script; add it properly
    if filename == "index.html":
        html = html.replace('<link rel="stylesheet" href="style.css">',
                            '<link rel="stylesheet" href="style.css">\n<script src="calculator.js" defer></script>')
    path = os.path.join(OUT, filename)
    with open(path, "w") as f:
        f.write(html)
    print("wrote", filename, len(html), "bytes")

# ---------------------------------------------------------------- index
INDEX_BODY = """
    <section class="hero">
      <p class="eyebrow">United States &middot; Based on Social Security's own formula</p>
      <h1>Social Security Calculator: How Much Will You Get?</h1>
      <p class="lede">A Social Security calculator estimates your monthly benefit before you claim it. You enter what you earn, or the benefit from your Social Security statement, and it shows what you'd get at every age you could start, from 62 to 70. It uses the same formula Social Security uses: your 35 highest-earning years, averaged into a monthly figure, then adjusted for when you claim. The number is an estimate in today's dollars. Your real benefit depends on your actual earnings record, which you can check at ssa.gov.</p>
      <ul class="chips">
        <li>&#10003; No sign-up</li>
        <li>&#10003; Nothing leaves your browser</li>
        <li>&#10003; Every claiming age, 62 to 70</li>
      </ul>
    </section>

    <div class="calc-layout">
      <section class="calc-box" id="calculator" aria-label="Social Security benefits calculator">
        <h2>Your numbers</h2>
        <p class="sub">Fill in your numbers — the answer updates as you type.</p>

        <div class="mode-toggle" role="radiogroup" aria-label="How to estimate your benefit">
          <label><input type="radio" name="mode" id="mode-earnings" value="earnings" checked> <span>From my earnings<span class="hint">Estimate from your annual pay, assuming 35 years at that level.</span></span></label>
          <label><input type="radio" name="mode" id="mode-statement" value="statement"> <span>From my statement<span class="hint">Use the benefit at full retirement age shown on your Social Security statement.</span></span></label>
        </div>

        <div class="field" id="earnings-field">
          <label for="earnings">Your annual earnings</label>
          <span class="money-input"><span>$</span><input type="number" id="earnings" value="70000" min="0" max="184500" step="1000" inputmode="numeric"></span>
          <span class="hint">Your pay before tax, in today's dollars. Earnings above $184,500 a year (the 2026 wage base) do not count toward your benefit.</span>
        </div>

        <div class="field" id="statement-field" style="display:none">
          <label for="statement-benefit">Your benefit at full retirement age (from your statement)</label>
          <span class="money-input"><span>$</span><input type="number" id="statement-benefit" value="2000" min="0" step="10" inputmode="numeric"></span>
          <span class="hint">Find it on your statement at ssa.gov/myaccount — it is the monthly amount at your full retirement age.</span>
        </div>

        <div class="field-row">
          <div class="field">
            <label for="birth-year">Year you were born</label>
            <input type="number" id="birth-year" value="1964" min="1920" max="2010" step="1" inputmode="numeric">
            <span class="hint">Your birth year sets your full retirement age: 67 if you were born in 1960 or later.</span>
          </div>
          <div class="field">
            <label for="life-expectancy">How long do you expect to live? (age)</label>
            <input type="number" id="life-expectancy" value="85" min="63" max="100" step="1" inputmode="numeric">
            <span class="hint">Used only for the lifetime totals below. Your best guess is fine — try 85, then try 90 and see how the answer changes.</span>
          </div>
        </div>

        <p><button type="button" class="example-btn" id="load-example">Try the example: $70,000 a year, born 1964</button></p>
      </section>

      <div class="results-col">
        <div class="results" id="results">
          <p class="big-label">Your benefit at full retirement age</p>
          <p class="big" id="out-big">—</p>
          <p class="big-sub" id="out-big-sub">—</p>
          <dl>
            <div class="row">
              <dt>Full retirement age benefit (your PIA)</dt>
              <dd id="out-pia">—</dd>
            </div>
            <div class="row">
              <dt>At 62 (earliest)</dt>
              <dd id="out-at62">—</dd>
            </div>
            <div class="row">
              <dt>At 70 (latest)</dt>
              <dd id="out-at70">—</dd>
            </div>
          </dl>
          <p class="note" id="out-mode-note"></p>
          <p class="note" id="out-aime"></p>
          <p class="note" id="out-fra"></p>
        </div>
      </div>
    </div>

    <div class="sticky-bar" id="sticky-bar"><span>At full retirement age</span><strong id="sticky-big">—</strong></div>

    <div class="ad-slot" data-ad-slot="in-content"><!-- AdSense code goes here when approved --></div>

    <h2>Your benefit at every age, 62 to 70</h2>
    <div class="table-scroll">
    <table class="claim-table">
      <thead><tr><th>Claim at age</th><th class="num">Monthly benefit</th><th class="num">Lifetime total</th></tr></thead>
      <tbody>
        <tr><td>62</td><td class="num" id="out-age-62">—</td><td class="num" id="out-life-62">—</td></tr>
        <tr><td>63</td><td class="num" id="out-age-63">—</td><td class="num" id="out-life-63">—</td></tr>
        <tr><td>64</td><td class="num" id="out-age-64">—</td><td class="num" id="out-life-64">—</td></tr>
        <tr><td>65</td><td class="num" id="out-age-65">—</td><td class="num" id="out-life-65">—</td></tr>
        <tr><td>66</td><td class="num" id="out-age-66">—</td><td class="num" id="out-life-66">—</td></tr>
        <tr class="best"><td>67 (full retirement age)</td><td class="num" id="out-age-67">—</td><td class="num" id="out-life-67">—</td></tr>
        <tr><td>68</td><td class="num" id="out-age-68">—</td><td class="num" id="out-life-68">—</td></tr>
        <tr><td>69</td><td class="num" id="out-age-69">—</td><td class="num" id="out-life-69">—</td></tr>
        <tr><td>70</td><td class="num" id="out-age-70">—</td><td class="num" id="out-life-70">—</td></tr>
      </tbody>
    </table>
    </div>
    <p>Lifetime totals assume you live to the age you entered above (<span id="out-life-note">—</span>). Change it and watch the totals move — living longer is what makes waiting pay off.</p>

    <h2>When does waiting catch up?</h2>
    <dl>
      <dt>Claim at full retirement age instead of 62</dt>
      <dd>Breaks even at <strong id="out-be-67-62">—</strong></dd>
      <dt>Claim at 70 instead of 62</dt>
      <dd>Breaks even at <strong id="out-be-70-62">—</strong></dd>
      <dt>Claim at 70 instead of full retirement age</dt>
      <dd>Breaks even at <strong id="out-be-70-fra">—</strong></dd>
    </dl>
    <p>Read more on the <a href="break-even.html">break-even age</a> page, and the full comparison on <a href="62-vs-67-vs-70.html">62 vs 67 vs 70</a>.</p>

    <section class="example" aria-label="Worked example">
      <h3>Worked example — see the math</h3>
      <p>Someone born in 1964 (full retirement age 67) who earned <strong>$70,000 a year</strong> for 35 years, and expects to live to <strong>85</strong>.</p>
      <dl>
        <dt>Average indexed monthly earnings (AIME)</dt>
        <dd>$5,833 ($70,000 &divide; 12)</dd>
        <dt>Benefit at full retirement age (PIA)</dt>
        <dd><strong>$2,612 a month</strong></dd>
        <dt>At 62 (70% of full)</dt>
        <dd>$1,828 a month</dd>
        <dt>At 70 (124% of full)</dt>
        <dd>$3,239 a month</dd>
        <dt>Break-even, 70 vs 62</dt>
        <dd>About 80 years and 4 months</dd>
        <dt>Lifetime total to age 85, claiming at 62</dt>
        <dd>$504,528</dd>
        <dt>Lifetime total to age 85, claiming at 70</dt>
        <dd>$583,020</dd>
      </dl>
      <p>Press "Try the example" above and the calculator will show these same numbers.</p>
    </section>

    <h2>How much Social Security will I get?</h2>
    <p>How much you'll get depends on two things: what you earned over your working life, and the age you start collecting. Social Security averages your 35 highest-earning years, runs them through its formula, and that gives your full benefit at age 67, for anyone born in 1960 or later. The average retired worker gets about $2,071 a month in 2026. The most anyone can get is $5,181 a month, and only by earning at the top for 35 years and waiting until 70. Your own statement at ssa.gov shows your exact estimate.</p>

    <section class="example" aria-label="Should I take it at 62 or 70?">
      <h3>Should I take it at 62 or 70?</h3>
      <p>Claiming at 62 means 70% of your full benefit, for life. Waiting until 70 means 124% — but you skip eight years of checks. The two roughly even out around age 80 or 81: live past that and waiting wins. <a href="62-vs-67-vs-70.html">See the full comparison &rarr;</a></p>
    </section>

    <section class="example" aria-label="Spousal benefits">
      <h3>Spousal benefits</h3>
      <p>If you are married, you may be able to claim up to 50% of your spouse's full benefit — and it does not reduce what they get. The survivor benefit is different: if your spouse dies, you can step into 100% of what they were receiving. <a href="spousal-survivor.html">Learn how spousal and survivor benefits work &rarr;</a></p>
      <p>Read more:</p>
      <ul>
        <li><a href="https://www.aarp.org/social-security/faq/collecting-benefits-as-spouse/">Collecting Social Security Benefits as a Spouse</a> (AARP)</li>
        <li><a href="https://www.aarp.org/videos/social-security/6395248215112/">How Social Security Spousal Benefits Work</a> (AARP video)</li>
        <li><a href="https://fedlaws.org/how-do-social-security-spousal-benefits-work/">How Do Social Security Spousal Benefits Work?</a> (FedLaws)</li>
      </ul>
    </section>

    <h2>How the number is worked out</h2>
    <h3>Your 35 best years</h3>
    <p>Social Security takes your earnings from your 35 highest-earning years, adjusts each year for wage growth, and averages them into a monthly figure called your AIME (average indexed monthly earnings). Years you earned little or nothing still count if you worked fewer than 35 years — they go in as zeros and pull the average down. That is why a long career matters so much.</p>
    <h3>The 90/32/15% formula</h3>
    <p>Your AIME runs through a three-part formula to give your PIA (primary insurance amount) — the benefit you would get at full retirement age. For workers first eligible in 2026, the formula pays 90% of the first $1,286 of AIME, 32% of the part from $1,286 to $7,749, and 15% of anything above $7,749. The formula is progressive on purpose: lower earners get a bigger share of their past earnings replaced. The dollar cutoffs, called bend points, rise each year with average wages — for 2027 they are $1,340 and $8,077.</p>
    <h3>Claiming age: the big lever</h3>
    <p>Your PIA is only the starting point. Claim before full retirement age and it is cut: 5/9 of 1% for each of the first 36 months early, then 5/12 of 1% per month. With a full retirement age of 67, claiming at 62 means a 30% cut — you get 70% of your full benefit, for life. Wait past full retirement age and it grows 8% a year (2/3 of 1% a month) until 70, when it stops growing. Claiming at 70 gives you 124% of your full benefit.</p>
    <h3>Why your number may differ slightly</h3>
    <p>This calculator assumes you earned the amount you typed, in today's dollars, for all 35 years. Your real record is year by year, with wage indexing, and the bend points that apply are from the year you turn 62. That usually moves the answer by only a few dollars. One exception: very high earners. The wage base was much lower in past years, so a flat $184,500 for 35 years overstates the benefit — the real maximum at full retirement age in 2026 is $4,152 a month, not the $4,369 this simple math gives. For an exact figure, check your statement at <a href="https://www.ssa.gov/myaccount">ssa.gov/myaccount</a>.</p>
    <p>Also see: <a href="62-vs-67-vs-70.html">should I take Social Security at 62 or 70?</a> &middot; <a href="break-even.html">break-even ages</a> &middot; <a href="full-retirement-age.html">full retirement age by birth year</a> &middot; <a href="spousal-survivor.html">spousal and survivor benefits</a> &middot; <a href="tax-on-benefits.html">are benefits taxed?</a> &middot; <a href="cola.html">cost-of-living adjustments</a> &middot; <a href="where-to-retire.html">where to retire on your benefit</a></p>

    <h2>Where to retire on your benefit</h2>
    <p>Once you know your monthly check, the next question is where it goes furthest. The <a href="where-to-retire.html">best places to retire in the US</a> include small cities where the average benefit covers rent with room to spare — and if you want your dollars to stretch further still, some of the <a href="where-to-retire.html">cheapest countries to retire abroad</a> offer a comfortable life for $1,000 to $2,500 a month. Compare the lists, then run your own numbers above.</p>
    <p class="note">This calculator is an estimate for education only. It is not financial advice, and it is not the Social Security Administration. Your real benefit depends on your actual earnings record. Confirm the numbers at ssa.gov/myaccount before you make a claiming decision.</p>
"""

page("index.html",
     "Social Security Calculator — How Much Will I Get at 62, 67, or 70?",
     "Free social security calculator: enter your earnings or your statement benefit and see your monthly check at every age from 62 to 70, plus break-even ages.",
     INDEX_BODY)

# ------------------------------------------------- 62 vs 67 vs 70
BODY_6270 = """
    <section class="page-hero">
      <p class="eyebrow">Claiming age &middot; The biggest decision in Social Security</p>
      <h1>Should I Take Social Security at 62 or 70?</h1>
      <p class="lede">There's no one right answer. It's a bet on how long you'll live. Take it at 62 and you get a smaller check, 70% of your full benefit, but for eight more years. Wait until 70 and the check is 77% bigger for life, but you skip eight years of payments. The two roughly even out around age 80 or 81: live past that and waiting wins; don't, and claiming early was right. Health, family history, whether you need the money now, and whether you're married all tilt the answer.</p>
    </section>

    <div class="ad-slot" data-ad-slot="in-content"><!-- AdSense code goes here when approved --></div>

    <h2>When to take Social Security</h2>
    <p>You can start Social Security any time from 62 to 70, and the month you pick is permanent. Full retirement age is 67 for anyone born in 1960 or later. Claim before that and your check is cut, by 30% at 62. Wait past it and it grows by 8% a year until 70, when it stops growing. There's no benefit to waiting past 70. Most people decide based on three things: how long they expect to live, whether they need the money now, and whether they're still working. Earning too much before full retirement age can mean some benefits are withheld.</p>

    <h2>How much Social Security will I get at 62?</h2>
    <p>At 62 you get 70% of your full benefit, permanently. If your full benefit at 67 would be $2,000 a month, claiming at 62 gives you about $1,400. The average retired worker gets about $2,071 a month at full retirement age in 2026, so the average 62-year-old claimer gets roughly $1,450. The reduction never goes away. You get the smaller amount for the rest of your life, adjusted only for cost-of-living increases. But you also get five extra years of checks before someone waiting until 67 gets anything.</p>

    <h2>62 vs 67 vs 70, side by side</h2>
    <p>The table below uses a full benefit of $2,000 a month at age 67 (for someone born in 1960 or later). Scale it to your own number with the <a href="index.html">Social Security calculator</a>.</p>
    <div class="table-scroll">
    <table>
      <thead><tr><th>Claim at</th><th class="num">Monthly check</th><th class="num">Share of full benefit</th><th>What you give up / gain</th></tr></thead>
      <tbody>
        <tr><td><strong>62</strong></td><td class="num">$1,400</td><td class="num">70%</td><td>Smallest check, but five extra years of payments.</td></tr>
        <tr><td><strong>67 (full retirement age)</strong></td><td class="num">$2,000</td><td class="num">100%</td><td>The full benefit, no cut and no bonus.</td></tr>
        <tr><td><strong>70</strong></td><td class="num">$2,480</td><td class="num">124%</td><td>Biggest check for life, but you skip eight years of payments.</td></tr>
      </tbody>
    </table>
    </div>

    <h2>The case for claiming at 62</h2>
    <ul>
      <li><strong>You need the money now.</strong> If you have stopped working and have no other income, the check is there for a reason.</li>
      <li><strong>Your health is poor, or your parents died young.</strong> If you do not expect to live past about 80, claiming early usually pays more in total.</li>
      <li><strong>You want to stop working.</strong> Social Security was built to replace wages. If work is done, take the check.</li>
    </ul>

    <h2>The case for waiting until 70</h2>
    <ul>
      <li><strong>You expect a long life.</strong> Past about 80 or 81, the bigger check has paid back everything you skipped, and every month after that is pure gain.</li>
      <li><strong>You are the higher earner in a couple.</strong> When you die, your spouse steps into your check. A bigger check protects them for the rest of their life. See <a href="spousal-survivor.html">spousal and survivor benefits</a>.</li>
      <li><strong>You are still working.</strong> Waiting means no earnings test, and your later earnings can even raise your benefit if they replace a low year in your 35-year average.</li>
    </ul>

    <h2>The case for 67, the middle road</h2>
    <p>Claiming at full retirement age is the compromise: no cut, no eight-year wait, and no earnings limit from that month on. For many people it is the sensible default, especially if you retire right around 67 anyway.</p>

    <h2>Working while you collect</h2>
    <p>Before full retirement age, Social Security withholds $1 for every $2 you earn above $24,480 in 2026. In the year you reach full retirement age, the limit is $65,160 and the withholding is $1 for every $3, counting only earnings before the month you reach it. Once you reach full retirement age there is no limit at all. The withheld money is not lost — your benefit is recalculated upward once you reach full retirement age.</p>

    <p class="note">There is no way to know how long you will live, so there is no way to be sure which age was best until afterward. Run your own numbers on the <a href="index.html">calculator</a>, and look at the <a href="break-even.html">break-even ages</a> before you decide. This page is education, not financial advice.</p>
"""
page("62-vs-67-vs-70.html",
     "Should I Take Social Security at 62 or 70? When to Take It",
     "Should you take Social Security at 62 or 70? Compare the monthly checks, the 30% cut at 62, the 24% bonus at 70, and when waiting pays off.",
     BODY_6270)

# ------------------------------------------------- break-even
BODY_BE = """
    <section class="page-hero">
      <p class="eyebrow">Break-even ages &middot; When waiting catches up</p>
      <h1>Social Security Break Even Age: When Waiting Pays Off</h1>
      <p class="lede">The break-even age is when waiting to claim catches up with claiming early, in total dollars collected. For someone whose full retirement age is 67: claiming at 67 instead of 62 breaks even around age 78 or 79; claiming at 70 instead of 62 breaks even around age 80 or 81; and 70 instead of 67 around age 82 or 83. Live past the break-even age and waiting paid off. Die before it and claiming early was the better call. It's just arithmetic. Your health and family history are what make the decision personal.</p>
    </section>

    <div class="ad-slot" data-ad-slot="in-content"><!-- AdSense code goes here when approved --></div>

    <h2>What "break even" means</h2>
    <p>Claiming early gives you more checks, each smaller. Claiming late gives you fewer checks, each bigger. Add up the dollars, and there is one age where the two totals are exactly equal. That is the break-even age. Before it, the early claimer is ahead. After it, the late claimer pulls ahead — and stays ahead for the rest of their life.</p>

    <h2>The break-even ages (full retirement age 67)</h2>
    <div class="table-scroll">
    <table>
      <thead><tr><th>Compare</th><th class="num">Break-even age</th><th>What it means</th></tr></thead>
      <tbody>
        <tr><td>67 vs 62</td><td class="num">About 78&ndash;79</td><td>Wait until 67 and you catch up around 78 or 79.</td></tr>
        <tr><td>70 vs 62</td><td class="num">About 80&ndash;81</td><td>Wait until 70 and you catch up around 80 or 81.</td></tr>
        <tr><td>70 vs 67</td><td class="num">About 82&ndash;83</td><td>The last three years of waiting take the longest to pay back.</td></tr>
      </tbody>
    </table>
    </div>
    <p>These ages barely move with the size of your benefit — they come from the percentages, not the dollars. Use the <a href="index.html">calculator</a> to get your exact break-even ages for your own benefit and birth year.</p>

    <h2>A worked example</h2>
    <p>Full benefit $2,000 a month at 67. At 62 you get $1,400; at 70 you get $2,480. Claim at 62 and by your 70th birthday you have collected $134,400. Claim at 70 and you have collected nothing yet — but from then on you get $1,080 more every month. Divide the $134,400 head start by $1,080 a month and it takes about 124 months, or 10 years and 4 months, to catch up: age 80 and 4 months.</p>

    <h2>What break-even does not capture</h2>
    <ul>
      <li><strong>Your spouse.</strong> If you are the higher earner, your check becomes your spouse's survivor benefit. Waiting can be worth far more to a couple than the break-even age suggests.</li>
      <li><strong>Needing the money now.</strong> Break-even math assumes you can afford to wait. If you cannot, the math does not matter.</li>
      <li><strong>Peace of mind.</strong> A bigger guaranteed check for life is worth something that no total-dollars table can show, especially if you worry about outliving your savings.</li>
      <li><strong>Taxes and other income.</strong> A bigger check can push more of your benefit into tax. See <a href="tax-on-benefits.html">is Social Security taxable?</a></li>
    </ul>

    <p class="note">Break-even ages are arithmetic, not advice. They tell you the age where waiting starts to pay in dollars. Whether you will live past it is a question about your health and your family history — and only you can answer that.</p>
"""
page("break-even.html",
     "Social Security Break Even Age — 62 vs 67 vs 70",
     "Your Social Security break even age: 67 vs 62 is about 78-79, 70 vs 62 about 80-81. See the math and what it leaves out.",
     BODY_BE)

# ------------------------------------------------- full retirement age
BODY_FRA = """
    <section class="page-hero">
      <p class="eyebrow">Full retirement age &middot; The age that sets your benefit</p>
      <h1>Full Retirement Age: What It Is and When You Reach It</h1>
      <p class="lede">Your full retirement age is the age Social Security pays you 100% of your calculated benefit. It's 67 for anyone born in 1960 or later, and 66 and some months for people born between 1943 and 1959. Claim before it and your check is permanently reduced. Wait past it and it grows 8% a year until 70. It matters for more than the amount: once you reach it, there's no limit on how much you can earn while collecting, and any benefits withheld earlier for working get credited back.</p>
    </section>

    <div class="ad-slot" data-ad-slot="in-content"><!-- AdSense code goes here when approved --></div>

    <h2>Full retirement age by birth year</h2>
    <div class="table-scroll">
    <table>
      <thead><tr><th>Born</th><th>Full retirement age</th><th class="num">Claiming at 62 costs you</th></tr></thead>
      <tbody>
        <tr><td>1937 or earlier</td><td>65</td><td class="num">20%</td></tr>
        <tr><td>1938</td><td>65 and 2 months</td><td class="num">20.8%</td></tr>
        <tr><td>1939</td><td>65 and 4 months</td><td class="num">21.7%</td></tr>
        <tr><td>1940</td><td>65 and 6 months</td><td class="num">22.5%</td></tr>
        <tr><td>1941</td><td>65 and 8 months</td><td class="num">23.3%</td></tr>
        <tr><td>1942</td><td>65 and 10 months</td><td class="num">24.2%</td></tr>
        <tr><td>1943&ndash;1954</td><td>66</td><td class="num">25%</td></tr>
        <tr><td>1955</td><td>66 and 2 months</td><td class="num">25.8%</td></tr>
        <tr><td>1956</td><td>66 and 4 months</td><td class="num">26.7%</td></tr>
        <tr><td>1957</td><td>66 and 6 months</td><td class="num">27.5%</td></tr>
        <tr><td>1958</td><td>66 and 8 months</td><td class="num">28.3%</td></tr>
        <tr><td>1959</td><td>66 and 10 months</td><td class="num">29.2%</td></tr>
        <tr><td><strong>1960 or later</strong></td><td><strong>67</strong></td><td class="num"><strong>30%</strong></td></tr>
      </tbody>
    </table>
    </div>
    <p>One quirk: if you were born on January 1, Social Security treats you as born in the previous year, so use that year's row. Your exact full retirement age is also on your statement at ssa.gov/myaccount.</p>

    <h2>Why it matters</h2>
    <ul>
      <li><strong>It sets your full benefit.</strong> Your calculated benefit (your PIA) is what you get if you claim exactly at full retirement age.</li>
      <li><strong>It sets the size of the early cut.</strong> The further full retirement age is from 62, the bigger the reduction for claiming at 62 — 30% for anyone born in 1960 or later.</li>
      <li><strong>It sets the delayed credits.</strong> You earn 8% a year only for months after full retirement age, up to 70. With a full retirement age of 67, that is three years and a 24% bonus.</li>
      <li><strong>It ends the earnings limit.</strong> Before full retirement age, earning above $24,480 in 2026 means some benefits are withheld. From the month you reach full retirement age, there is no limit.</li>
    </ul>

    <h2>Full retirement age is not Medicare age</h2>
    <p>Medicare starts at 65, whatever your full retirement age is. You can sign up for Medicare at 65 and still wait until 67 or 70 to claim Social Security — the two are separate decisions.</p>

    <p class="note">Congress raised the full retirement age from 65 to 67 in 1983, in steps by birth year. The rise is now complete: everyone born in 1960 or later has a full retirement age of 67. Figures verified November 2026.</p>
"""
page("full-retirement-age.html",
     "Full Retirement Age by Birth Year — 67 for Anyone Born 1960 or Later",
     "Full retirement age is 67 if you were born in 1960 or later. Find your age by birth year and see what claiming at 62 costs you.",
     BODY_FRA)

# ------------------------------------------------- spousal / survivor
BODY_SP = """
    <section class="page-hero">
      <p class="eyebrow">For couples &middot; Spousal and survivor benefits</p>
      <h1>Social Security Spousal Benefits and Survivor Benefits</h1>
      <p class="lede">If you're married, you may be able to claim a benefit based on your spouse's record instead of your own, up to 50% of their full benefit at their full retirement age. It doesn't reduce what they get. But there's a catch: the spousal top-up never includes delayed retirement credits, so waiting until 70 doesn't raise a living spouse's spousal benefit. The survivor benefit is different. When one spouse dies, the survivor steps into 100% of whatever the deceased was actually receiving, including every dollar of delayed credits. That's why the higher earner's claiming age matters so much for couples.</p>
    </section>

    <div class="ad-slot" data-ad-slot="in-content"><!-- AdSense code goes here when approved --></div>

    <h2>Spousal benefits: the basics</h2>
    <ul>
      <li><strong>Up to 50%</strong> of your spouse's full benefit (their PIA), if you claim at your own full retirement age.</li>
      <li><strong>You must be at least 62</strong>, married for at least one year, and your spouse must already be collecting their own benefit.</li>
      <li><strong>Social Security pays the higher of the two:</strong> your own earned benefit, or the spousal benefit. You do not get both added together.</li>
      <li><strong>Claiming early cuts it.</strong> At 62, the spousal benefit drops to as little as 32.5% of your spouse's full benefit.</li>
      <li><strong>No delayed credits.</strong> Waiting past your full retirement age does not raise a spousal benefit. It tops out at 50%.</li>
      <li><strong>It costs your spouse nothing.</strong> Your spousal benefit does not reduce their check by a dollar.</li>
    </ul>
    <p>Example: your spouse's full benefit is $2,400 a month. At your full retirement age you could receive up to $1,200 a month as a spousal benefit — if that is more than your own earned benefit.</p>

    <h2>Divorced? You may still qualify</h2>
    <p>If your marriage lasted at least 10 years, you are at least 62, you are currently unmarried, and your ex-spouse is at least 62 and has enough work credits, you can claim a spousal benefit on their record — up to 50% of their full benefit. It does not reduce what they or their current spouse receive.</p>

    <h2>Survivor benefits: the basics</h2>
    <ul>
      <li><strong>Up to 100%</strong> of what the deceased worker was receiving (or was entitled to receive), if you claim at your full retirement age for survivors.</li>
      <li><strong>You can claim as early as 60</strong> (50 if disabled), at a reduced rate — about 71.5% at 60.</li>
      <li><strong>Delayed credits count.</strong> If the deceased waited until 70, the survivor inherits the full boosted amount, including all delayed retirement credits. This is the biggest reason for a higher earner in a couple to wait.</li>
      <li><strong>Caring for a young child:</strong> a surviving spouse caring for the worker's child under 16 gets 75%, whatever their own age.</li>
      <li><strong>Marriage length:</strong> generally at least nine months before the death (10 years for a divorced survivor).</li>
      <li><strong>Remarriage:</strong> remarrying before 60 usually ends survivor benefits on the deceased spouse's record; remarrying at 60 or later does not.</li>
    </ul>

    <h2>Why couples should decide together</h2>
    <p>For a couple, the claiming decision is really two decisions: the lower earner can often claim earlier, while the higher earner waiting until 70 buys the largest possible survivor benefit — a check the surviving spouse may live on for many years. Run both numbers on the <a href="index.html">calculator</a> and compare the <a href="break-even.html">break-even ages</a> together.</p>

    <p class="note">Spousal and survivor rules have many exceptions — government pensions, caring for children, and remarriage all change the answer. Confirm your situation with the Social Security Administration at ssa.gov or by calling 1-800-772-1213.</p>
"""
page("spousal-survivor.html",
     "Social Security Spousal Benefits & Survivor Benefits Explained",
     "Social security spousal benefits pay up to 50% of your spouse's full benefit; survivors get up to 100%. Rules and examples.",
     BODY_SP)

# ------------------------------------------------- tax
BODY_TAX = """
    <section class="page-hero">
      <p class="eyebrow">Taxes &middot; Federal tax on benefits</p>
      <h1>Is Social Security Taxable?</h1>
      <p class="lede">Yes, it can be. Whether you owe tax depends on your combined income: your adjusted gross income, plus half your Social Security, plus any tax-free interest. For single filers, if combined income is under $25,000 ($32,000 for couples), none of it is taxed. Between $25,000 and $34,000 single ($32,000 to $44,000 joint), up to 50% can be taxed. Above that, up to 85% can be taxed. Nine states also tax benefits to some degree. Most people with only Social Security and little other income pay no tax on it at all.</p>
    </section>

    <div class="ad-slot" data-ad-slot="in-content"><!-- AdSense code goes here when approved --></div>

    <h2>What is "combined income"?</h2>
    <p>The IRS adds three things: your adjusted gross income (everything except Social Security), plus half of your Social Security benefits, plus any tax-free interest (for example, from municipal bonds). That total is your combined income. It is the only number that decides whether your benefits are taxed.</p>

    <h2>The thresholds</h2>
    <div class="table-scroll">
    <table>
      <thead><tr><th>Filing status</th><th class="num">No tax below</th><th class="num">Up to 50% taxable</th><th class="num">Up to 85% taxable</th></tr></thead>
      <tbody>
        <tr><td>Single, head of household, or qualifying surviving spouse</td><td class="num">$25,000</td><td class="num">$25,000&ndash;$34,000</td><td class="num">Above $34,000</td></tr>
        <tr><td>Married filing jointly</td><td class="num">$32,000</td><td class="num">$32,000&ndash;$44,000</td><td class="num">Above $44,000</td></tr>
        <tr><td>Married filing separately (lived together)</td><td class="num">$0</td><td class="num" colspan="2">Up to 85% can be taxable from the first dollar</td></tr>
      </tbody>
    </table>
    </div>
    <p>These thresholds have never been adjusted for inflation — they are the same numbers Congress set in 1983 and 1993. As benefits rise with cost-of-living adjustments, more people cross them each year.</p>

    <h2>An example</h2>
    <p>A single retiree gets $24,000 a year from Social Security and has $10,000 of other income. Combined income is $10,000 + $12,000 (half the benefit) = $22,000 — under $25,000, so none of the benefit is taxed. Give that same person $20,000 of other income instead, and combined income is $32,000 — between $25,000 and $34,000, so up to 50% of the benefit can be taxed, worked out on the IRS worksheet (Publication 915).</p>

    <h2>"Up to 85% taxable" is not an 85% tax rate</h2>
    <p>It means up to 85% of your benefit is added to your taxable income, and then taxed at your normal income tax rate. At most 85% of your benefit can ever be counted — at least 15% is always tax-free federally.</p>

    <h2>State taxes</h2>
    <p>Nine states tax Social Security benefits to some degree. The rest do not tax them at all. State rules change often and many states exempt lower incomes, so check your own state's rules before you count on the federal answer alone.</p>

    <h2>Can you have tax withheld?</h2>
    <p>Yes. You can ask Social Security to withhold federal tax from your check at 7%, 10%, 12%, or 22% by filing Form W-4V. It is a simple way to avoid a surprise bill at tax time. Your SSA-1099, which arrives each January, shows how much you received and is what you use on your tax return.</p>

    <p class="note">This page is general information, not tax advice. The exact taxable amount comes from the IRS worksheet in Publication 915. If your income is near a threshold, a tax preparer can usually save you more than they cost.</p>
"""
page("tax-on-benefits.html",
     "Is Social Security Taxable? Federal Thresholds Explained",
     "Is Social Security taxable? It depends on combined income: under $25,000 single or $32,000 joint, none is taxed; above that, up to 50% or 85%.",
     BODY_TAX)

# ------------------------------------------------- COLA
BODY_COLA = """
    <section class="page-hero">
      <p class="eyebrow">Cost-of-living adjustments &middot; Your check keeps up with prices</p>
      <h1>Social Security COLA: How Cost-of-Living Adjustments Work</h1>
      <p class="lede">Every year, Social Security raises benefits to keep up with inflation. The increase is called a cost-of-living adjustment, or COLA. It is automatic — Congress does not vote on it — and it is based on a price index called the CPI-W, which tracks what urban wage earners actually buy. The COLA for 2026 is 2.8%, and for 2027 it is 3.6%. Once your benefit starts, every COLA raises it for life, so the adjustments compound year after year.</p>
    </section>

    <div class="ad-slot" data-ad-slot="in-content"><!-- AdSense code goes here when approved --></div>

    <h2>How the COLA is set</h2>
    <p>Each October, the Social Security Administration compares the average CPI-W for July through September with the same three months a year earlier. If prices rose, benefits rise by the same percentage starting with December benefits, paid in January. If prices did not rise, there is no COLA that year — benefits never go down.</p>

    <h2>Recent COLAs</h2>
    <div class="table-scroll">
    <table>
      <thead><tr><th>Paid starting in January</th><th class="num">COLA</th><th>What happened</th></tr></thead>
      <tbody>
        <tr><td>2027</td><td class="num">3.6%</td><td>Announced October 14, 2026; average benefit rises about $75 a month.</td></tr>
        <tr><td>2026</td><td class="num">2.8%</td><td>Average benefit rose about $56 a month, from $2,015 to $2,071.</td></tr>
        <tr><td>2025</td><td class="num">2.5%</td><td>A quiet year for inflation.</td></tr>
        <tr><td>2024</td><td class="num">3.2%</td><td>Inflation cooling after the 2022 spike.</td></tr>
        <tr><td>2023</td><td class="num">8.7%</td><td>The largest since 1981, after the post-pandemic inflation surge.</td></tr>
        <tr><td>2022</td><td class="num">5.9%</td><td>Inflation taking off.</td></tr>
        <tr><td>2021</td><td class="num">1.3%</td><td>Pandemic-year prices barely moved.</td></tr>
      </tbody>
    </table>
    </div>

    <h2>What the COLA does — and does not — do</h2>
    <ul>
      <li><strong>It protects your buying power.</strong> A $2,000 check in 2026 becomes $2,056 after a 2.8% COLA, and the next year's COLA applies to the new, larger amount.</li>
      <li><strong>It applies whether or not you have claimed yet.</strong> Your benefit amount grows with COLAs from age 62 onward, even if you wait until 70 to claim.</li>
      <li><strong>It does not track your costs exactly.</strong> The CPI-W is based on working people's spending, not retirees'. Health care, which retirees buy more of, has often risen faster — which is why many retirees feel the COLA falls short.</li>
      <li><strong>Medicare premiums can eat it.</strong> The standard Part B premium is usually deducted from your check, and when it rises, it takes a bite out of the COLA. A "hold harmless" rule limits how much of the increase most people can lose in a year.</li>
    </ul>

    <p class="note">The calculator on this site gives estimates in today's dollars — it does not add future COLAs, because nobody knows what they will be. Your real check will be higher than the estimate if you claim years from now, because COLAs will have raised it in the meantime. Figures verified November 2026.</p>
"""
page("cola.html",
     "Social Security COLA Explained — 2026 Is 2.8%, 2027 Is 3.6%",
     "The Social Security COLA raises benefits with inflation: 2.8% in 2026, 3.6% in 2027. How it is set and what it means for your check.",
     BODY_COLA)

# ------------------------------------------------- where to retire
BODY_RETIRE = """
    <section class="page-hero">
      <p class="eyebrow">Where to retire &middot; Making your check go further</p>
      <h1>Best Places to Retire in the US — and the Cheapest Countries to Retire Abroad</h1>
      <p class="lede">Once you know your monthly Social Security check, the next question is where it goes furthest. The best places to retire in the US are not the famous Florida beach towns this year — they are small, affordable cities where the average benefit of about $2,071 a month covers the rent with room to spare. And if you want your dollars to stretch further still, the cheapest countries to retire abroad offer a comfortable life for $1,000 to $2,500 a month. Both lists below come from published 2026 rankings, and the source of every figure is named on this page.</p>
    </section>

    <div class="ad-slot" data-ad-slot="in-content"><!-- AdSense code goes here when approved --></div>

    <h2>Top 5 retirement destinations in the US</h2>
    <p>From U.S. News &amp; World Report's 2026 Best Places to Retire, which ranked more than 850 cities on quality of life, affordability, health care, retiree taxes, job market, and senior migration. The cost-of-living index is 100 for the US average — lower means cheaper. Home values and rents are from Homes.com's write-up of the same ranking.</p>
    <div class="table-scroll">
    <table>
      <thead><tr><th>#</th><th>Place</th><th class="num">Cost of living</th><th class="num">Median rent</th><th class="num">Median home value</th><th>Why it ranks</th></tr></thead>
      <tbody>
        <tr><td>1</td><td><strong>Midland, Michigan</strong></td><td class="num">85.7</td><td class="num">$790/mo</td><td class="num">$265,000</td><td>Small Midwest city, low crime, 80-plus parks. Michigan does not tax Social Security, and from the 2026 tax year its pension-tax phase-out is complete, so retirement income is deductible up to about $67,610 single or $135,220 joint.</td></tr>
        <tr><td>2</td><td><strong>Weirton, West Virginia</strong></td><td class="num">75.8</td><td class="num">$548/mo</td><td class="num">$150,000</td><td>The lowest cost of living on the list. A former steel town on the Ohio River, strong on affordability and retiree taxes.</td></tr>
        <tr><td>3</td><td><strong>Homosassa Springs, Florida</strong></td><td class="num">87.8</td><td class="num">$864/mo</td><td class="num">$330,000</td><td>Gulf Coast fishing-village feel about an hour north of Tampa, inland enough to be safer from hurricanes than coastal towns. Florida has no state income tax.</td></tr>
        <tr><td>4</td><td><strong>The Woodlands, Texas</strong></td><td class="num">100.1</td><td class="num">$1,440/mo</td><td class="num">$575,000</td><td>Master-planned community 30 minutes from Houston, with 55-plus communities and 200-plus miles of trails. The priciest on this list, but Texas has no state income tax.</td></tr>
        <tr><td>5</td><td><strong>Spring, Texas</strong></td><td class="num">96.9</td><td class="num">$1,328/mo</td><td class="num">$391,000</td><td>Houston-area suburb with a historic Old Town, just north of The Woodlands and a little cheaper. More than 68,000 residents, about 11% of them seniors. Texas has no state income tax.</td></tr>
      </tbody>
    </table>
    </div>
    <p>What the numbers mean in practice: the average Social Security benefit of $2,071 a month covers the median rent in Midland, Weirton, and Homosassa Springs with money left over, and roughly covers it in Spring. In The Woodlands it does not. Run your own benefit on the <a href="index.html">Social Security calculator</a> and compare it with the rent where you want to live.</p>

    <h2>5 cheapest places for Americans to retire abroad</h2>
    <p>From International Living's Cheapest Places to Live in the World 2026, which scored destinations on cost of living in its 2026 Global Retirement Index. The figures are monthly budgets for a couple, as reported by expats living there — not prices from a database, so treat them as a guide, not a quote.</p>
    <div class="table-scroll">
    <table>
      <thead><tr><th>#</th><th>Place</th><th class="num">Monthly budget</th><th>What you get</th></tr></thead>
      <tbody>
        <tr><td>1</td><td><strong>Sri Lanka</strong></td><td class="num">About $1,000</td><td>A modest lifestyle for about $1,000 a month; a couple can live extravagantly on $2,200. Cheap local transport and retirement visas that are easy to get.</td></tr>
        <tr><td>2</td><td><strong>Bali, Indonesia</strong></td><td class="num">About $1,400</td><td>A couple can live well for about $1,400 a month; a villa near the beach rents for under $900. Good health care, cheap and excellent food.</td></tr>
        <tr><td>3</td><td><strong>Hanoi, Vietnam</strong></td><td class="num">Under $1,800</td><td>Low rent, fresh street food, and affordable health care in a historic capital with as many as 100,000 expats.</td></tr>
        <tr><td>4</td><td><strong>Thailand</strong></td><td class="num">$1,700&ndash;$2,500</td><td>Chiang Mai about $1,700 a month, Phuket about $2,500. Warm weather, good hospitals, and a long-established expat scene.</td></tr>
        <tr><td>5</td><td><strong>Penang, Malaysia</strong></td><td class="num">About $2,500</td><td>A comfortable life for about $2,500 a month, with affordable modern apartments, low utility costs, and reliable, inexpensive public transport and health care.</td></tr>
      </tbody>
    </table>
    </div>
    <p>For scale: the average Social Security benefit of $2,071 a month covers the Sri Lanka, Bali, and Hanoi budgets outright, and covers most of the Thailand and Penang budgets. A couple with two benefits has far more room. But budgets are only half the story — visas, health care, and distance from family matter just as much.</p>

    <h2>Getting paid abroad, and health care</h2>
    <p>Social Security can usually still be paid to you abroad. The Social Security Administration has a Payments Abroad Screening Tool to check whether your country is covered — most are, with a few exceptions. But Medicare generally does not cover care outside the US, so you would need local health insurance or pay out of pocket. The standard Part B premium was $202.90 a month in 2026 and still applies if you keep your Medicare coverage while living abroad.</p>

    <p class="note">Sources: U.S. News &amp; World Report, 2026 Best Places to Retire (250 Best Places to Retire in the U.S. in 2026), with home values and rents as reported by Homes.com; International Living, Cheapest Places to Live in the World 2026 (2026 Global Retirement Index), as reported by GoBankingRates and others. Figures are from 2026 and change — check current prices before you move. This page is education, not financial advice.</p>
"""
page("where-to-retire.html",
     "Best Places to Retire in the US & Cheapest Countries to Retire Abroad",
     "Best places to retire in the US in 2026 and the cheapest countries to retire abroad, with monthly budgets and the sources behind every figure.",
     BODY_RETIRE)

# ------------------------------------------------- about
BODY_ABOUT = """
    <h1>About this site</h1>
    <p>This site answers one question: <strong>how much Social Security will I get?</strong></p>
    <p>Social Security is the biggest source of retirement income for most Americans, and the rules around it — full retirement age, bend points, delayed retirement credits, break-even ages — are usually explained in government language. This site explains them the way you would explain them to a friend, and it does the math for you.</p>
    <p>The calculator uses the same formula Social Security uses: your 35 highest-earning years, averaged into a monthly figure, run through the 90/32/15% bend-point formula, then adjusted for the age you claim. It shows your benefit at every age from 62 to 70, your break-even ages, and your lifetime totals at the life expectancy you enter.</p>
    <p>The site is run by Cory Lewis. It is educational only — it is not financial advice, and it is not the Social Security Administration. Before you make a claiming decision, confirm the numbers on your own statement at ssa.gov/myaccount.</p>
    <p>Everything on this site runs in your browser. There is no account to create and no sign-up. The numbers you type into the calculator are never sent anywhere.</p>
    <p>Figures on this site were verified in November 2026. Benefit rules, bend points and tax thresholds change, so the numbers are checked and updated when they do.</p>
    <p><a href="index.html">Back to the calculator</a></p>
"""
page("about.html",
     "About — Social Security Calculator",
     "About this site: a free Social Security calculator that estimates your benefit at every claiming age from 62 to 70.",
     BODY_ABOUT)

# ------------------------------------------------- privacy
BODY_PRIVACY = """
    <h1>Privacy policy</h1>
    <p><strong>Last updated: November 2026.</strong></p>

    <h2>What this site collects</h2>
    <p>Nothing. The calculator runs entirely in your web browser. The earnings, birth year, and other numbers you type in are used on your own device to work out the answer, and are never sent to us or to anyone else. This site has no accounts, no sign-up, and no way to identify you.</p>

    <h2>Cookies and advertising</h2>
    <p>This site currently uses no cookies and shows no ads. In future, advertising may be shown through Google AdSense, which uses cookies to show ads that are relevant to you. Google's use of advertising cookies lets it and its partners show ads based on your visits to this site and other sites. You can opt out of personalized advertising at any time by visiting Google's Ads Settings page. This policy will be updated if and when advertising is added.</p>

    <h2>Analytics</h2>
    <p>This site currently uses no analytics. If anonymous visitor statistics are added later, they will count visits only and will not identify individual visitors.</p>

    <h2>Links to other sites</h2>
    <p>This site links to ssa.gov, the Social Security Administration's website, so you can check your own statement. That link is the only link to another website on this site.</p>

    <h2>Contact</h2>
    <p>If you email us, we will use your email address only to reply to you. We do not sell, share or rent personal information to anyone, and we do not send marketing emails.</p>

    <h2>Changes to this policy</h2>
    <p>If this policy changes, the new version will be posted on this page with a new "last updated" date.</p>

    <p><a href="index.html">Back to the calculator</a></p>
"""
page("privacy.html",
     "Privacy Policy — Social Security Calculator",
     "Privacy policy: this Social Security calculator runs entirely in your browser and collects no personal information.",
     BODY_PRIVACY)

# ------------------------------------------------- contact
BODY_CONTACT = """
    <h1>Contact</h1>
    <p>Questions about the calculator, a number that looks wrong, or a page you would like added? Get in touch.</p>
    <p><strong>Email:</strong> <a href="mailto:retirementtoday1@hotmail.com">retirementtoday1@hotmail.com</a></p>
    <p>Please note this site cannot give personal financial advice. For advice about your own Social Security decision, talk to the Social Security Administration at ssa.gov or call 1-800-772-1213.</p>
    <p><a href="index.html">Back to the calculator</a></p>
"""
page("contact.html",
     "Contact — Social Security Calculator",
     "Contact the people behind this Social Security calculator with questions or corrections.",
     BODY_CONTACT)

print("done")
