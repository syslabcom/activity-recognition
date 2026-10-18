# 📊 WEEKLY SUMMARY
**2026-10-11 to 2026-10-18**

This week, Plone's open-source ecosystem saw significant contributions across numerous repositories, with a focus on infrastructure improvements and contributions to ongoing project features. Particularly notable were metadata migrations and updates to improve the functionality of various Plone components.

## 📦 plone/plone.event
**[10 files changed, +124/-102 lines, 1 pull request merged]**  
Gil Forcada Codinachs implemented a feature to move project metadata from `setup.py` to `pyproject.toml`, aiming to enhance configuration management. 

## 📦 plone/plone.formwidget.recurrence
**[25 files changed, +190/-172 lines, 1 pull request merged]**  
The project saw improvements by relocating metadata from `setup.py` to `pyproject.toml`, in line with ongoing efforts for configuration standardization.

## 📦 plone/plone.app.event
**[2 files changed, +2/-2 lines, 1 pull request merged]**  
Dependabot updated the `astral-sh/setup-uv` dependency from version 10.2.0 to 10.3.0, adding enhancements to the workflows.

## 📦 plone/plone.app.multilingual
**[18 files changed, +53/-45 lines, 1 pull request merged]**  
Developers removed `plone.restapi` and `plone.rest` as hard dependencies, streamlining project dependencies and improving compatibility.

## 📦 plone/plone.app.querystring
**[25 files changed, +738/-8 lines, 4 pull requests merged]**  
This repository received updates for dependency bumps and substantial enhancements, including the introduction of new query string operations and improved handling for virtual hosting paths.

## 📦 plone/plone.namedfile
**[29 files changed, +373/-158 lines, 2 pull requests merged]**  
Improvements were made to the `filestream_range_iterator` to better handle end range requests, and project metadata was moved to `pyproject.toml`, enhancing overall maintainability.

## 📦 plone/plone.formwidget.namedfile
**[10 files changed, +122/-90 lines, 1 pull request merged]**  
Metadata was shifted from `setup.py` to `pyproject.toml`, part of broader efforts to modernize project configurations across Plone.

## 📦 plone/plone.folder
**[10 files changed, +122/-116 lines, 1 pull request merged]**  
As with other repositories, this one also transitioned metadata from `setup.py` to `pyproject.toml`, promoting consistency in project formatting.

## 📦 plone/plone.app.relationfield
**[2 files changed, +2/-2 lines, 1 pull request merged]**  
Dependabot updated `setup-uv`, ensuring continued compatibility with the latest dependency features.

## 📦 plone/plone.app.linkintegrity
**[4 files changed, +20/-7 lines, 1 pull request merged]**  
MrTango implemented a change to create only one reference per linked object, improving how relations are managed in the integrity framework.

## 📦 plone/plone.portlets
**[4 files changed, +70/-65 lines, 1 pull request merged]**  
As part of the ongoing transition to `pyproject.toml`, metadata has been effectively moved, streamlining further developments.

## 📦 plone/plone.indexer
**[10 files changed, +114/-92 lines, 1 pull request merged]**  
Similar updates were made regarding the migration of metadata, alongside several structural improvements aimed at optimizing indexing performance.

## 📦 plone/plone.locking
**[10 files changed, +118/-104 lines, 2 pull requests merged]**  
Changes included moving metadata to `pyproject.toml` and updating dependencies for improved functionality.

## 📦 plone/plone.portlet.collection
**[4 files changed, +70/-57 lines, 1 pull request merged]**  
Efforts to migrate project metadata continued, enhancing configuration practices moving forward.

## 📦 plone/plone.keyring
**[10 files changed, +106/-80 lines, 2 pull requests merged]**  
Contributors migrated metadata, contributing to overall strategic improvements across the repository.

## 📦 plone/plone.portlet.static
**[4 files changed, +63/-57 lines, 1 pull request merged]**  
The repository underwent similar updates for metadata management as part of the broader sustainability strategy.

## 📦 plone/plone.outputfilters
**[10 files changed, +150/-134 lines, 1 pull request merged]**  
Updates involved refining output handling, with enhancements made to metadata configurations.

## 📦 plone/plone.intelligenttext
**[14 files changed, +106/-88 lines, 1 pull request merged]**  
Adapter for modern tooling was added, improving how intelligent text insights are generated.

## 📦 plone/plone.i18n
**[10 files changed, +132/-122 lines, 1 pull request merged]**  
Improvements to locale handling were undertaken, following the ongoing migration efforts.

## 📦 plone/Products.CMFPlone
**[2 files changed, +6/-2 lines, 1 pull request merged]**  
MrTango made changes to ensure the Robot content-browser link targets are selected by title, enhancing consistency in testing.

## 📦 plone/plone.memoize
**[17 files changed, +136/-124 lines, 2 pull requests merged]**  
Updates included dependency management improvements alongside metadata migrations.

## 📦 plone/buildout.coredev
**[41 files changed, +590/-481 lines, 2 pull requests merged]**  
This week, several dependencies were adjusted to maintain overall consistency and build stability within the Plone framework.

## 📦 plone/training
**[4 files changed, +4/-4 lines, 1 pull request merged]**  
Dependency bumps were implemented to maintain compatibility with upcoming changes in the Plone stack.

## 📦 plone/plone-contributor-statistics
**[886 files changed, +53125/-29386 lines, 5 pull requests merged]**  
A major restructuring of contributor data took place, improving the accuracy of statistics and addressing longstanding issues regarding organization mapping.

## 📦 plone/pastanaga-angular
**[2 files changed, +8/-3 lines, 1 pull request merged]**  
The deprecated `@angular/animations` package was removed as part of ongoing maintenance work.

## 📦 plone/plone.volto
**[20 files changed, +4766/-4069 lines, 7 pull requests merged]**  
Substantial updates to Volto included numerous dependency updates and enhancements for visual regression testing, aiming to improve development speed and reliability.

## 📦 plone/cookiecutter-zope-instance
**[74 files changed, +2627/-214 lines, 3 pull requests merged]**  
Significant contributions included tools to improve default context handling, making customization processes more robust and less error-prone.

## 📦 plone/mockup
**[19 files changed, +3173/-3062 lines, 3 pull requests merged]**  
The repository saw extensive updates, including dependency management improvements and various bug fixes aimed at enhancing mockup stability.

## 📦 plone/aurora
**[218 files changed, +6163/-913 lines, 2 pull requests merged]**  
Key contributions were made addressing visual regression tests while building the Quanta components inventory.

## 📦 plone/plone-ping
**[169 files changed, +310/-309 lines, 0 pull requests merged]**  
Updates were primarily executed through automated bot contributions focusing on maintaining status logs and reporting metrics.

## 📦 plone/collective.icalendar
**[2 files changed, +0/-0 lines, 0 pull requests merged]**  
No significant updates were logged this week.

## 📦 plone/aurora-visual-regression
**[255 files changed, +0/-0 lines, 0 pull requests merged]**  
Visual regression testing resources were updated, reinforcing testing protocols for code quality.

In summary, the Plone ecosystem has made substantial strides this week with mixed contributions across the entire organization. Noteworthy is the cohesive push to migrate metadata configurations, which should significantly aid future development workflows and enhance compatibility. 

### Contributors
- Gil Forcada Codinachs
- MrTango
- Mikel Larreategi
- David Glick
- Érico Andrei
- Kunal Kumar
- Peter Mathis
- Davisagli
- Johannes Raggam
- Tishasoumya-02
- 1letter
- jensens
- sneridagh
- Wesleybl
- upptime-bot

Automatically generated from 44 active repositories.
