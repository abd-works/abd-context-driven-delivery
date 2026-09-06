import json
data = json.load(open("C:/dev/paradise-mobile/pml-my/docs/stories/story-graph.json", encoding="utf-8"))
for ep in data.get("epics", []):
    if "Complete Onboarding" in ep.get("name", ""):
        for se in ep.get("sub_epics", []):
            print("SUB-EPIC:", se["name"])
            for sg in se.get("story_groups", []):
                for s in sg.get("stories", []):
                    tfs = len(s.get("test_files", []))
                    scens = len(s.get("scenarios", []))
                    acs = len(s.get("acceptance_criteria", []))
                    print("  STORY:", s["name"][:70])
                    print("    test_files:", tfs, "| scenarios:", scens, "| ACs:", acs)
