/* Social Security Calculator (US) — calculator logic.
   Pure functions first (testable in Node), DOM wiring at the bottom.
   All figures in US dollars. Bend points and rules verified November 2026
   against SSA sources (ssa.gov/oact/cola/bendpoints.html,
   ssa.gov/oact/cola/piaformula.html, SSA retirement benefits guidance).
   Estimates are in today's dollars, using the 2026 bend points. */
(function () {
  'use strict';

  /* ---------- constants (2026) ---------- */

  var BEND1 = 1286;      // first bend point, workers first eligible in 2026
  var BEND2 = 7749;      // second bend point, workers first eligible in 2026
  var TAXABLE_MAX = 184500; // 2026 Social Security wage base
  var AVG_BENEFIT_2026 = 2071; // average retired-worker benefit, Jan 2026
  var MAX_AT_70_2026 = 5181;   // maximum monthly benefit at 70, 2026
  var MAX_AT_FRA_2026 = 4152;  // maximum monthly benefit at full retirement age, 2026

  /* ---------- helpers ---------- */

  function money(n) {
    return '$' + Math.round(n).toLocaleString('en-US');
  }

  function moneyExact(n) {
    return '$' + Math.round(n).toLocaleString('en-US');
  }

  /* ---------- full retirement age by birth year ---------- */
  /* SSA schedule: 65 for 1937 or earlier, rising 2 months per birth year
     to 66 for 1943-1954, then 2 months per year again to 67 for 1960+.
     Returns total months of age (e.g. 67 years = 804 months). */
  function fraMonthsByBirthYear(year) {
    var y = Math.floor(year);
    if (y <= 1937) return 65 * 12;
    if (y === 1938) return 65 * 12 + 2;
    if (y === 1939) return 65 * 12 + 4;
    if (y === 1940) return 65 * 12 + 6;
    if (y === 1941) return 65 * 12 + 8;
    if (y === 1942) return 65 * 12 + 10;
    if (y >= 1943 && y <= 1954) return 66 * 12;
    if (y === 1955) return 66 * 12 + 2;
    if (y === 1956) return 66 * 12 + 4;
    if (y === 1957) return 66 * 12 + 6;
    if (y === 1958) return 66 * 12 + 8;
    if (y === 1959) return 66 * 12 + 10;
    return 67 * 12; // 1960 or later
  }

  function fraText(year) {
    var m = fraMonthsByBirthYear(year);
    var years = Math.floor(m / 12);
    var months = m % 12;
    if (months === 0) return years + '';
    return years + ' years and ' + months + ' months';
  }

  /* ---------- PIA from AIME ---------- */
  /* PIA = 90% of the first $1,286 of AIME + 32% of AIME from $1,286 to
     $7,749 + 15% of AIME above $7,749 (2026 bend points).
     SSA rounds the PIA down to the next lower multiple of $0.10. */
  function piaFromAime(aime) {
    var pia = 0;
    pia += 0.90 * Math.min(aime, BEND1);
    if (aime > BEND1) pia += 0.32 * (Math.min(aime, BEND2) - BEND1);
    if (aime > BEND2) pia += 0.15 * (aime - BEND2);
    return Math.floor(pia * 10) / 10;
  }

  /* AIME from a steady annual earnings level: assumes a full 35-year
     career at that level, in today's dollars (the SSA Quick Calculator
     approach). Earnings above the taxable wage base do not count. */
  function aimeFromAnnualEarnings(annual) {
    var capped = Math.min(Math.max(annual, 0), TAXABLE_MAX);
    return capped / 12;
  }

  /* ---------- claiming-age adjustment ---------- */
  /* Early: 5/9 of 1% per month for the first 36 months before FRA,
     then 5/12 of 1% per month. Late: 2/3 of 1% per month (8% a year)
     past FRA, up to age 70. claimAgeYears is a whole age 62-70. */
  function factorAtClaimAge(claimAgeYears, fraMonths) {
    var claimMonths = claimAgeYears * 12;
    if (claimMonths < fraMonths) {
      var early = fraMonths - claimMonths;
      var reduction = (5 / 9) * Math.min(early, 36) + (5 / 12) * Math.max(early - 36, 0);
      return 1 - reduction / 100;
    }
    var late = claimMonths - fraMonths;
    return 1 + (2 / 3) * late / 100;
  }

  /* Monthly benefit at a claiming age. SSA rounds benefits down to the
     next lower whole dollar. */
  function benefitAtAge(pia, claimAgeYears, fraMonths) {
    return Math.floor(pia * factorAtClaimAge(claimAgeYears, fraMonths));
  }

  /* Monthly benefit at every claiming age from 62 to 70. */
  function benefitsByAge(pia, fraMonths) {
    var out = {};
    for (var age = 62; age <= 70; age++) {
      out[age] = benefitAtAge(pia, age, fraMonths);
    }
    return out;
  }

  /* ---------- break-even ---------- */
  /* Age at which total dollars collected by claiming later catch up with
     claiming earlier. earlyAge/lateAge are whole ages; monthly amounts
     are the monthly benefits at those ages. */
  function breakEvenAge(monthlyEarly, earlyAge, monthlyLate, lateAge) {
    if (monthlyLate <= monthlyEarly) return null;
    var gapMonths = (lateAge - earlyAge) * 12;
    var monthsAfterLate = (monthlyEarly * gapMonths) / (monthlyLate - monthlyEarly);
    return lateAge + monthsAfterLate / 12;
  }

  function formatBreakEven(age) {
    if (age === null) return '—';
    var years = Math.floor(age);
    var months = Math.round((age - years) * 12);
    if (months === 12) { years += 1; months = 0; }
    return 'about ' + years + (months > 0 ? ' years and ' + months + ' months' : '');
  }

  /* ---------- lifetime totals ---------- */
  function lifetimeTotal(monthly, claimAge, lifeExpectancy) {
    if (lifeExpectancy <= claimAge) return 0;
    return monthly * 12 * (lifeExpectancy - claimAge);
  }

  /* ---------- full calculation ---------- */
  /* opts: { mode: 'earnings' | 'statement', earnings, statementBenefit,
             birthYear, lifeExpectancy } */
  function calculate(opts) {
    var fraMonths = fraMonthsByBirthYear(opts.birthYear);
    var aime = null;
    var pia;
    if (opts.mode === 'statement') {
      pia = Math.max(opts.statementBenefit || 0, 0);
    } else {
      aime = aimeFromAnnualEarnings(opts.earnings || 0);
      pia = piaFromAime(aime);
    }
    var byAge = benefitsByAge(pia, fraMonths);
    var fraYears = fraMonths / 12;
    /* The benefit at full retirement age is the PIA itself, by definition
       (for birth years with a fractional FRA, e.g. 66 and 10 months, the
       whole-year table does not have an exact FRA row). */
    var beFraV62 = breakEvenAge(byAge[62], 62, pia, fraYears);
    var be70v62 = breakEvenAge(byAge[62], 62, byAge[70], 70);
    var be70vFra = breakEvenAge(pia, fraYears, byAge[70], 70);
    var life = {};
    for (var age = 62; age <= 70; age++) {
      life[age] = lifetimeTotal(byAge[age], age, opts.lifeExpectancy);
    }
    return {
      fraMonths: fraMonths,
      fraText: fraText(opts.birthYear),
      aime: aime,
      pia: pia,
      byAge: byAge,
      atFra: Math.floor(pia), // SSA rounds the monthly benefit down to the dollar
      breakEven67v62: beFraV62,
      breakEven70v62: be70v62,
      breakEven70vFra: be70vFra,
      lifetime: life
    };
  }

  /* Expose the pure functions for Node tests. */
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      money: money, moneyExact: moneyExact,
      BEND1: BEND1, BEND2: BEND2, TAXABLE_MAX: TAXABLE_MAX,
      AVG_BENEFIT_2026: AVG_BENEFIT_2026,
      MAX_AT_70_2026: MAX_AT_70_2026, MAX_AT_FRA_2026: MAX_AT_FRA_2026,
      fraMonthsByBirthYear: fraMonthsByBirthYear, fraText: fraText,
      piaFromAime: piaFromAime,
      aimeFromAnnualEarnings: aimeFromAnnualEarnings,
      factorAtClaimAge: factorAtClaimAge,
      benefitAtAge: benefitAtAge,
      benefitsByAge: benefitsByAge,
      breakEvenAge: breakEvenAge, formatBreakEven: formatBreakEven,
      lifetimeTotal: lifetimeTotal,
      calculate: calculate
    };
  }

  /* ---------- page wiring ---------- */

  if (typeof document === 'undefined') return;

  function num(id, fallback) {
    var el = document.getElementById(id);
    if (!el) return fallback;
    var v = parseFloat(String(el.value).replace(/[^0-9.]/g, ''));
    return isNaN(v) ? fallback : v;
  }

  function setText(id, text) {
    var el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  function show(id, on) {
    var el = document.getElementById(id);
    if (el) el.style.display = on ? '' : 'none';
  }

  function readInputs() {
    var modeEl = document.querySelector('input[name="mode"]:checked');
    return {
      mode: modeEl ? modeEl.value : 'earnings',
      earnings: num('earnings', 70000),
      statementBenefit: num('statement-benefit', 2000),
      birthYear: num('birth-year', 1964),
      lifeExpectancy: num('life-expectancy', 85)
    };
  }

  function updateMain() {
    var inp = readInputs();
    if (inp.birthYear < 1920) inp.birthYear = 1920;
    if (inp.birthYear > 2010) inp.birthYear = 2010;
    if (inp.lifeExpectancy < 63) inp.lifeExpectancy = 63;
    if (inp.lifeExpectancy > 100) inp.lifeExpectancy = 100;

    show('earnings-field', inp.mode === 'earnings');
    show('statement-field', inp.mode === 'statement');

    var r = calculate(inp);
    var fraAge = Math.round(r.fraMonths / 12);

    setText('out-fra', 'Your full retirement age is ' + r.fraText + '.');
    setText('out-pia', money(Math.floor(r.pia)) + ' / month');
    setText('out-aime', r.aime === null
      ? 'Taken straight from your statement — no earnings math needed.'
      : 'Average indexed monthly earnings: ' + money(r.aime) + ' (from 35 years at ' + money(inp.earnings) + ' a year).');
    setText('out-big', money(r.atFra) + ' / month');
    setText('out-big-sub', 'at full retirement age (' + r.fraText + ')');
    setText('sticky-big', money(r.atFra) + ' / mo');

    for (var age = 62; age <= 70; age++) {
      setText('out-age-' + age, money(r.byAge[age]) + ' / mo');
      setText('out-life-' + age, money(r.lifetime[age]));
    }
    setText('out-at62', money(r.byAge[62]) + ' / month');
    setText('out-at70', money(r.byAge[70]) + ' / month');
    setText('out-be-67-62', formatBreakEven(r.breakEven67v62));
    setText('out-be-70-62', formatBreakEven(r.breakEven70v62));
    setText('out-be-70-fra', formatBreakEven(r.breakEven70vFra));
    setText('out-life-62', money(r.lifetime[62]));
    setText('out-life-67', money(r.lifetime[67]));
    setText('out-life-70', money(r.lifetime[70]));
    setText('out-life-note', 'If you live to ' + inp.lifeExpectancy + '.');

    var note = document.getElementById('out-mode-note');
    if (note) {
      note.textContent = inp.mode === 'statement'
        ? 'Using the benefit from your statement as your full retirement age benefit.'
        : 'Estimated from 35 years at ' + money(inp.earnings) + ' a year, in today\'s dollars.';
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    var inputs = document.querySelectorAll('#calculator input');
    inputs.forEach(function (el) {
      el.addEventListener('input', updateMain);
      el.addEventListener('change', updateMain);
    });
    if (document.getElementById('calculator')) updateMain();

    var exampleBtn = document.getElementById('load-example');
    if (exampleBtn) {
      exampleBtn.addEventListener('click', function () {
        var set = function (id, v) { var el = document.getElementById(id); if (el) el.value = v; };
        var earn = document.getElementById('mode-earnings');
        if (earn) earn.checked = true;
        set('earnings', 70000);
        set('birth-year', 1964);
        set('life-expectancy', 85);
        updateMain();
        document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      });
    }
  });
})();
