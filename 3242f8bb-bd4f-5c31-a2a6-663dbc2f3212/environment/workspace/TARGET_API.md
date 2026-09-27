# Target Rust compatibility surface

Implement the following public module paths and declarations. Bodies are intentionally omitted. Preserve behavior of the source implementation and its tests. This describes compatibility, not internal implementation.

## src/cmd/cmd_allow.rs
```rust
pub fn cmd_allow() -> Cmd
```

## src/cmd/cmd_apply_dump.rs
```rust
pub fn cmd_apply_dump() -> Cmd
```

## src/cmd/cmd_check_required.rs
```rust
pub fn cmd_check_required() -> Cmd
```

## src/cmd/cmd_current.rs
```rust
pub fn cmd_current() -> Cmd
```

## src/cmd/cmd_deny.rs
```rust
pub fn cmd_deny() -> Cmd
```

## src/cmd/cmd_dotenv.rs
```rust
pub fn cmd_dotenv() -> Cmd
```

## src/cmd/cmd_dump.rs
```rust
pub fn cmd_dump() -> Cmd
```

## src/cmd/cmd_edit.rs
```rust
pub fn cmd_edit() -> Cmd
pub const EDITORS: &[&[&str]] = &[ &["editor"], &["subl", "-w"], &["mate", "-w"], &["open", "-t", "-W"], // Opens with the default text editor on mac &["nano"], &["vim"], &["emacs"], ]
```

## src/cmd/cmd_exec.rs
```rust
pub fn cmd_exec() -> Cmd
```

## src/cmd/cmd_export.rs
```rust
pub fn cmd_export() -> Cmd
```

## src/cmd/cmd_fetchurl.rs
```rust
pub fn cmd_fetchurl() -> Cmd
impl Drop for TempFile
```

## src/cmd/cmd_help.rs
```rust
pub fn cmd_help() -> Cmd
```

## src/cmd/cmd_hook.rs
```rust
pub fn cmd_hook() -> Cmd
```

## src/cmd/cmd_log.rs
```rust
pub fn cmd_log() -> Cmd
```

## src/cmd/cmd_prune.rs
```rust
pub fn cmd_prune() -> Cmd
```

## src/cmd/cmd_reload.rs
```rust
pub fn cmd_reload() -> Cmd
```

## src/cmd/cmd_show_dump.rs
```rust
pub fn cmd_show_dump() -> Cmd
```

## src/cmd/cmd_status.rs
```rust
pub fn cmd_status() -> Cmd
```

## src/cmd/cmd_stdlib.rs
```rust
pub fn cmd_stdlib() -> Cmd
```

## src/cmd/cmd_version.rs
```rust
pub fn cmd_version() -> Cmd
pub fn ensure_v_prefixed(version: &str) -> String
```

## src/cmd/cmd_watch.rs
```rust
pub fn cmd_watch() -> Cmd
```

## src/cmd/cmd_watch_dir.rs
```rust
pub fn cmd_watch_dir() -> Cmd
```

## src/cmd/cmd_watch_list.rs
```rust
pub fn cmd_watch_list() -> Cmd
```

## src/cmd/cmd_watch_print.rs
```rust
pub fn cmd_watch_print() -> Cmd
```

## src/cmd/commands.rs
```rust
pub enum Action
impl Action
pub struct Cmd
pub name: &'static str, pub desc: String, pub args: &'static [&'static str], pub aliases: &'static [&'static str], pub private: bool, pub action: Action, }  /// The list of all direnv sub-commands, in `direnv help` order. pub fn cmd_list() -> Vec<Cmd>
pub fn commands_dispatch(env: &Env, args: &[String]) -> Result<()>
```

