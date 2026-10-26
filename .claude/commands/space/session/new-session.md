Open a new CDD session folder under the repo.

Ask the user for the session name when it is not already clear from the chat.
Resolve workpath from CDD_PROJECT or the current working directory and repo from CDD_REPO or the current directory.
Call MCP ``session.new`` with name, workpath, and repo_path. Do not call ``session.open_named``.
