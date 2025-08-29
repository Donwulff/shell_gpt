# Shell Command Execution

ShellGPT can suggest shell commands and, when explicitly enabled, execute them.
This document explains the options and environment variables that control this
behaviour.

## `--shell`

Passing the `--shell` flag makes ShellGPT generate shell commands instead of
plain text. By default, generated commands are **not** executed.

## `SHELL_INTERACTION`

`SHELL_INTERACTION` controls whether ShellGPT may execute commands it
suggests. The default value is `false`, meaning commands are never executed
without explicit opt‑in. Set `SHELL_INTERACTION=true` or pass the
`--interaction` flag together with `--shell` to allow the program to prompt for
execution.

## `DEFAULT_EXECUTE_SHELL_CMD`

When `SHELL_INTERACTION` is enabled, ShellGPT prompts you with
`[E]xecute, [M]odify, [D]escribe, [A]bort` before running a command. By default
pressing Enter chooses `[A]bort`. Setting
`DEFAULT_EXECUTE_SHELL_CMD=true` changes the default to `[E]xecute`, which will
run the command on Enter. This is not recommended for security reasons.

## Security

Shell commands are executed only when all of the following conditions are met:

1. The `--shell` flag is provided.
2. `SHELL_INTERACTION=true` (or `--interaction` is passed).
3. You explicitly choose to execute the command when prompted.

If any of these conditions are not satisfied, ShellGPT will not run the
suggested command.