## src/cmd/config.rs
```rust
pub struct Config
pub env: Env, /// Current directory. pub work_dir: String, pub conf_dir: String, pub cache_dir: String, pub data_dir: String, pub self_path: String, pub bash_path: String, pub rc_file: String, pub toml_path: String, pub hide_env_diff: bool, pub disable_stdin: bool, pub strict_env: bool, pub load_dotenv: bool, pub log_format: String, pub log_filter: Option<Regex>, pub log_color: bool, /// Nanoseconds, matching Go's `time.Duration`. pub warn_timeout: i64, pub whitelist_prefix: Vec<String>, pub whitelist_exact: BTreeMap<String, bool>, }  impl Default for Config
pub fn load_config(env: &Env) -> Result<Config>
impl Config
pub fn allow_dir(&self) -> String
pub fn deny_dir(&self) -> String
pub fn allowed_required_dir(&self) -> String
pub fn loaded_rc(&self) -> Option<RC>
pub fn env_from_rc_pair(&self, path: &str, previous_env: &Env) -> (Option<Env>, Option<Error>)
pub fn find_rc(&self) -> Result<Option<RC>>
pub fn revert(&self, env: &Env) -> Result<Env>
pub fn format_string_slice(items: &[String]) -> String
pub fn format_string_bool_map(map: &BTreeMap<String, bool>) -> String
```

## src/cmd/consts.rs
```rust
pub const DIRENV_CONFIG: &str = "DIRENV_CONFIG"
pub const DIRENV_BASH: &str = "DIRENV_BASH"
pub const DIRENV_DEBUG: &str = "DIRENV_DEBUG"
pub const DIRENV_DIR: &str = "DIRENV_DIR"
pub const DIRENV_FILE: &str = "DIRENV_FILE"
pub const DIRENV_WATCHES: &str = "DIRENV_WATCHES"
pub const DIRENV_DIFF: &str = "DIRENV_DIFF"
pub const DIRENV_REQUIRED: &str = "DIRENV_REQUIRED"
pub const DIRENV_DUMP_FILE_PATH: &str = "DIRENV_DUMP_FILE_PATH"
```

## src/cmd/env.rs
```rust
pub struct Env(pub HashMap<String, String>)
impl Env
pub fn new() -> Env
pub fn from_process() -> Env
pub fn get(&self, key: &str) -> Option<&String>
pub fn get_or_empty(&self, key: &str) -> &str
pub fn contains_key(&self, key: &str) -> bool
pub fn insert(&mut self, key: &str, value: &str)
pub fn remove(&mut self, key: &str)
pub fn len(&self) -> usize
pub fn is_empty(&self) -> bool
pub fn iter(&self) -> std::collections::hash_map::Iter<'_, String, String>
pub fn clean_context(&mut self)
pub fn copy(&self) -> Env
pub fn to_go_env(&self) -> Vec<String>
pub fn to_shell(&self, shell: &dyn Shell) -> Result<String>
pub fn serialize(&self) -> String
pub fn diff(&self, other: &Env) -> EnvDiff
pub fn fetch(&self, key: &str, default: &str) -> String
impl From<HashMap<String, String>> for Env
pub fn load_env(gzenv_str: &str) -> Result<Env>
pub fn load_env_json(json_bytes: &[u8]) -> Result<Env>
```

## src/cmd/env_diff.rs
```rust
pub fn ignored_keys() -> &'static [&'static str]
pub struct EnvDiff
pub prev: HashMap<String, String>, /// Serialised as `"n"`. pub next: HashMap<String, String>, }  impl EnvDiff
pub fn new() -> EnvDiff
pub fn any(&self) -> bool
pub fn to_shell(&self, shell: &dyn Shell) -> Result<String>
pub fn patch(&self, env: &Env) -> Env
pub fn reverse(&self) -> EnvDiff
pub fn serialize(&self) -> String
pub fn build_env_diff(e1: &Env, e2: &Env) -> EnvDiff
pub fn load_env_diff(gzenv_str: &str) -> Result<EnvDiff>
pub fn ignored_env(key: &str) -> bool
```

## src/cmd/file_times.rs
```rust
pub struct FileTime
pub path: String, pub modtime: i64, pub exists: bool, }  impl FileTime
pub fn check(&self) -> Result<()>
pub fn formatted(&self, rel_dir: &str) -> String
pub fn to_json(&self) -> JsonValue
pub struct FileTimes
pub list: Vec<FileTime>, }  impl FileTimes
pub fn new() -> FileTimes
pub fn update(&mut self, path: &str) -> Result<()>
pub fn new_time(&mut self, path: &str, modtime: i64, exists: bool) -> Result<()>
pub fn check(&self) -> Result<()>
pub fn check_one(&self, path: &str) -> Result<()>
pub fn marshal(&self) -> String
pub fn unmarshal(&mut self, from: &str) -> Result<()>
```

