:: Dump list of my repos, sorted by ascending last-touched date/time
gh repo list DerellLicht --limit 200 --json name,pushedAt,isArchived --jq "sort_by(.pushedAt)[] | .pushedAt + \"  \" + .name + (if .isArchived then \"  [archived]\" else \"\" end)"
