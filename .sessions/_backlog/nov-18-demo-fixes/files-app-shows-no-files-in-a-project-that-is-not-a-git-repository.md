# Files app shows no files in a project that is not a git repository

In a plain folder (client-testimonial-video-creator, dev lane port 9783): "All session files" says "No files here yet" though ticket.root_files and ticket.fidelity_files answer every file; "This session" lists only branch-changed files, and with no git nothing is ever changed, so it should fall back to the files the session's fidelities declare; and ?session-folder=<ticket> lists only .sessions/<ticket>/, not the session's .context/ files.
