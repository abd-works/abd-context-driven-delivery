# Story tests: the code formats

The code formats write a story map as runnable story tests and read those tests back into the same map. The classes are *CodeStoryModel* and its language subclasses in `practices/stories/model/` (`code_story_model.py`, `brace_story.py`, `python/`, `typescript/`, `javascript/`, `java/`), described in `practices/stories/model/.context/story-model.md`. This document explains the layout they write and why the code inside a story test survives regeneration.

## Layout

```
<tests-root>/
  story-test.ts                        <- step library every story file imports (TypeScript; story-test.js for JavaScript)
  <epic-slug>/
    examples/                          <- example values shared by the stories below
    <epic>_story.test.ts               <- the epic's own stories, when it has any
    <sub-epic>_story.test.ts           <- one file per sub-epic that has no sub-epics of its own
    <sub-epic-slug>/                   <- a sub-epic with sub-epics of its own is a folder
      <nested-sub-epic>_story.test.ts
```

| Language | Story file | Format class |
| --- | --- | --- |
| TypeScript | `{sub_epic}_story.test.ts` (also reads `_story.spec.ts`) | *TypeScriptStoryModel* |
| JavaScript | `{sub_epic}_story.test.js` | *JavaScriptStoryModel* |
| Python | `{sub_epic}_story.test.py` | *PythonStoryModel* |
| Java | `{SubEpic}Story.java` | *JavaStoryModel* |

Each story file opens with a comment naming its epic and its order on the map, imports `story` and `scenario` from the step library and the example values it uses, then holds one `story(...)` block per story with its backgrounds and `scenario(...)` blocks, each step written as a Given, When, Then, And, or But call with its code inside. Java writes no step library: each story is a doc comment listing its steps, with no code to keep.

The step library is written only for a new tree. A tree read from code already has its own, so rendering never replaces it. TypeScript and JavaScript start a new tree's step library from `practices/stories/model/{typescript,javascript}/seeds/story-test.{ts,js}`; Python's comes from `practices/stories/templates/py/story_test.py`.

## Why the code survives

A story test holds two kinds of content: what the story map knows (story, scenario, and step names, actors, examples) and the code someone wrote to run each step against the system. Generating the file again from the map must not lose that code.

- **Every node keeps the code it was read with.** Reading a story file gives each story, background, and scenario the block it was written as (`written`), the code inside it that is not a scenario or step (`setup`), and each step its `body`. The file is read once: each story is made from its own block, and each story, scenario, and step reads its own block (`read_code`); the file's own code above the first story and below the last stays with the file (*StoryFile*).
- **An unchanged node is written exactly as read.** While a node's `code_key` (for a story: its name, actors, evidence, and backgrounds; for a step: its keyword, text, and body) is the one it was read with, rendering in the same language writes its lines unchanged. A changed node is spelled again from the map with its bodies kept.
- **Rendering takes the previous tree's code.** `render(canonical, previous)` is given the tree already on disk; every epic, story, scenario, and step in the new map that has no code in this language takes the code of the node with the same name in that tree. Moving a story or adding a scenario therefore keeps every step body that was already written.

## Adding a language

1. Subclass *CodeStoryModel* (or *BraceStoryModel* for a language with braces), set `language`, `epic_type`, `story_type`, and `writing_type`.
2. Subclass *StoryWriting* (or *BraceStoryWriting*) for how the language writes a story file: give as data what differs (`file_name_template`, the indents, the opening and closing templates, the verbs) and as operations only what a template cannot say (`file_header`, `story_open`, the background lines). `CodeStoryModel.load` reads every language's story files one way; the language's story and scenario classes give only the patterns their text uses (`_NAME`, `_STORY_START`, `_SCENARIO`, `_IMPORT`).
3. Add a *StoryFile* that finds each block in a file, and a block class that answers the *CodeBlock* shape: each story is made from its block and keeps the code read in that language. Give the format its `story_file_suffixes`, and its `not_story_paths` when some files that end that way hold no story.
4. List the format under `formats` in `Stories` (`practices/stories/stories.py`).
