# Dev Environment Checker

A small, dependency-free Python CLI that audits a developer workstation against a version-controlled JSON policy. It answers a practical question before setup or CI work begins: **are the required tools, versions, and environment-variable names available?**

## Why it exists
Onboarding instructions drift. Different machines silently use different Git, Python, or Node versions. Dev Environment Checker makes those expectations executable without installing a large environment manager.

## Features
- Detects executables using the system `PATH`.
- Queries and parses tool versions without shell execution.
- Supports `>=`, `<=`, `>`, `<`, `==` and comma-separated constraints.
- Checks required environment-variable **presence without exposing values**.
- Human-readable and JSON reports; exit `0` when ready, `1` on failed checks, `2` on invalid policy/runtime input.
- Cross-platform Python API and CLI; no runtime dependencies, network access, telemetry, or credentials.

## Preview
```text
Development environment: READY
[OK      ] Python: 3.12.7 (required >=3.10,<4)
[OK      ] Git: 2.46.0 (required >=2.30)
```
This is terminal output, so screenshots are optional; a screenshot should show the same CLI rather than imply a GUI.

## Requirements & installation
Python 3.10+.
```bash
git clone https://github.com/rad03i2/dev-environment-checker.git
cd dev-environment-checker
python -m pip install -e .
```

## Usage
Copy `examples/dev-environment.json` to `dev-environment.json`, adjust it, then:
```bash
dev-env-check
dev-env-check path/to/policy.json
dev-env-check path/to/policy.json --json
python -m dev_environment_checker path/to/policy.json
```
Policy format:
```json
{"tools":[{"name":"Python","command":"python","version_args":["--version"],"version":">=3.10,<4"}],"environment":["CI"]}
```
`version_args` defaults to `["--version"]`. Environment values are never included in reports.

## Python API
```python
from dev_environment_checker import audit, load_policy
report = audit(load_policy("dev-environment.json"))
print(report["healthy"])
```

## Project structure
`src/dev_environment_checker/` contains the audit engine and CLI; `tests/` contains functional tests; `examples/` contains a safe sample policy; `.github/workflows/ci.yml` runs the test matrix.

## Testing
```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
```
CI runs Python 3.10, 3.12 and 3.13 on Linux, Windows and macOS.

## Security & privacy
Commands are invoked as argument arrays with `shell=False`; the checker never evaluates project code. It only invokes version commands explicitly listed in a policy. **Review untrusted policy files before running them**, because a policy controls which local executable is invoked. Environment values are deliberately hidden. No network requests are made by the application.

## Limitations
Version parsing intentionally targets conventional numeric versions. It is not a full SemVer/PEP 440 solver, does not install or repair tools, does not validate SDK-specific configuration, and does not infer project requirements automatically. A tool with unusual version output may require different `version_args` or may not be parseable.

## Optional roadmap
Potential future additions include policy presets, richer version grammars, and opt-in project-file discovery. These are not claimed as current features.

## Contributing
See `CONTRIBUTING.md`. Please include tests for behavioral changes and keep checks deterministic and local.

## License
MIT — see `LICENSE`.

## Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

# مدقق بيئة التطوير — العربية

أداة Python صغيرة بلا اعتماديات تشغيلية لفحص جهاز المطور مقابل سياسة JSON محفوظة مع المشروع. هدفها التأكد من توفر الأدوات المطلوبة وإصداراتها وأسماء متغيرات البيئة قبل بدء العمل أو CI.

## لماذا المشروع؟
تعليمات إعداد المشاريع قد تصبح قديمة، وقد يعمل أعضاء الفريق بإصدارات مختلفة دون ملاحظة. يحول المشروع متطلبات البيئة إلى فحص قابل للتكرار بدل الاعتماد على خطوات يدوية فقط.

## المزايا
- اكتشاف البرامج عبر `PATH` وفحص أرقام إصداراتها.
- دعم `>=` و`<=` و`>` و`<` و`==` والقيود المتعددة.
- التحقق من وجود متغيرات البيئة **من دون كشف قيمها**.
- إخراج نصي أو JSON ورموز خروج مناسبة للأتمتة.
- CLI وPython API، بلا اتصال شبكة أو telemetry أو أسرار.

## التثبيت والمتطلبات
يتطلب Python 3.10 أو أحدث:
```bash
git clone https://github.com/rad03i2/dev-environment-checker.git
cd dev-environment-checker
python -m pip install -e .
```

## الاستخدام والإعداد
انسخ `examples/dev-environment.json` وعدّل قائمة الأدوات والقيود، ثم شغّل:
```bash
dev-env-check dev-environment.json
dev-env-check dev-environment.json --json
```
يمكن كذلك استدعاء `audit` و`load_policy` من Python كما في القسم الإنجليزي. `version_args` اختيارية وقيمتها الافتراضية `--version`.

## بنية المشروع والاختبارات
الكود في `src/dev_environment_checker/`، والاختبارات في `tests/`، والمثال في `examples/`، وCI في `.github/workflows/ci.yml`.
```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

## الأمان والخصوصية
لا تستخدم الأداة shell ولا تشغّل كود المشروع، ولا ترسل بيانات للشبكة. لكنها تشغّل أمر الإصدار المحدد في ملف السياسة، لذلك يجب مراجعة أي سياسة غير موثوقة قبل تشغيلها. قيم متغيرات البيئة لا تظهر في التقرير.

## القيود
ليست الأداة مدير حزم أو مثبت أدوات، ولا تنفذ SemVer أو PEP 440 كاملين، ولا تستنتج المتطلبات تلقائيًا. بعض البرامج ذات مخرجات الإصدار غير التقليدية قد لا يمكن تحليلها.

## تطوير اختياري
يمكن مستقبلًا إضافة قوالب سياسات وقواعد إصدارات أوسع واكتشاف اختياري لملفات المشاريع؛ هذه ليست ميزات حالية.

## المساهمة والترخيص
راجع `CONTRIBUTING.md`. المشروع مرخص MIT، والتفاصيل في `LICENSE`.

## المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