## src/cmd/log.rs
```rust
pub const DEFAULT_LOG_FORMAT: &str = "direnv: %s"
pub const ERROR_COLOR: &str = "\x1b[31m"
pub const CLEAR_COLOR: &str = "\x1b[0m"
pub fn setup_logging(env: &Env)
pub fn prefix() -> String
pub fn set_prefix(value: &str)
pub struct PrefixGuard(String)
impl PrefixGuard
pub fn push(extra: &str) -> PrefixGuard
impl Drop for PrefixGuard
pub fn debugging() -> bool
pub fn log_error(config: &Config, message: &str)
pub fn log_error_args(config: &Config, message: &str, args: &[Arg])
pub fn log_status(config: &Config, message: &str)
pub fn log_status_args(config: &Config, message: &str, args: &[Arg])
pub fn log_debug_at(file: &str, line: u32, message: &str)
```

## src/cmd/look_path.rs
```rust
pub const ERR_NOT_FOUND: &str = "executable file not found in $PATH"
pub fn look_path(file: &str, pathenv: &str) -> Result<String, String>
```

## src/cmd/mod.rs
```rust
pub mod cmd_allow
pub mod cmd_apply_dump
pub mod cmd_check_required
pub mod cmd_current
pub mod cmd_deny
pub mod cmd_dotenv
pub mod cmd_dump
pub mod cmd_edit
pub mod cmd_exec
pub mod cmd_export
pub mod cmd_fetchurl
pub mod cmd_help
pub mod cmd_hook
pub mod cmd_log
pub mod cmd_prune
pub mod cmd_reload
pub mod cmd_show_dump
pub mod cmd_status
pub mod cmd_stdlib
pub mod cmd_version
pub mod cmd_watch
pub mod cmd_watch_dir
pub mod cmd_watch_list
pub mod cmd_watch_print
pub mod commands
pub mod config
pub mod consts
pub mod env
pub mod env_diff
pub mod file_times
pub mod log
pub mod look_path
pub mod printf
pub mod rc
pub mod shell
pub mod shell_bash
pub mod shell_elvish
pub mod shell_fish
pub mod shell_gha
pub mod shell_gzenv
pub mod shell_json
pub mod shell_murex
pub mod shell_pwsh
pub mod shell_systemd
pub mod shell_tcsh
pub mod shell_vim
pub mod shell_zsh
pub mod stdlib
pub fn bash_path() -> &'static str
pub fn stdlib_source() -> &'static str
pub fn version() -> &'static str
pub fn main( env: &Env, args: &[String], mod_bash_path: &str, mod_stdlib: &str, mod_version: &str, ) -> Result<()>
```

## src/cmd/printf.rs
```rust
pub enum Arg
impl Arg
pub fn sprintf(format: &str, args: &[Arg]) -> String
```

## src/cmd/rc.rs
```rust
pub struct RC
pub(crate) path: String, pub(crate) allow_path: String, pub(crate) deny_path: String, pub(crate) times: FileTimes, config: Config, }  /// The permission status of an RC file. /// /// The numeric values are user-visible: `direnv status` prints them raw and /// `direnv status --json` marshals them as numbers. #[derive(Debug, Clone, Copy, PartialEq, Eq)] pub enum AllowStatus
impl std::fmt::Display for AllowStatus
pub fn not_allowed_message(path: &str) -> String
pub fn find_rc(wd: &str, config: &Config) -> Result<Option<RC>>
impl RC
pub fn from_path(path: &str, config: &Config) -> Result<RC>
pub fn allow(&mut self) -> Result<()>
pub fn deny(&self) -> Result<()>
pub fn allowed(&self) -> AllowStatus
pub fn path(&self) -> &str
pub fn times(&self) -> &FileTimes
pub fn allow_path(&self) -> &str
pub fn touch(&self) -> Result<()>
pub fn load(&self, previous_env: &Env) -> (Env, Option<Error>)
pub(crate) fn exit_error(status: &std::process::ExitStatus) -> String
impl InterruptGuard
impl Drop for InterruptGuard
pub fn rc_from_env(path: &str, marshalled_times: &str, config: &Config) -> Option<RC>
pub fn each_dir(path: &str) -> Vec<String>
pub fn file_exists(path: &str) -> bool
pub fn file_hash(path: &str) -> Result<String>
pub fn path_hash(path: &str) -> Result<String>
pub(crate) fn write_file(path: &str, contents: &str, mode: u32) -> Result<()>
pub fn find_env_up(search_dir: &str, load_dotenv: bool) -> String
```

