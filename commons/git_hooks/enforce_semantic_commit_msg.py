import re
import sys

ERROR_MSG = """
Commit failed!
Please use semantic commit message format. Examples:
    'feat: TT-123 Applying some changes'
    'fix: TT-321 Fixing something broken'
    'feat(config): TT-00 Fix something in config files'

For more details in commit message format, review https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits
"""

SUCCESS_MSG = "Commit succeed!. Semantic commit message is correct."

COMMIT_MSG_REGEX = r'(build|ci|docs|feat|fix|perf|refactor|test|chore|revert)(\([\w\-]+\))?: TT-[0-9]+ .*'  # test

# Get the commit message file
commit_msg_file = open(sys.argv[1])  # The first argument is the file
commit_msg = commit_msg_file.read()

if re.match(COMMIT_MSG_REGEX, commit_msg) is None:
    print(ERROR_MSG)
    sys.exit(1)

print(SUCCESS_MSG)
sys.exit(0)
