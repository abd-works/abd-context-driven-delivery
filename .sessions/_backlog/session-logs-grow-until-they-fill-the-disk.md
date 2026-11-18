# Session logs grow until they fill the disk

Session logs are written so heavily they fill the drive ("logging like a monster"); people are told to delete them by hand. On Nov 18 C: reached 0 GB free (with test runs' temp leftovers). Wanted: rotation or a size cap, or a kill-session-logs action. Test runs also leave their temp folders behind (about 7 GB that day).
