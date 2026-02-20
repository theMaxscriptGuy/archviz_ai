# GitHub Deploy Key (ArchViz AI)

This folder contains an SSH keypair created for pushing this repo to GitHub.

## Add the deploy key on GitHub

1. Go to your repo: https://github.com/theMaxscriptGuy/archviz_ai
2. Settings → **Deploy keys** → **Add deploy key**
3. Title: `openclaw-archviz-ai`
4. Key: paste the contents of `id_ed25519.pub`
5. Check: **Allow write access**

## Security

- Keep `id_ed25519` private. Do not commit it.
- This repo's `.gitignore` does not ignore `.ssh/` by default. Do NOT add `.ssh/id_ed25519` to git.
- Recommended: move the private key outside the repo folder and load it via ssh-agent.
