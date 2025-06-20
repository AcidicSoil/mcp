# shellcheck shell=bash
_eza() {
    cur=${COMP_WORDS[COMP_CWORD]}
    prev=${COMP_WORDS[COMP_CWORD-1]}

    case "$prev" in
        --help|-v|--version|--smart-group)
            return
            ;;

        --colour)
            mapfile -t COMPREPLY < <(compgen -W 'always automatic auto never' -- "$cur")
            return
            ;;

        --icons)
            mapfile -t COMPREPLY < <(compgen -W 'always automatic auto never' -- "$cur")
            return
            ;;

        -L|--level)
            mapfile -t COMPREPLY < <(compgen -W '{0..9}' -- "$cur")
            return
            ;;

        -s|--sort)
            mapfile -t COMPREPLY < <(compgen -W 'name filename Name Filename size filesize extension Extension date time modified changed accessed created type inode oldest newest age none --' -- "$cur")
            return
            ;;

        -t|--time)
            mapfile -t COMPREPLY < <(compgen -W 'modified changed accessed created --' -- "$cur")
            return
            ;;

        --time-style)
            mapfile -t COMPREPLY < <(compgen -W 'default iso long-iso full-iso relative +FORMAT --' -- "$cur")
            return
            ;;

        --color-scale)
            mapfile -t COMPREPLY < <(compgen -W 'all age size --' -- "$cur")
            return
            ;;

        --color-scale-mode)
            mapfile -t COMPREPLY < <(compgen -W 'fixed gradient --' -- "$cur")
            return
            ;;

        --absolute)
            mapfile -t COMPREPLY < <(compgen -W 'on follow off --' -- "$cur")
            return
            ;;
    esac

    case "$cur" in
        # _parse_help doesn't pick up short options when they are on the same line than long options
        --*)
            # colo[u]r isn't parsed correctly so we filter these options out and add them by hand
            parse_help=$(eza --help | grep -oE ' (--[[:alnum:]@-]+)' | tr -d ' ' | grep -v '\--colo')
            completions=$(echo '--color --colour --color-scale --colour-scale --color-scale-mode --colour-scale-mode' "$parse_help")
            mapfile -t COMPREPLY < <(compgen -W "$completions" -- "$cur")
            ;;

        -*)
            completions=$(eza --help | grep -oE ' (-[[:alnum:]@])' | tr -d ' ')
            mapfile -t COMPREPLY < <(compgen -W "$completions" -- "$cur")
            ;;

        *)
            _filedir
            ;;
    esac
} &&
complete -o filenames -o bashdefault -F _eza eza
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# Auto-use Node version from .nvmrc if available
if [ -f .nvmrc ]; then
  nvm use > /dev/null
fi


   # Add to your .bashrc file
   docker() {
     export MSYS_NO_PATHCONV=1
     "docker.exe" "$@"
   }
export PATH="$HOME/.cargo/bin:$PATH"
# Codex CLI Environment Variables
# export OPENAI_API_KEY="your-api-key-here"  # Uncomment and add your API key
# export GOOGLE_GENERATIVE_AI_API_KEY="your-gemini-api-key-here"  # For Gemini provider
# LM Studio API config for Codex
export OPENAI_API_KEY="1234"


export OLLAMA_BASE_URL="http://localhost:1234/v1"
alias codex='codex --provider ollama'