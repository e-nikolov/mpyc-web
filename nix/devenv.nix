{ pkgs, ... }: {
  # https://devenv.sh/basics/
  env.GREET = "devenv";
  env.PYTHON_KEYRING_BACKEND = "keyring.backends.null.Keyring";

  # https://devenv.sh/packages/
  packages = [
    pkgs.git
    pkgs.poetry
    pkgs.python311Packages.pip
    pkgs.just
    pkgs.yarn
    pkgs.bun
    pkgs.nodePackages_latest.pnpm
    # pkgs.mpyc-demo
    pkgs.pwnat
    pkgs.curl
    pkgs.jq
    pkgs.tailscale

    pkgs.colmena
    pkgs.pssh
    pkgs.natpunch
    pkgs.wireguard-tools
    pkgs.gole
    pkgs.go-stun
    pkgs.pion-stun
    # pkgs.bun
    pkgs.nodePackages.lerna
    pkgs.yarn2nix
    pkgs.python311Packages.gmpy2
    pkgs.python311Packages.numpy
    pkgs.twine
    pkgs.netlify-cli
    # pkgs.tailwindcss

    (pkgs.terraform.withPlugins (tp: [
      # (tp.digitalocean.overrideAttrs (final: old: {
      #   rev = "a88a19be189e01aec9a9152dc3543f9a6493cc80";
      #   hash = "123";
      #   vendorHash = "123";
      # }))
      tp.null
      tp.external
      tp.tailscale
      tp.random
      (tp.mkProvider {
        hash = "sha256-ZRMVmaNXQhJmo+pHjnkL0hk6pqYIblNrPfQe7mFg1f0=";
        owner = "digitalocean";
        repo = "terraform-provider-digitalocean";
        rev = "a88a19be189e01aec9a9152dc3543f9a6493cc81";
        version = "2.28.1";
        homepage =
          "https://registry.terraform.io/providers/digitalocean/digitalocean";
        vendorHash = null;
      })
      (tp.mkProvider {
        hash = "sha256-8wnmdIRAnUgJx3uGpopyk3Ayi6NVJ5f8vB+DvHXfBBI=";
        owner = "loafoe";
        repo = "terraform-provider-ssh";
        rev = "v2.4.0";
        homepage = "https://registry.terraform.io/providers/loafoe/ssh/";
        vendorHash = "sha256-MFp6KD9xXB6+B9XenGxxlR9Tueu4gDNeF1sMRvpIxGc=";
      })
    ]))
  ];

  # https://devenv.sh/scripts/
  scripts.hello.exec = "echo hello from $GREET";
  scripts.yi.exec =
    "yarn; yarn workspace @mpyc-web/core install; yarn workspace @mpyc-web/demo install";
  scripts.yb.exec = "yarn workspace @mpyc-web/$1 build";
  scripts.yd.exec = "yarn workspace @mpyc-web/$1 dev";
  scripts.yw.exec = ''
    ws=$1
    shift
    yarn workspace @mpyc-web/$ws $@
  '';
  # devenv.debug = true;
  dotenv.enable = true;
  enterShell = ''
    hello
    git --version
  '';

  # https://devenv.sh/languages/
  languages.nix.enable = true;

  languages.javascript.enable = true;
  languages.javascript.corepack.enable = true;
  # languages.javascript.npm.install.enable = true;
  languages.typescript.enable = true;
  languages.python.enable = true;
  languages.python.package = pkgs.python311;
  languages.python.poetry.enable = true;
  languages.python.poetry.activate.enable = true;
  languages.python.poetry.install.enable = true;
  languages.deno.enable = true;
  # languages.python.venv.enable = false;
  # languages.python.version = "3.11.5";

  devenv.flakesIntegration = true;

  # https://devenv.sh/pre-commit-hooks/
  # pre-commit.hooks.shellcheck.enable = true;

  # https://devenv.sh/processes/
  # processes.ping.exec = "ping example.com";

  # See full reference at https://devenv.sh/reference/options/
}
