{
  description = "Diffable plain-text JSON from *.knxproj files via xknxproject";

  inputs = {
    nullkomma.url = "https://flakehub.com/f/dataheld/nullkomma/0.1.*";
    nixpkgs.follows = "nullkomma/nixpkgs";
  };

  outputs =
    inputs:
    inputs.nullkomma.lib.mkFlake { inherit inputs; } {
      nullkomma = {
        gitignore = [ ".claude/" ];
        lint.markdown = {
          MD013 = false;
          MD033.allowed-elements = [ "img" ];
        };
        python.enable = true;
        quarto = {
          enable = true;
          brand.enable = true;
        };
        cloudflare = {
          enable = true;
          domain = "maxheld.de";
        };
      };

      partitions.dev = {
        extraInputsFlake = ./dev;
        module =
          { inputs, ... }:
          {
            nullkomma.brand = inputs.brand;
          };
      };

      perSystem =
        { config, pkgs, ... }:
        {
          process-compose.dev.settings.processes.update-readme = {
            description = "Regenerate the README diff example after test fixtures change";
            disabled = true;
            command = pkgs.writeShellApplication {
              name = "update-readme";
              runtimeInputs = [ config.nullkomma.python.interpreter ];
              # Without PC_NO_WATCH, a scratch copy would receive the snapshot.
              text = ''
                PC_NO_WATCH=1 ${config.process-compose.dev.settings.processes.python-test.command} \
                  tests/test_knxray.py::test_git_diff_textconv_snapshot --snapshot-update -q
                python scripts/update_readme.py
              '';
            };
          };
          nullkomma.python.test.packages = [ pkgs.git ];
          nullkomma.editor.vscode.settings."files.associations"."*.ambr" = "json";
        };
    };
}
