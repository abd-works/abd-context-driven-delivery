# Render gives no step for placing a rendered document

render returns the converted content but writes no file, and its place_rendered instructions only say how to fold code into modules; a markdown to drawio or whiteboard render has no placing step, so the agent places it by guess. The whiteboard render should go straight onto its board. (The ux-ia render that returned just the slug was ux turned off, fixed in 0d29115c8 on release-1-2-fixes.)
