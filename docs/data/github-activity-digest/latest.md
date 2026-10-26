📊 WEEKLY SUMMARY  
2026-10-19 to 2026-10-26  

This week in the Plone organization saw significant enhancements and transitions across various repositories, particularly related to infrastructure improvements and ongoing updates for upcoming releases. Several contributors actively improved code quality, merged multiple pull requests, and prepared new release versions, ensuring a robust ecosystem moving forward.

📦 plone/plone.event  
[4 files changed, +41/-1 lines, 1 pull request merged]  
Contributor @syahra712 enhanced the `re.sub` function to correctly use `re.MULTILINE` as a flag instead of a count, addressing a deprecation warning in Python 3.13+. Additional test cases were added to ensure `DTSTART` lines are appropriately removed from the recurrence rules.

📦 plone/plone.subrequest  
[1 file changed, +1/-1 lines, 1 pull request merged]  
@dependabot[bot] updated the `astral-sh/setup-uv` dependency from version 10.2.0 to 10.3.0, which includes a Python architecture selection feature.

📦 plone/plone.portlets  
[161 files changed, +17966/-416 lines, 7 pull requests merged]  
This repository underwent significant changes, including the merging of previous portlet repositories (`plone.app.portlets`, `plone.portlet.collection`, and `plone.portlet.static`) into one. Contributor @gforcada played a major role in implementing these transitions along with @jensens, @mauritsvanrees, and others. Various enhancements were made, including the removal of unnecessary files and configuration updates for `plone.meta`.

📦 plone/plone.app.content  
[6 files changed, +13/-7 lines, 0 pull requests merged]  
Contributors @davisagli and @mauritsvanrees implemented permission checks to improve group and principal vocabulary access.

📦 plone/plone.protect  
[1 file changed, +1/-1 lines, 1 pull request merged]  
A dependency update was made to bump `astral-sh/setup-uv` to version 10.3.0 by @dependabot[bot].

📦 plone/plone.portlet.collection  
[35 files changed, +68/-1982 lines, 1 pull request merged]  
The repository transitioned into an empty package as part of `PLIP 4137`, with @jensens leading the changes, moving its source code to the consolidated `plone.portlets` distribution.

📦 plone/plone.portlet.static  
[29 files changed, +66/-1204 lines, 1 pull request merged]  
Similar to the previous repository, `plone.portlet.static` now exists as an empty transitional package following the progressive consolidation efforts under `PLIP 4137`, spearheaded by @jensens.

📦 plone/plone.app.portlets  
[129 files changed, +68/-13497 lines, 1 pull request merged]  
The repository has also turned into an empty transitional package as part of the merging strategy under `PLIP 4137`, which involves significant restructuring of portlet capabilities.

📦 plone/buildout.coredev  
[37 files changed, +180/-261 lines, 5 pull requests merged]  
Updates were made to dependencies and configurations for building images, including support for the Pillow library and various packages needed for Plone 6.1 and 6.3, led by contributors such as @davisagli and @mauritsvanrees.

📦 plone/training  
[28 files changed, +1175/-21 lines, 2 pull requests merged]  
@petschki introduced new training documentation, including blicca customization training, alongside @stevepiercy who worked on improving merge conditions.

📦 plone/cookiecutter-zope-instance  
[4 files changed, +8/-2 lines, 1 pull request merged]  
Contributions focused on adding support for Python 3.15 in the template testing.

📦 plone/meta  
[1 file changed, +1/-1 lines, 0 pull requests merged]  
A minor update to the CI configuration was made to reflect recent changes.

📦 plone/plone-contributor-statistics  
[6430 files changed, +166272/-50517 lines, 9 pull requests merged]  
A major restructuring effort was undertaken by @jensens, focusing on enhancing data accuracy related to contributed statistics, improving configuration and the integrity of records.

📦 plone/plone.ping  
[260 files changed, +430/-429 lines, 0 pull requests merged]  
Automated updates were performed primarily by the Upptime Bot, reflecting the status checks across various Plone services.

In conclusion, the Plone organization has made considerable strides this week through collaborative efforts and a focus on updating dependencies, restructuring repositories for better efficiency, and refining processes across multiple projects. 

Contributors this week:  
- @davisagli  
- @mauritsvanrees  
- @jensens  
- @dependabot[bot]  
- @gforcada  
- @petschki  
- @stevepiercy  
- @syahra712  
- @Wagner3UB  
- @sneridagh  
- @ericof  


Automatically generated from 22 active repositories.
