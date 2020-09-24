#!/usr/bin/env bash
set -u

PHENIQS_RELEASE_VERSION="head_static"
PHENIQS_INSTALLER="pheniqs-build-api.py"
PHENIQS_INSTALLER_URL="https://raw.githubusercontent.com/biosails/pheniqs-build-api/master/$PHENIQS_INSTALLER"
PHENIQS_TEMP_DIRECTORY="~/pheniqs_$PHENIQS_RELEASE_VERSION"

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

if ! [[ -d "$PHENIQS_TEMP_DIRECTORY" ]]; then
    execute "/bin/mkdir" "-p" "$PHENIQS_TEMP_DIRECTORY"
fi

(
    cd "$PHENIQS_TEMP_DIRECTORY";
    curl -fsSLO "$PHENIQS_INSTALLER_URL";
    chmod +x $PHENIQS_INSTALLER;
    execute "./$PHENIQS_INSTALLER" "build"
)

printf "Build successful. Please copy the portable Pheniqs binary at $PHENIQS_TEMP_DIRECTORY/bin/static-HEAD/install/bin/pheniqs to your path.\n"