## src/cmd/shell.rs
```rust
pub trait Shell: Sync
pub struct ShellExport(pub HashMap<String, Option<String>>)
impl ShellExport
pub fn new() -> ShellExport
pub fn add(&mut self, key: &str, value: &str)
pub fn remove(&mut self, key: &str)
pub fn iter(&self) -> std::collections::hash_map::Iter<'_, String, Option<String>>
pub static BASH: Bash = Bash
pub static ELVISH: Elvish = Elvish
pub static FISH: Fish = Fish
pub static GITHUB_ACTIONS: GitHubActions = GitHubActions
pub static GZENV: GzEnvShell = GzEnvShell
pub static JSON: JsonShell = JsonShell
pub static MUREX: Murex = Murex
pub static PWSH: Pwsh = Pwsh
pub static SYSTEMD: SystemdShell = SystemdShell
pub static TCSH: Tcsh = Tcsh
pub static VIM: Vim = Vim
pub static ZSH: Zsh = Zsh
pub fn supported_shell_list() -> &'static HashMap<&'static str, &'static dyn Shell>
pub fn detect_shell(target: &str) -> Option<&'static dyn Shell>
```

## src/cmd/shell_bash.rs
```rust
pub struct Bash
impl Shell for Bash
pub(crate) const ACK: u8 = 6
pub(crate) const TAB: u8 = 9
pub(crate) const LF: u8 = 10
pub(crate) const CR: u8 = 13
pub(crate) const US: u8 = 31
pub(crate) const SPACE: u8 = 32
pub(crate) const AMPERSTAND: u8 = 38
pub(crate) const SINGLE_QUOTE: u8 = 39
pub(crate) const STAR: u8 = 42
pub(crate) const PLUS: u8 = 43
pub(crate) const NINE: u8 = 57
pub(crate) const COLON: u8 = 58
pub(crate) const EQUALS: u8 = 61
pub(crate) const QUESTION: u8 = 63
pub(crate) const UPPERCASE_Z: u8 = 90
pub(crate) const OPEN_BRACKET: u8 = 91
pub(crate) const BACKSLASH: u8 = 92
pub(crate) const UNDERSCORE: u8 = 95
pub(crate) const CLOSE_BRACKET: u8 = 93
pub(crate) const BACKTICK: u8 = 96
pub(crate) const LOWERCASE_Z: u8 = 122
pub(crate) const OPEN_CURLY_BRACE: u8 = 123
pub(crate) const CLOSE_CURLY_BRACE: u8 = 125
pub(crate) const TILDE: u8 = 126
pub(crate) const DEL: u8 = 127
pub fn bash_escape(str: &str) -> String
```

## src/cmd/shell_elvish.rs
```rust
pub struct Elvish
impl Shell for Elvish
```

## src/cmd/shell_fish.rs
```rust
pub struct Fish
impl Shell for Fish
```

## src/cmd/shell_gha.rs
```rust
pub struct GitHubActions
impl Shell for GitHubActions
```

## src/cmd/shell_gzenv.rs
```rust
pub struct GzEnvShell
impl Shell for GzEnvShell
```

## src/cmd/shell_json.rs
```rust
pub struct JsonShell
impl Shell for JsonShell
```

## src/cmd/shell_murex.rs
```rust
pub struct Murex
impl Shell for Murex
```

