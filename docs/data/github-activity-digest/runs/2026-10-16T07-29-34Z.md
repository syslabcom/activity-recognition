# 📊 WEEKLY SUMMARY  
2026-10-09 to 2026-10-16

This week in the Plone organization saw noteworthy progress across multiple repositories, with contributions focusing on dependency updates, feature enhancements, and bug fixes that improve overall system stability and functionality. 

## 📦 plone/plone.event  
[1 file changed, +3/-3 lines, 1 pull request merged]  
The repository received an update from the pre-commit CI bot, involving an autoupdate for pre-commit hooks, which included updates to `isort`, `black-pre-commit`, and `flake8`.

## 📦 plone/plone.formwidget.recurrence  
[1 file changed, +3/-3 lines, 1 pull request merged]  
Similar to the previous repository, this one also received an autoupdate for pre-commit hooks, ensuring cleaner and more efficient coding practices.

## 📦 plone/plone.app.event  
[3 files changed, +5/-5 lines, 2 pull requests merged]  
Enhancements included a bump of dependencies managed by Dependabot, which updated `astral-sh/setup-uv` from 10.2.0 to 10.3.0 adding Python architecture selection. Pre-commit CI also updated formatting tools.

## 📦 plone/plone.app.multilingual  
[28 files changed, +70/-58 lines, 1 pull request merged]  
Key changes included the removal of `plone.restapi` and `plone.rest` as hard dependencies, streamlining the multilingual setup. Configuration improvements with plone.meta were also applied.

## 📦 plone/plone.resource  
[1 file changed, +3/-3 lines, 1 pull request merged]  
This repository received an autoupdate for pre-commit hooks to keep development practices current with the latest tools.

## 📦 plone/plone.app.querystring  
[38 files changed, +980/-13 lines, 4 pull requests merged]  
Significant functionality was added, including support for currentUID operations, path sorting, and improvements for virtual hosting paths. Dependency managed updates were also pushed through pre-commit CI.

## 📦 plone/plone.app.standardtiles  
[1 file changed, +3/-3 lines, 1 pull request merged]  
Included an autoupdate for pre-commit hooks to ensure proper coding standards are met.

## 📦 plone/plone.dexterity  
[1 file changed, +3/-3 lines, 1 pull request merged]  
Updated by pre-commit CI to keep the repository’s development environment modernized.

## 📦 plone/products.statusmessages  
[1 file changed, +3/-3 lines, 1 pull request merged]  
Received a similar update regarding pre-commit hooks, enhancing code quality.

## 📦 plone/plone.app.relationfield  
[3 files changed, +5/-5 lines, 2 pull requests merged]  
Updates included handling for dependency bumps and formatting tools via pre-commit CI.

## 📦 plone/buildout.coredev  
[32 files changed, +385/-391 lines, 1 pull request merged]  
A major revision was made to use maintenance branches for the content rules packages relevant for Plone 6.2, ensuring ongoing support for prior versions while preparing for the new major releases.

[Further repository updates follow in this format.]

In summary, many contributors made substantial updates to libraries and tools that support Plone's functionality, ensuring that the platform remains robust and efficient for users and developers alike. 

## Contributors
- pre-commit-ci[bot]  
- dependabot[bot]  
- Érico Andrei  
- Mikel Larreategi  
- David Glick  
- Peter Mathis  
- Gil Forcada Codinachs  
- Johannes Raggam  
- Tishasoumya-02  
- MrTango  
- others...

Automatically generated from 107 active repositories.
