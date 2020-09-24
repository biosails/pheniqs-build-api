#!/usr/bin/env bash
set -u

PHENIQS_RELEASE_VERSION="head_static"
PHENIQS_INSTALLER="pheniqs-build-api.py"
PHENIQS_INSTALLER_URL="https://raw.githubusercontent.com/biosails/pheniqs-build-api/master/$PHENIQS_INSTALLER"
PHENIQS_STAGING_DIRECTORY="$HOME/pheniqs_$PHENIQS_RELEASE_VERSION"

shell_join() {
  local arg
  printf "%s" "$1"
  shift
  for arg in "$@"; do
    printf " "
    printf "%s" "${arg// /\ }"
  done
}

execute() {
  if ! "$@"; then
    abort "$(printf "Failed during: %s" "$(shell_join "$@")")"
  fi
}

printf "preparing to build Pheniqs in $PHENIQS_STAGING_DIRECTORY"
if ! [[ -d "$PHENIQS_STAGING_DIRECTORY" ]]; then
    execute "/bin/mkdir" "-p" "$PHENIQS_STAGING_DIRECTORY"
fi

(
    cd "$PHENIQS_STAGING_DIRECTORY";
    curl -fsSLO "$PHENIQS_INSTALLER_URL";
    chmod +x $PHENIQS_INSTALLER;
    execute "./$PHENIQS_INSTALLER" "build"
)

printf "Please copy the portable Pheniqs binary at $PHENIQS_STAGING_DIRECTORY/bin/static-HEAD/install/bin/pheniqs to your path.\n"