## src/cmd/shell_pwsh.rs
```rust
pub struct Pwsh
impl Shell for Pwsh
pub fn powershell_escape_env_key(str: &str) -> String
pub fn powershell_escape_verbatim_env_key(str: &str) -> String
pub fn powershell_escape_verbatim_string(str: &str) -> String
```

## src/cmd/shell_systemd.rs
```rust
pub struct SystemdShell
impl Shell for SystemdShell
pub fn cut_encapsulated<'a>(value_to_test: &'a str, encapsulating_value: &str) -> (&'a str, bool)
pub fn sanitize_value(value: &str) -> String
```

## src/cmd/shell_tcsh.rs
```rust
pub struct Tcsh
impl Shell for Tcsh
```

## src/cmd/shell_vim.rs
```rust
pub struct Vim
impl Shell for Vim
```

## src/cmd/shell_zsh.rs
```rust
pub struct Zsh
impl Shell for Zsh
```

## src/cmd/stdlib.rs
```rust
pub fn get_stdlib(config: &Config) -> String
```

## src/deps/goerr.rs
```rust
pub fn errno_text(err: &io::Error) -> String
pub fn path_error(op: &str, path: &str, err: &io::Error) -> String
```

## src/deps/goexpand.rs
```rust
pub fn expand<F>(text: &str, mapping: F) -> String where F: Fn(&str) -> String,
```

## src/deps/gojson.rs
```rust
pub enum JsonValue
impl JsonValue
pub fn from_string_map(map: &HashMap<String, String>) -> JsonValue
pub fn from_optional_string_map(map: &HashMap<String, Option<String>>) -> JsonValue
pub fn sorted_object(mut pairs: Vec<(String, JsonValue)>) -> JsonValue
pub fn marshal(value: &JsonValue) -> String
pub fn marshal_indent(value: &JsonValue, indent: &str) -> String
pub fn encode(value: &JsonValue) -> String
pub fn parse(text: &str) -> Result<JsonValue, String>
pub fn kind(value: &JsonValue) -> &'static str
pub fn type_error(value: &JsonValue, target: &str) -> String
pub fn field_type_error(value: &JsonValue, path: &str, target: &str) -> String
pub fn element_type_error(value: &JsonValue, path: &str, target: &str) -> String
pub fn decode_string_map( value: &JsonValue, named: &str, prefix: &str, ) -> Result<HashMap<String, String>, String>
pub fn parse_string_map(text: &str) -> Result<HashMap<String, String>, String>
```

## src/deps/gopath.rs
```rust
pub fn clean(path: &str) -> String
pub fn is_abs(path: &str) -> bool
pub fn join(elems: &[&str]) -> String
pub fn base(path: &str) -> String
pub fn dir(path: &str) -> String
pub fn abs(path: &str) -> io::Result<String>
pub fn rel(basepath: &str, targpath: &str) -> Result<String, String>
pub fn to_slash(path: &str) -> String
pub fn eval_symlinks(path: &str) -> io::Result<String>
pub fn walk<F>(root: &str, visit: &mut F) -> io::Result<()> where F: FnMut(&str, &std::fs::Metadata) -> io::Result<()>,
pub fn getwd() -> io::Result<String>
pub fn exists(path: &str) -> bool
```

## src/deps/goregexp.rs
```rust
pub fn compile_pattern(pattern: &str) -> Result<String, String>
pub fn translate(pattern: &str) -> String
```

## src/deps/gosemver.rs
```rust
pub fn is_valid(v: &str) -> bool
pub fn compare(v: &str, w: &str) -> i32
```

## src/deps/gotemplate.rs
```rust
pub struct HookContext
pub self_path: String, }  /// Render `template` against `ctx`. pub fn execute(name: &str, template: &str, ctx: &HookContext) -> Result<String, String>
```

## src/deps/gotime.rs
```rust
pub const NANOSECOND: i64 = 1
pub const MICROSECOND: i64 = 1_000 * NANOSECOND
pub const MILLISECOND: i64 = 1_000 * MICROSECOND
pub const SECOND: i64 = 1_000 * MILLISECOND
pub const MINUTE: i64 = 60 * SECOND
pub const HOUR: i64 = 60 * MINUTE
pub fn parse_duration(input: &str) -> Result<i64, String>
pub fn duration_string(d: i64) -> String
pub fn unix_marshal_text(sec: i64) -> String
```

