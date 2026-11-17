```markdown
📊 WEEKLY SUMMARY  
2026-11-10 to 2026-11-17  

This week in the Plone organization saw significant activity across various repositories, including infrastructure improvements, maintenance releases, and feature enhancements for the Plone ecosystem. Notably, contributors focused on updating dependencies, refining CI configurations, and improving user experience through various bug fixes and documentation updates.

📦 plone/plone.app.multilingual  
[3 files changed, +3/-3 lines, 1 pull request merged]  
Updated CI configuration by bumping the `astral-sh/setup-uv` version to 10.3.3 and fixed the CI by using the latest `pipforester`. 

📦 plone/plone.app.querystring  
[11 files changed, +102/-12 lines, 1 pull request merged]  
Implemented a fix for path criteria when the virtual root is above the portal. Additional formatting adjustments were made alongside this fix.

📦 plone/plone.app.dexterity  
[7 files changed, +25/-5 lines, 1 pull request merged]  
Temporarily disabled a circular CI job to address the dependency cycle issue caused by the recent merge of portlets, and updated the `astral-sh/setup-uv` dependency.

📦 plone/plone.app.content  
[1 file changed, +1/-1 lines, 1 pull request merged]  
Updated the version of `astral-sh/setup-uv` from 10.3.1 to 10.3.3.

📦 plone/Products.CMFPlone  
[44 files changed, +309/-119 lines, 9 pull requests merged]  
Introduced multiple enhancements including small QA fixes, a backport for robot tests related to default page overlays, and various code quality improvements to maintain compatibility with upcoming versions.

📦 plone/plone.app.upgrade  
[6 files changed, +25/-4 lines, 3 direct commits]  
Focused on upgrades related to Plone 6.2.4 and preparations for the development of future releases.

📦 plone/plone.app.users  
[1 file changed, +1/-1 lines, 1 pull request merged]  
Updated the `astral-sh/setup-uv` dependency from 10.3.0 to 10.3.3.

📦 plone/plone.app.layout  
[7 files changed, +25/-5 lines, 1 pull request merged]  
Disabled the circular CI job temporarily, with a similar update to the Astral dependency.

📦 plone/buildout.coredev  
[84 files changed, +1216/-1338 lines, 6 pull requests merged]  
Upgraded to test against Python 3.11 and Zope 6.3, including various dependency adjustments and improvements in CI configurations.

📦 plone/Products.MimetypesRegistry  
[7 files changed, +38/-6 lines, 3 direct commits]  
Updated development versions and released 4.0.2, with minor fixes.

📦 plone/plone.restapi  
[31 files changed, +427/-131 lines, 2 pull requests merged]  
Added support for the new plate block type for Plate regions, enhancing the unified Plate editor experience in Plone Aurora.

📦 plone/plone.batching  
[7 files changed, +69/-6 lines, 3 direct commits]  
Continued development with the upcoming 3.0.4 release, focusing on cleanup and maintenance.

📦 plone/plone.app.mosaic  
[28 files changed, +171/-26 lines, 2 pull requests merged]  
Enhanced the usability of the TinyMCE toolbar and improved form rendering in the Mosaic editor.

📦 plone/plone.volto  
[207 files changed, +5141/-606 lines, 3 pull requests merged]  
Significant updates including a fix for dropdown clipping issues, enhancements to the Maps block, and the introduction of various new features related to content management.

📦 plone/plone.ping  
[169 files changed, +385/-384 lines, 1 direct commit]  
Routine status updates and maintenance performed, including checks for server response.

[An emphasis was placed on reducing code complexity and improving overall performance across many repositories this week, which reflects ongoing maintenance efforts to keep the Plone ecosystem robust and user-friendly.]

**Contributors:**  
Gil Forcada Codinachs, Maurits van Rees, Peter Mathis, Jens W. Klein, Victor Fernandez de Alba, Érico Andrei, David Glick, Dante Álvarez, and others.

Automatically generated from 32 active repositories.
```
