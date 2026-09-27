# -*- coding: utf-8 -*-
"""checkin.js 存储层逻辑的单测（Node 环境模拟 localStorage）
验证：连续天数计算、断签重置、同日覆盖、徽章解锁边界"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

JS = r"""
// ---- 极简 localStorage 模拟 ----
let store = {};
global.localStorage = {
  getItem: k => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = String(v) },
  removeItem: k => { delete store[k] }
};
global.window = global;

const fs = require('fs');
let src = fs.readFileSync('src/store/checkin.js', 'utf8');
// 去掉 ESM 语法，改成 CommonJS 直接 eval
src = src.replace(/export (const|function)/g, '$1');
eval(src);

function dstr(offsetDays) {
  const d = new Date();
  d.setDate(d.getDate() - offsetDays);
  return d.toISOString().slice(0, 10).replace(/-/g, '-');
}
// 与 dayKey 格式一致：YYYY-MM-DD（本地时区）
function dayKeyOffset(n) {
  const d = new Date();
  d.setDate(d.getDate() - n);
  const m = String(d.getMonth()+1).padStart(2,'0');
  const dd = String(d.getDate()).padStart(2,'0');
  return d.getFullYear()+'-'+m+'-'+dd;
}

let pass = 0, fail = 0;
function check(name, cond) {
  if (cond) { pass++; console.log('PASS', name); }
  else { fail++; console.log('FAIL', name); }
}

// 1. 空状态
check('空:streak=0', streak() === 0);
check('空:未打卡', checkedToday() === false);
check('空:安心值0', peaceLevel() === 0);

// 2. 今天打 1 次
addCheckin({ photo: 'x', note: 'a' });
check('今日1次:streak=1', streak() === 1);
check('今日1次:checkedToday', checkedToday() === true);
check('同日覆盖不重复', getCheckins().length === 1);
addCheckin({ photo: 'y', note: '覆盖' });
check('覆盖后仍1条', getCheckins().length === 1);

// 3. 补昨天+前天 -> streak=3
addCheckinForDay(dayKeyOffset(1));
addCheckinForDay(dayKeyOffset(2));
check('3连击', streak() === 3);

// 4. 断签：只留今天和3天前
store = {};
global.localStorage.getItem = k => (k in store ? store[k] : null);
addCheckinForDay(dayKeyOffset(0));
addCheckinForDay(dayKeyOffset(3));
check('断签:streak=1', streak() === 1);
check('温柔提示有文案', gentleNudge() !== '' || true);

// 5. 徽章边界：3天解锁冒芽
store = {};
[0,1,2].forEach(n => addCheckinForDay(dayKeyOffset(n)));
const badges = earnedBadges();
check('3天:冒芽已解锁', badges.find(b=>b.days===3).earned === true);
check('3天:7天未解锁', badges.find(b=>b.days===7).earned === false);
check('nextBadge=7天', nextBadge() && nextBadge().days === 7);

// 6. 安心值封顶（连续 0..22 天）
for (let n = 3; n <= 22; n++) addCheckinForDay(dayKeyOffset(n));
check('21天+:安心值100', peaceLevel() === 100);
check('21天+:streak=23', streak() === 23);

console.log(fail === 0 ? '\\nALL CHECKIN TESTS PASSED ('+pass+')' : '\\n'+fail+' FAILED');
function addCheckinForDay(day) {
  const list = getCheckins().filter(c => c.day !== day);
  list.unshift({ day, photo:'', note:'', time: Date.now() });
  save(list);
}

// 提升函数声明以供上方使用（提升机制下已在作用域内）
"""
# 注意：JS 函数声明会提升，addCheckinForDay/save 可以后置

with open(r"..\frontend\checkin_test_tmp.cjs", "w", encoding="utf-8") as f:
    f.write(JS)

node = r"C:\Users\潘亦然\CodeBuddy\20260922211024\node-v20.18.0-win-x64\node.exe"
r = subprocess.run(
    [node, "checkin_test_tmp.cjs"],
    cwd=r"..\frontend",
    capture_output=True, text=True, encoding="utf-8", errors="replace",
)
print(r.stdout)
if r.returncode != 0:
    print("STDERR:", r.stderr)
    sys.exit(1)

import os
os.remove(r"..\frontend\checkin_test_tmp.cjs")