## src/deps/mod.rs
```rust
pub mod goerr
pub mod goexpand
pub mod gojson
pub mod gopath
pub mod goregexp
pub mod gosemver
pub mod gotemplate
pub mod gotime
```

## src/dotenv/mod.rs
```rust
pub const LINE: &str = r#" \A \s* (?:|#.*|          # comment line (?:export\s+)?    # optional export ([\w\.]+)         # key (?:\s*=\s*|:\s+?) # separator (                 # optional value begin '(?:\'|[^'])*'  #   single quoted value |               #   or "(?:\"|[^"])*"  #   double quoted value |               #   or [^\s#\n]+       #   unquoted value )?                # value end \s* (?:\#.*)?         # optional comment ) \z "#
pub fn parse(data: &str) -> Result<HashMap<String, String>, String>
pub fn must_parse(data: &str) -> HashMap<String, String>
```

## src/gzenv.rs
```rust
pub fn marshal(value: &JsonValue) -> String
pub fn unmarshal(gzenv: &str) -> Result<JsonValue, String>
```

## src/lib.rs
```rust
pub mod cmd
pub mod deps
pub mod dotenv
pub mod gzenv
pub mod sri
pub mod xdg
pub struct Error(pub String)
impl fmt::Display for Error
impl std::error::Error for Error
impl From<String> for Error
impl From<&str> for Error
pub type Result<T> = std::result::Result<T, Error>
```

## src/sri/mod.rs
```rust
pub use parse::parse
pub use writer::Writer
pub enum Algo
impl Algo
pub fn as_str(self) -> &'static str
pub struct Hash
impl Hash
pub(crate) fn new(algo: String, sum: Vec<u8>) -> Hash
pub fn hex(&self) -> String
impl std::fmt::Display for Hash
```

## src/sri/parse.rs
```rust
pub fn parse(sri_hash: &str) -> Result<Hash, String>
```

## src/sri/writer.rs
```rust
pub struct Writer<W: io::Write>
impl<W: io::Write> Writer<W>
pub fn new(w: W, algo: Algo) -> Writer<W>
pub fn sum(self) -> Hash
impl<W: io::Write> io::Write for Writer<W>
```

## src/xdg.rs
```rust
pub fn data_dir(env: &HashMap<String, String>, program_name: &str) -> String
pub fn config_dir(env: &HashMap<String, String>, program_name: &str) -> String
pub fn cache_dir(env: &HashMap<String, String>, program_name: &str) -> String
```

Enum variants in src/cmd/commands.rs:
```rust
pub enum Action {
    Simple(fn(&Env, &[String]) -> Result<()>),
    WithConfig(fn(&Env, &[String], &Config) -> Result<()>),
    WithConfigAndWarnTimeout(fn(&Env, &[String], &Config) -> Result<()>),
}
```

Enum variants in src/cmd/printf.rs:
```rust
pub enum Arg {
    Str(String),
    /// A Go `[]string`, which `%v` renders as `[a b c]`.
    List(Vec<String>),
}
```

Enum variants in src/cmd/rc.rs:
```rust
pub enum AllowStatus {
    /// The RC file is permitted to load.
    Allowed = 0,
    /// The RC file has not been granted permission.
    NotAllowed = 1,
    /// The RC file has been explicitly denied.
    Denied = 2,
}
```

Enum variants in src/deps/gojson.rs:
```rust
pub enum JsonValue {
    Null,
    Bool(bool),
    /// Go unmarshals every JSON number into `float64`, and marshals it back
    /// with `strconv.AppendFloat(_, 'f', -1, 64)` unless the magnitude forces
    /// exponent form.
    Number(f64),
    String(String),
    Array(Vec<JsonValue>),
    /// Key/value pairs in emission order.
    Object(Vec<(String, JsonValue)>),
}
```

Enum variants in src/sri/mod.rs:
```rust
pub enum Algo {
    Sha256,
    Sha384,
    Sha512,
}
```
