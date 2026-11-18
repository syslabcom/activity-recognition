📊 WEEKLY SUMMARY  
*2026-11-11 to 2026-11-18*

This week in the Plone organization saw significant contributions across various repositories, including maintenance updates, feature enhancements, and bug fixes. A notable highlight was the ongoing refactoring efforts and improvements in CI workflows.

📦 plone/plone.app.multilingual  
*3 files changed, +3/-3 lines, 1 pull request merged*  
Dependabot updated `astral-sh/setup-uv` from version 10.3.2 to 10.3.3, enhancing the action's functionality, alongside a CI fix by Gil Forcada that uses the latest `pipforester`.

📦 plone/plone.app.querystring  
*11 files changed, +102/-12 lines, 1 pull request merged*  
Peter Mathis implemented a fix for path criteria when the virtual root is above the portal, addressing empty query results for folder contents.

📦 plone/plone.subrequest  
*1 file changed, +5/-5 lines, 1 pull request merged*  
Maintained by the pre-commit CI bot, this update automated the code formatting to align with the latest standards.

📦 plone/plone.schemaeditor  
*1 file changed, +5/-5 lines, 1 pull request merged*  
Another update from the pre-commit CI bot for keeping the codebase clean and consistent.

📦 plone/plone.testing  
*1 file changed, +5/-5 lines, 1 pull request merged*  
Standard maintenance update from the pre-commit CI bot.

📦 plone/plone.app.dexterity  
*7 files changed, +25/-5 lines, 2 pull requests merged*  
Jens W. Klein temporarily disabled a circular CI job caused by a dependency cycle, while Dependabot performed another version bump on `astral-sh/setup-uv`.

📦 plone/plone.uuid  
*1 file changed, +5/-5 lines, 1 pull request merged*  
Managed by the pre-commit CI bot, which ensured adherence to the coding standards.

📦 plone/plone.stringinterp  
*1 file changed, +5/-5 lines, 1 pull request merged*  
Maintenance update from the pre-commit CI bot.

📦 plone/plone.app.content  
*1 file changed, +1/-1 line, 1 pull request merged*  
Dependabot upgraded `astral-sh/setup-uv` from 10.3.1 to 10.3.3.

📦 plone/plone.registry  
*1 file changed, +5/-5 lines, 1 pull request merged*  
Another update from the pre-commit CI bot for consistent code quality.

📦 plone/plone.app.upgrade  
*2 files changed, +14/-1 lines, 1 pull request merged*  
Maurits van Rees added an upgrade to support Plone 6.2.4.

📦 plone/plone.app.workflow  
*6 files changed, +25/-12 lines, 1 pull request merged*  
Contributed by Maurits van Rees and the pre-commit CI bot, this update focuses on maintaining code quality while preparing for future releases.

📦 plone/plone.app.users  
*1 file changed, +1/-1 line, 1 pull request merged*  
Dependabot's version bump from 10.3.0 to 10.3.3 on `astral-sh/setup-uv`.

📦 plone/plone.app.layout  
*7 files changed, +25/-5 lines, 2 pull requests merged*  
Another contribution from Jens W. Klein to disable the circular CI job, alongside Dependabot's versioning updates.

📦 plone/buildout.coredev  
*76 files changed, +1159/-1125 lines, 1 pull request merged*  
Significant updates to support Zope 6.3 and Python 3.11 to 3.15 by Maurits van Rees and others, improving compatibility with newer dependencies.

📦 plone/plone.app.themingplugins  
*62 files changed, +1129/-351 lines, 1 pull request merged*  
Rémi Dubois modernized the package by incorporating `plone.meta`, enhancing compatibility with Plone 6.

📦 plone/Products.CMFPlone  
*39 files changed, +130/-89 lines, 3 pull requests merged*  
Maurits van Rees and Peter Mathis focused on QA fixes for robot tests, enhancing stability and reliability in the latest iterations.

📦 plone/plone.app.robotframework  
*9 files changed, +36/-9 lines, 1 pull request merged*  
Updates from Maurits van Rees and Peter Mathis to keep the testing framework aligned with recent changes.

📦 plone/plone.restapi  
*48 files changed, +432/-214 lines, 3 pull requests merged*  
David Glick and Victor Fernandez de Alba made substantial improvements, including updates to package configurations and support for new block types.

📦 plone/volto  
*207 files changed, +5141/-606 lines, 7 pull requests merged*  
Major updates from various contributors to enhance user experience, including bug fixes and new features for Volto.

📦 plone/guillotina_elasticsearch  
*10 files changed, +255/-24 lines, 1 pull request merged*  
Improvements by Roger Boixader Güell optimizing the automatic context path filter in Elasticsearch queries.

📦 plone/demo.plone.org  
*24 files changed, +31/-44 lines, 1 pull request merged*  
Maurits van Rees updated to Plone 6.2.3 and removed outdated dependencies improving the project's performance.

📦 plone/container-frontend  
*2 files changed, +2/-2 lines, 1 pull request merged*  
David Glick ensured the latest base images are used while building the container application.

📦 plone/meta  
*37 files changed, +93/-43 lines, 4 pull requests merged*  
Highlighted by Gil Forcada and Jens W. Klein's work on optimizing configurations and ignoring unnecessary cycles in workflows.

📦 plone/cookieplone-templates  
*219 files changed, +4349/-1305 lines, 4 pull requests merged*  
Contributions from multiple authors aimed at updating dependencies and ensuring template compatibility with the latest Plone features.

📦 plone/form-block  
*22 files changed, +867/-341 lines, 1 pull request merged*  
Érico Andrei added support for the `@blocks-schema` endpoint in the form block, enhancing documentation and usability.

📦 plone/plone.observability  
*104 files changed, +3058/-311 lines, 1 pull request merged*  
Jens W. Klein released version 1.3.1, addressing several issues with observability metrics and improving overall performance.

📦 plone/aurora  
*39 files changed, +1772/-44 lines, 4 pull requests merged*  
Victor Fernandez de Alba and Richard Braun optimized the CI for visual regression testing and enhanced the user interface for managing add-ons.

📦 plone/plone-ping  
*286 files changed, +476/-473 lines, 1 pull request merged*  
Updates made by the Upptime bot for maintaining the site's status checks and summary updates.

📦 plone/container-aurora  
*1 file changed, +2/-0 lines, 1 pull request merged*  
David Glick added functionality to pull the latest base images during builds.

📦 plone/aurora-visual-regression  
*35 files changed, +0/-0 lines, 2 pull requests merged*  
Automated updates of visual regression screenshots by the GitHub Actions bot.

Overall, this week reflected the ongoing dedication of contributors across the Plone ecosystem to enhance functionality, improve code quality, and ensure robust system maintenance. The collaborative efforts and multiple enhancements across repositories indicate a vibrant and active community.

**Contributors:**  
Gil Forcada Codinachs, Maurits van Rees, Peter Mathis, Jens W. Klein, Rémi Dubois, David Glick, Victor Fernandez de Alba, Érico Andrei, Richard Braun, Sashank Bhamidi, Ramon Navarro Bosch, Dante Álvarez, Xavi, Alé-Rt, and several automated contributions by bots.

*Automatically generated from 39 active repositories.*
