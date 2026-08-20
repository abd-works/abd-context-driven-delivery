# physical-folder-3

- **entry_id:** bd5f2222
- **artifact:** C:\dev\paradise-mobile\pml-my\src\pages\.context\module-context.md
- **rule:** physical-folder
- **wrong:** Documentation stopped arbitrarily at the top-level page folders (pages/My, pages/Onboarding, pages/SignIn, pages/SignUp, pages/Protected). Each of these is a self-contained sub-application with its own pages, components, hooks, recoil, types, utils, and services layers — dozens of meaningful modules that were left undocumented. Either every folder that represents a cohesive functional unit must get a module-context.md, or sub-folders that are pure implementation details of their parent (assets/, thin config/) should be absorbed into the parent description. Stopping mid-tree at an arbitrary depth is never correct.
- **status:** fixed